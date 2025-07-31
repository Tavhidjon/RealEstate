from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.forms import AdminPasswordChangeForm, UserCreationForm, UserChangeForm
# Remove the problematic import
from unfold.decorators import display

from .models import AppUser, Company, Building, Floor, Flat, Chat, Message, BuildingImage

# Register the custom user model with Unfold styling
class AppUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_verified', 
                  'get_company', 'is_company_owner', 'date_joined', 'get_profile_picture')
    list_filter = ('is_verified', 'is_staff', 'is_active', 'company', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'is_company_owner')
    list_per_page = 25
    
    # Unfold specific customization
    empty_value_display = "—"
    search_help_text = "Search by email, username, or name"
    date_hierarchy = "date_joined"
    show_facets = True
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('phone_number', 'profile_picture', 'is_verified', 'company')}),
        ('Company Owner Information', {'fields': ('is_company_owner',), 'classes': ('collapse',)}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Company Owner Creation', {
            'classes': ('wide',),
            'fields': ('email', 'company', 'first_name', 'last_name', 'phone_number'),
        }),
    )
    
    def get_company(self, obj):
        if obj.company:
            return obj.company.name
        return '-'
    get_company.short_description = 'Company'
    
    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_picture.url)
        return format_html('<span style="color: #999;">No Image</span>')
    get_profile_picture.short_description = 'Profile Picture'
    
    # Add custom actions
    actions = ['make_company_owner', 'remove_company_owner']
    
    def make_company_owner(self, request, queryset):
        """Admin action to mark selected users as company owners by prompting for company selection"""
        if request.POST.get('company_id'):
            company_id = request.POST.get('company_id')
            try:
                company = Company.objects.get(id=company_id)
                count = 0
                for user in queryset:
                    user.company = company
                    user.save()
                    count += 1
                self.message_user(request, f"{count} users were successfully made company owners for {company.name}.")
                return
            except Company.DoesNotExist:
                self.message_user(request, "Selected company does not exist.", level='error')
        
        # Get all companies for the dropdown
        companies = Company.objects.all().order_by('name')
        
        return render(
            request,
            'admin/make_company_owner.html',
            {'users': queryset, 'companies': companies}
        )
    make_company_owner.short_description = "Assign selected users as company owners"
    
    def remove_company_owner(self, request, queryset):
        """Remove company owner status by removing company relationship"""
        count = 0
        for user in queryset:
            if user.company:
                user.company = None
                user.save()
                count += 1
        
        self.message_user(request, f"Company owner status removed from {count} users.")
    remove_company_owner.short_description = "Remove company owner status from selected users"
    
    # Add a custom view to the admin
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('user-dashboard/', self.admin_site.admin_view(self.user_dashboard_view), name='user-dashboard'),
        ]
        return custom_urls + urls
    
    def user_dashboard_view(self, request):
        # Get user statistics
        total_users = AppUser.objects.count()
        active_users = AppUser.objects.filter(is_active=True).count()
        verified_users = AppUser.objects.filter(is_verified=True).count()
        
        # Get new users in the last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        new_users = AppUser.objects.filter(date_joined__gte=week_ago).order_by('-date_joined')
        
        # Get users by company
        users_by_company = list(Company.objects.annotate(
            user_count=Count('representatives')
        ).values('name', 'user_count').order_by('-user_count'))
        
        # Get users with most chat activity
        active_chatters = AppUser.objects.annotate(
            chat_count=Count('chats__messages')
        ).order_by('-chat_count')[:10]
        
        context = {
            'title': 'User Dashboard',
            'total_users': total_users,
            'active_users': active_users,
            'verified_users': verified_users,
            'new_users': new_users,
            'users_by_company': users_by_company,
            'active_chatters': active_chatters,
        }
        
        return render(request, 'admin/user_dashboard.html', context)


# Company admin with improved interface using Unfold
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_building_count', 'get_representative_count', 'description')
    search_fields = ('name', 'description')
    list_filter = ('representatives__is_active',)
    
    # Unfold specific customization
    empty_value_display = "—"
    search_help_text = "Search by company name or description"
    show_facets = True
    
    def get_building_count(self, obj):
        count = obj.buildings.count()
        return format_html(
            '<span class="pill pill-success">{}</span>', 
            count
        ) if count > 0 else format_html('<span class="pill pill-light">0</span>')
    get_building_count.short_description = 'Buildings'
    
    def get_representative_count(self, obj):
        count = obj.representatives.count()
        return format_html(
            '<span class="pill pill-primary">{}</span>', 
            count
        ) if count > 0 else format_html('<span class="pill pill-light">0</span>')
    get_representative_count.short_description = 'Company Owners'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            building_count=Count('buildings', distinct=True),
            representative_count=Count('representatives', distinct=True)
        )
        return queryset

