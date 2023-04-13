from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .forms import UserAdminCreationForm, UserAdminChangeForm

admin.site.unregister(Group)
User = get_user_model()

class UserAdmin(BaseUserAdmin):
    add_form = UserAdminCreationForm

    list_display = ('first_name', 'last_name', 'phone_number', 'email',  'is_staff')
    ordering = ('phone_number',)
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'patronymic', 'phone_number', 'email', 'is_driver')
        }),
        ("System info", {
            'classes': ('collapse',),
            'fields': ('is_staff', 'is_superuser', 'is_active')
        })
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number',
                'first_name',
                'last_name',
                'patronymic',
                'email',
                'secret_word',
                'is_driver',
                'password',
                'password_2'
            ),
        }),
    )


admin.site.register(User, UserAdmin)

