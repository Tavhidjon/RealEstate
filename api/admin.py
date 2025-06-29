from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AppUser, Company, Building, Floor, Flat

# Register the custom user model
class AppUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_verified')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('phone_number', 'profile_picture', 'is_verified')}),
    )


# Register models
admin.site.register(AppUser, AppUserAdmin)
admin.site.register(Company)
admin.site.register(Building)
admin.site.register(Floor)
admin.site.register(Flat)
