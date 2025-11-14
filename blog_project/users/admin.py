from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    """
    Inline редагування профілю на сторінці користувача
    """
    model = Profile
    can_delete = False
    verbose_name = 'Профіль'
    verbose_name_plural = 'Профіль'
    fields = ['bio', 'avatar', 'role']


class UserAdmin(BaseUserAdmin):
    """
    Розширена адмін-панель для користувачів
    """
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'profile__role']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    
    def get_role(self, obj):
        """Отримати роль користувача"""
        return obj.profile.role
    get_role.short_description = 'Роль'
    get_role.admin_order_field = 'profile__role'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Налаштування адмін-панелі для профілів
    """
    list_display = ['user', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('user', 'role')
        }),
        ('Додаткова інформація', {
            'fields': ('bio', 'avatar')
        }),
        ('Дати', {
            'fields': ('created_at',)
        }),
    )
    
    def get_username(self, obj):
        """Отримати ім'я користувача"""
        return obj.user.username
    get_username.short_description = "Ім'я користувача"
    get_username.admin_order_field = 'user__username'
    
    def get_email(self, obj):
        """Отримати email користувача"""
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    actions = ['make_author', 'make_user', 'make_admin']
    
    def make_author(self, request, queryset):
        """Зробити авторами"""
        updated = queryset.update(role='author')
        self.message_user(request, f'{updated} користувачів стали авторами')
    make_author.short_description = 'Зробити авторами'
    
    def make_user(self, request, queryset):
        """Зробити звичайними користувачами"""
        updated = queryset.update(role='user')
        self.message_user(request, f'{updated} користувачів стали звичайними користувачами')
    make_user.short_description = 'Зробити користувачами'
    
    def make_admin(self, request, queryset):
        """Зробити адміністраторами"""
        updated = queryset.update(role='admin')
        self.message_user(request, f'{updated} користувачів стали адміністраторами')
    make_admin.short_description = 'Зробити адміністраторами'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)