# Building admin with improved filtering and search using Unfold
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'get_company_name', 'floors_count', 'flats_count', 'get_image')
    list_filter = ('company', 'floors_count')
    search_fields = ('name', 'address', 'description', 'company__name')
    readonly_fields = ('created_at',) if hasattr(Building, 'created_at') else ()
    list_per_page = 25
    
    # Unfold specific customization
    empty_value_display = "—"
    search_help_text = "Search by building name, address, or company"
    show_facets = True
    actions_position = "both"
    
    def get_company_name(self, obj):
        if obj.company:
            return format_html('<span class="pill pill-info">{}</span>', obj.company.name)
        return format_html('<span class="pill pill-light">-</span>')
    get_company_name.short_description = 'Company'
    get_company_name.admin_order_field = 'company__name'
    
    def get_image(self, obj):
        """Display thumbnail of the first building image"""
        if hasattr(obj, 'image') and obj.image:
            return format_html('<img src="{}" width="80" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        
        # If it has a related BuildingImage
        images = BuildingImage.objects.filter(building=obj)
        if images.exists() and images.first().image:
            return format_html('<img src="{}" width="80" height="50" style="object-fit: cover; border-radius: 4px;" />', images.first().image.url)
            
        return format_html('<span class="pill pill-light">No Image</span>')
    get_image.short_description = 'Image'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # If user is a company owner, only show buildings for their company
        if request.user.is_authenticated and hasattr(request.user, 'company') and request.user.company and not request.user.is_staff:
            queryset = queryset.filter(company=request.user.company)
        return queryset

# Inline admin classes for related models
class BuildingImageInline(admin.TabularInline):
    model = BuildingImage
    extra = 1
    max_num = 10
    fields = ('image', 'caption', 'order')

class FloorInline(admin.TabularInline):
    model = Floor
    extra = 1
    fields = ('floor_number', 'plan_image')

# Update BuildingAdmin to use the inline
BuildingAdmin.inlines = [BuildingImageInline, FloorInline]

# Add Floor and Flat admin classes
class FloorAdmin(admin.ModelAdmin):
    list_display = ('floor_number', 'get_building_name', 'get_flats_count')
    list_filter = ('building',)
    search_fields = ('building__name', 'floor_number')
    
    def get_building_name(self, obj):
        return obj.building.name
    get_building_name.short_description = 'Building'
    
    def get_flats_count(self, obj):
        count = obj.flats.count()
        return format_html(
            '<span class="pill pill-success">{}</span>', 
            count
        ) if count > 0 else format_html('<span class="pill pill-light">0</span>')
    get_flats_count.short_description = 'Flats'

class FlatAdmin(admin.ModelAdmin):
    list_display = ('number', 'get_floor_number', 'get_building_name', 'area')
    list_filter = ('floor__building', 'floor')
    search_fields = ('number', 'floor__building__name')
    
    def get_floor_number(self, obj):
        return obj.floor.floor_number
    get_floor_number.short_description = 'Floor'
    
    def get_building_name(self, obj):
        return obj.floor.building.name
    get_building_name.short_description = 'Building'

# Chat and Message admin classes
class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender_type', 'content', 'timestamp', 'is_read')
    can_delete = False
    
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'get_message_count', 'get_last_message_time')
    inlines = [MessageInline]
    
    def get_participants(self, obj):
        return f"{obj.user.username} - {obj.company.name}"
    get_participants.short_description = 'Participants'
    
    def get_message_count(self, obj):
        return obj.messages.count()
    get_message_count.short_description = 'Messages'
    
    def get_last_message_time(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return last_msg.timestamp
        return '-'
    get_last_message_time.short_description = 'Last Activity'

# Building Image admin
class BuildingImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_building_name', 'get_image_preview', 'caption', 'order')
    list_filter = ('building',)
    search_fields = ('building__name', 'caption')
    
    def get_building_name(self, obj):
        return obj.building.name if obj.building else '-'
    get_building_name.short_description = 'Building'
    
    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="60" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return '-'
    get_image_preview.short_description = 'Image'

# Register models with Unfold
admin.site.register(AppUser, AppUserAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Floor, FloorAdmin)
admin.site.register(Flat, FlatAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(Message)
admin.site.register(BuildingImage, BuildingImageAdmin)
