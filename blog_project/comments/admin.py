from django.contrib import admin
from django.utils.html import format_html
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Розширена адмін-панель для коментарів
    """
    list_display = [
        'get_user_info',
        'article',
        'content_preview',
        'get_status_badge',
        'get_reply_info',
        'created_at'
    ]
    list_filter = [
        'is_approved',
        'created_at',
        'article__category',
        'article__author'
    ]
    search_fields = [
        'content',
        'user__username',
        'article__title'
    ]
    readonly_fields = ['created_at', 'updated_at', 'get_article_link', 'get_parent_comment']
    date_hierarchy = 'created_at'
    list_per_page = 25
    actions = ['approve_comments', 'disapprove_comments', 'delete_spam']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('article', 'user', 'parent')
        }),
        ('Контент', {
            'fields': ('content', 'is_approved')
        }),
        ('Посилання', {
            'fields': ('get_article_link', 'get_parent_comment'),
            'classes': ('collapse',)
        }),
        ('Дати', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_info(self, obj):
        """Інформація про користувача"""
        role_colors = {
            'admin': 'danger',
            'author': 'primary',
            'user': 'secondary'
        }
        role = obj.user.profile.role
        return format_html(
            '{} <span class="badge badge-{}">role {}</span>',
            obj.user.username,
            role_colors.get(role, 'secondary'),
            role
        )
    get_user_info.short_description = 'Користувач'
    get_user_info.admin_order_field = 'user__username'
    
    def content_preview(self, obj):
        """Попередній перегляд контенту"""
        max_length = 60
        if len(obj.content) > max_length:
            return obj.content[:max_length] + '...'
        return obj.content
    content_preview.short_description = 'Контент'
    
    def get_status_badge(self, obj):
        """Відобразити статус схвалення"""
        if obj.is_approved:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Схвалено</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 3px 10px; border-radius: 3px;">⏳ На модерації</span>'
        )
    get_status_badge.short_description = 'Статус'
    get_status_badge.admin_order_field = 'is_approved'
    
    def get_reply_info(self, obj):
        """Інформація про відповіді"""
        if obj.parent:
            return format_html(
                '<span style="color: #6c757d;">↳ Відповідь на #{}</span>',
                obj.parent.id
            )
        replies_count = obj.replies.count()
        if replies_count > 0:
            return format_html(
                '<span style="color: #007bff;">{} відповідей</span>',
                replies_count
            )
        return '-'
    get_reply_info.short_description = 'Відповіді'
    
    def get_article_link(self, obj):
        """Посилання на статтю"""
        if obj.article:
            return format_html(
                '<a href="/admin/articles/article/{}/change/">{}</a>',
                obj.article.id,
                obj.article.title
            )
        return '-'
    get_article_link.short_description = 'Стаття'
    
    def get_parent_comment(self, obj):
        """Батьківський коментар"""
        if obj.parent:
            return format_html(
                '<a href="/admin/comments/comment/{}/change/">Коментар #{}: {}</a>',
                obj.parent.id,
                obj.parent.id,
                obj.parent.content[:50]
            )
        return 'Немає (основний коментар)'
    get_parent_comment.short_description = 'Батьківський коментар'
    
    def approve_comments(self, request, queryset):
        """Схвалити коментарі"""
        updated = queryset.update(is_approved=True)
        self.message_user(
            request,
            f'{updated} коментарів схвалено',
            level='success'
        )
    approve_comments.short_description = '✓ Схвалити вибрані коментарі'
    
    def disapprove_comments(self, request, queryset):
        """Відхилити коментарі"""
        updated = queryset.update(is_approved=False)
        self.message_user(
            request,
            f'{updated} коментарів відхилено',
            level='warning'
        )
    disapprove_comments.short_description = '✗ Відхилити вибрані коментарі'
    
    def delete_spam(self, request, queryset):
        """Видалити спам"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} спам-коментарів видалено', level='success')
    delete_spam.short_description = 'Видалити як спам'