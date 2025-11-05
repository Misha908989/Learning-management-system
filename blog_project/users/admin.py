from django.contrib import admin
from .models import Profile


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