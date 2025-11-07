from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Налаштування адмін-панелі для коментарів
    """
    list_display = ['user', 'article', 'content_preview', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at', 'article']
    search_fields = ['content', 'user__username', 'article__title']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_comments', 'disapprove_comments']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('article', 'user', 'parent')
        }),
        ('Контент', {
            'fields': ('content', 'is_approved')
        }),
        ('Дати', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def content_preview(self, obj):
        """Попередній перегляд контенту"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Контент'
    
    def approve_comments(self, request, queryset):
        """Схвалити коментарі"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} коментарів схвалено')
    approve_comments.short_description = 'Схвалити вибрані коментарі'
    
    def disapprove_comments(self, request, queryset):
        """Відхилити коментарі"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} коментарів відхилено')
    disapprove_comments.short_description = 'Відхилити вибрані коментарі'