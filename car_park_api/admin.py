from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import Car, Order


admin.site.unregister(Group)
User = get_user_model()


class OrderInline(admin.TabularInline):
    model = Order
    classes = ['collapse', ]
    extra = 1
    show_change_link = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = User.objects.filter(is_driver=False)
        if db_field.name == "driver":
            kwargs["queryset"] = User.objects.filter(is_driver=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CarAdmin(admin.ModelAdmin):
    inlines = (OrderInline,)


admin.site.register(Car, CarAdmin)


class OrderAdmin(admin.ModelAdmin):
    model = Order

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = User.objects.filter(is_driver=False)
        if db_field.name == "driver":
            kwargs["queryset"] = User.objects.filter(is_driver=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Order, OrderAdmin)


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

