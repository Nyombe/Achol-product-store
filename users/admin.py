from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserPreferences
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Verification', {'fields': ('is_verified',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )




@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications_badge', 'preferred_language', 'theme')
    list_filter = ('email_notifications', 'preferred_language', 'theme')
    search_fields = ('user__email',)

    def email_notifications_badge(self, obj):
        if obj.email_notifications:
            return format_html('<span style="color: green;">✓ Enabled</span>')
        return format_html('<span style="color: gray;">✗ Disabled</span>')
    email_notifications_badge.short_description = 'Email'