from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """
    Налаштування адмін-панелі для оголошень
    """
    list_display = ['title', 'type', 'is_active', 'is_pinned', 'created_by', 'expires_at', 'created_at']
    list_filter = ['type', 'is_active', 'is_pinned', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'created_by']
    actions = ['activate_announcements', 'deactivate_announcements', 'pin_announcements']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'content', 'type')
        }),
        ('Налаштування', {
            'fields': ('is_active', 'is_pinned', 'expires_at')
        }),
        ('Мета інформація', {
            'fields': ('created_by', 'created_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Автоматично встановити автора при створенні"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def activate_announcements(self, request, queryset):
        """Активувати оголошення"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} оголошень активовано')
    activate_announcements.short_description = 'Активувати вибрані оголошення'
    
    def deactivate_announcements(self, request, queryset):
        """Деактивувати оголошення"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} оголошень деактивовано')
    deactivate_announcements.short_description = 'Деактивувати вибрані оголошення'
    
    def pin_announcements(self, request, queryset):
        """Закріпити оголошення"""
        updated = queryset.update(is_pinned=True)
        self.message_user(request, f'{updated} оголошень закріплено')
    pin_announcements.short_description = 'Закріпити вибрані оголошення'