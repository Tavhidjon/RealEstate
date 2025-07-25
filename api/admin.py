from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import AppUser, Company, Building, Floor, Flat, Chat, Message, BuildingImage

# Register the custom user model
class AppUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_verified', 
                  'get_company', 'date_joined', 'get_profile_picture')
    list_filter = ('is_verified', 'is_staff', 'is_active', 'company', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('date_joined',)
    list_per_page = 25
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('phone_number', 'profile_picture', 'is_verified', 'company')}),
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


# Register models
admin.site.register(AppUser, AppUserAdmin)
admin.site.register(Company)
admin.site.register(Building)
admin.site.register(Floor)
admin.site.register(Flat)
