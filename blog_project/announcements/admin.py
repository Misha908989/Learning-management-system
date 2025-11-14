from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """
    Розширена адмін-панель для оголошень
    """
    list_display = [
        'title',
        'get_type_badge',
        'get_status_indicators',
        'created_by',
        'get_expiry_info',
        'created_at'
    ]
    list_filter = [
        'type',
        'is_active',
        'is_pinned',
        'created_at',
        'expires_at'
    ]
    search_fields = ['title', 'content', 'created_by__username']
    readonly_fields = ['created_at', 'created_by', 'get_preview']
    date_hierarchy = 'created_at'
    list_per_page = 25
    actions = [
        'activate_announcements',
        'deactivate_announcements',
        'pin_announcements',
        'unpin_announcements',
        'extend_expiry'
    ]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'content', 'type')
        }),
        ('Налаштування відображення', {
            'fields': ('is_active', 'is_pinned', 'expires_at'),
            'description': 'Керуйте видимістю та важливістю оголошення'
        }),
        ('Попередній перегляд', {
            'fields': ('get_preview',),
            'classes': ('collapse',)
        }),
        ('Мета інформація', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_type_badge(self, obj):
        """Відобразити тип оголошення"""
        colors = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'success': '#28a745',
            'danger': '#dc3545'
        }
        icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'success': '✅',
            'danger': '🚨'
        }
        return format_html(
            '{} <span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            icons.get(obj.type, 'ℹ️'),
            colors.get(obj.type, '#6c757d'),
            obj.get_type_display()
        )
    get_type_badge.short_description = 'Тип'
    get_type_badge.admin_order_field = 'type'
    
    def get_status_indicators(self, obj):
        """Індикатори статусу"""
        indicators = []
        
        if obj.is_active:
            indicators.append('<span style="background-color: #28a745; color: white; padding: 2px 8px; border-radius: 3px; margin: 2px;">Активне</span>')
        else:
            indicators.append('<span style="background-color: #dc3545; color: white; padding: 2px 8px; border-radius: 3px; margin: 2px;">Неактивне</span>')
        
        if obj.is_pinned:
            indicators.append('<span style="background-color: #ffc107; color: black; padding: 2px 8px; border-radius: 3px; margin: 2px;" Закріплено</span>')
        
        if obj.is_expired():
            indicators.append('<span style="background-color: #6c757d; color: white; padding: 2px 8px; border-radius: 3px; margin: 2px;">Прострочено</span>')
        
        return format_html(''.join(indicators))
    get_status_indicators.short_description = 'Статус'
    
    def get_expiry_info(self, obj):
        """Інформація про термін дії"""
        if not obj.expires_at:
            return format_html('<span style="color: #28a745;">Без терміну</span>')
        
        if obj.is_expired():
            return format_html(
                '<span style="color: #dc3545;">Закінчилось {}</span>',
                obj.expires_at.strftime('%d.%m.%Y %H:%M')
            )
        
        days_left = (obj.expires_at - timezone.now()).days
        if days_left <= 3:
            color = '#dc3545'
        elif days_left <= 7:
            color = '#ffc107'
        else:
            color = '#28a745'
        
        return format_html(
            '<span style="color: {};">Закінчується: {} (ще {} днів)</span>',
            color,
            obj.expires_at.strftime('%d.%m.%Y %H:%M'),
            days_left
        )
    get_expiry_info.short_description = 'Термін дії'
    get_expiry_info.admin_order_field = 'expires_at'
    
    def get_preview(self, obj):
        """Попередній перегляд оголошення"""
        return format_html(
            '''
            <div style="border: 2px solid {}; padding: 15px; border-radius: 5px; background-color: #f8f9fa;">
                <h3 style="margin-top: 0;">{}</h3>
                <p>{}</p>
                <small style="color: #6c757d;">Створено: {} | Автор: {}</small>
            </div>
            ''',
            {'info': '#17a2b8', 'warning': '#ffc107', 'success': '#28a745', 'danger': '#dc3545'}.get(obj.type, '#6c757d'),
            obj.title,
            obj.content,
            obj.created_at.strftime('%d.%m.%Y %H:%M'),
            obj.created_by.username if obj.created_by else 'Невідомо'
        )
    get_preview.short_description = 'Попередній перегляд'
    
    def save_model(self, request, obj, form, change):
        """Автоматично встановити автора при створенні"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def activate_announcements(self, request, queryset):
        """Активувати оголошення"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} оголошень активовано', level='success')
    activate_announcements.short_description = 'Активувати вибрані'
    
    def deactivate_announcements(self, request, queryset):
        """Деактивувати оголошення"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} оголошень деактивовано', level='warning')
    deactivate_announcements.short_description = 'Деактивувати вибрані'
    
    def pin_announcements(self, request, queryset):
        """Закріпити оголошення"""
        updated = queryset.update(is_pinned=True)
        self.message_user(request, f'{updated} оголошень закріплено', level='success')
    pin_announcements.short_description = 'Закріпити вибрані'
    
    def unpin_announcements(self, request, queryset):
        """Відкріпити оголошення"""
        updated = queryset.update(is_pinned=False)
        self.message_user(request, f'{updated} оголошень відкріплено', level='info')
    unpin_announcements.short_description = 'Відкріпити вибрані'
    
    def extend_expiry(self, request, queryset):
        """Продовжити термін дії на 7 днів"""
        from datetime import timedelta
        for announcement in queryset:
            if announcement.expires_at:
                announcement.expires_at = announcement.expires_at + timedelta(days=7)
            else:
                announcement.expires_at = timezone.now() + timedelta(days=7)
            announcement.save()
        self.message_user(
            request,
            f'Термін дії продовжено на 7 днів для {queryset.count()} оголошень',
            level='success'
        )
    extend_expiry.short_description = 'Продовжити термін на 7 днів'