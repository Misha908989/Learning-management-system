from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import Article, Category, Tag, Rating, Subscription, Media


class MediaInline(admin.TabularInline):
    """
    Inline редагування медіафайлів на сторінці статті
    """
    model = Media
    extra = 1
    fields = ['file', 'file_type', 'title', 'description']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Розширена адмін-панель для категорій
    """
    list_display = ['name', 'slug', 'get_articles_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'get_articles_count']
    list_per_page = 25
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Статистика', {
            'fields': ('get_articles_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_articles_count(self, obj):
        """Кількість статей у категорії"""
        count = obj.articles.count()
        return format_html(
            '<span style="color: {};">{} статей</span>',
            'green' if count > 0 else 'gray',
            count
        )
    get_articles_count.short_description = 'Кількість статей'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Розширена адмін-панель для тегів
    """
    list_display = ['name', 'slug', 'get_articles_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'get_articles_count']
    list_per_page = 25
    
    def get_articles_count(self, obj):
        """Кількість статей з цим тегом"""
        count = obj.articles.count()
        return format_html(
            '<span style="color: {};">{} статей</span>',
            'blue' if count > 0 else 'gray',
            count
        )
    get_articles_count.short_description = 'Використовується в статтях'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Розширена адмін-панель для статей
    """
    list_display = [
        'title', 
        'author', 
        'category', 
        'get_status_badge',
        'views_count', 
        'get_rating_display',
        'get_comments_count',
        'created_at'
    ]
    list_filter = [
        'status', 
        'category', 
        'created_at', 
        'updated_at',
        'author',
        ('tags', admin.RelatedOnlyFieldListFilter),
    ]
    search_fields = ['title', 'content', 'excerpt', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'views_count',
        'get_rating_display',
        'get_comments_count'
    ]
    filter_horizontal = ['tags']
    date_hierarchy = 'created_at'
    list_per_page = 25
    inlines = [MediaInline]
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Контент', {
            'fields': ('excerpt', 'content')
        }),
        ('Теги', {
            'fields': ('tags',),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': (
                'views_count', 
                'get_rating_display',
                'get_comments_count',
                'created_at', 
                'updated_at', 
                'published_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_articles', 'unpublish_articles', 'reset_views']
    
    def get_status_badge(self, obj):
        """Відобразити статус як значок"""
        colors = {
            'draft': '#ffc107',
            'published': '#28a745'
        }
        labels = {
            'draft': 'Чернетка',
            'published': 'Опублікована'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            labels.get(obj.status, obj.status)
        )
    get_status_badge.short_description = 'Статус'
    get_status_badge.admin_order_field = 'status'
    
    def get_rating_display(self, obj):
        """Відобразити рейтинг"""
        avg = obj.get_average_rating()
        count = obj.get_ratings_count()
        if count > 0:
            stars = '⭐' * int(avg)
            return format_html(
                '{} <span style="color: #ffc107;">{}</span> ({} оцінок)',
                stars, avg, count
            )
        return format_html('<span style="color: gray;">Без оцінок</span>')
    get_rating_display.short_description = 'Рейтинг'
    
    def get_comments_count(self, obj):
        """Кількість коментарів"""
        count = obj.comments.count()
        approved = obj.comments.filter(is_approved=True).count()
        return format_html(
            '{} коментарів ({} схвалених)',
            count, approved
        )
    get_comments_count.short_description = 'Коментарі'
    
    def publish_articles(self, request, queryset):
        """Опублікувати статті"""
        from django.utils import timezone
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'{updated} статей опубліковано')
    publish_articles.short_description = 'Опублікувати вибрані статті'
    
    def unpublish_articles(self, request, queryset):
        """Зняти з публікації"""
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} статей знято з публікації')
    unpublish_articles.short_description = 'Зняти з публікації'
    
    def reset_views(self, request, queryset):
        """Скинути перегляди"""
        updated = queryset.update(views_count=0)
        self.message_user(request, f'Перегляди скинуто для {updated} статей')
    reset_views.short_description = 'Скинути кількість переглядів'
    
    def save_model(self, request, obj, form, change):
        """Автоматично встановити автора при створенні"""
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """
    Розширена адмін-панель для оцінок
    """
    list_display = ['user', 'article', 'get_score_stars', 'created_at']
    list_filter = ['score', 'created_at', 'article__category']
    search_fields = ['user__username', 'article__title']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('article', 'user', 'score')
        }),
        ('Дати', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_score_stars(self, obj):
        """Відобразити оцінку зірочками"""
        stars = '⭐' * obj.score
        empty_stars = '☆' * (5 - obj.score)
        return format_html(
            '<span style="color: #ffc107;">{}</span><span style="color: #ddd;">{}</span>',
            stars, empty_stars
        )
    get_score_stars.short_description = 'Оцінка'
    get_score_stars.admin_order_field = 'score'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Розширена адмін-панель для підписок
    """
    list_display = ['email', 'user', 'get_status_badge', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email', 'user__username']
    readonly_fields = ['created_at', 'unsubscribe_token']
    date_hierarchy = 'created_at'
    list_per_page = 25
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('email', 'user', 'is_active')
        }),
        ('Технічна інформація', {
            'fields': ('unsubscribe_token', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_badge(self, obj):
        """Відобразити статус підписки"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">Активна</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">Неактивна</span>'
        )
    get_status_badge.short_description = 'Статус'
    get_status_badge.admin_order_field = 'is_active'
    
    def activate_subscriptions(self, request, queryset):
        """Активувати підписки"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} підписок активовано')
    activate_subscriptions.short_description = 'Активувати вибрані підписки'
    
    def deactivate_subscriptions(self, request, queryset):
        """Деактивувати підписки"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} підписок деактивовано')
    deactivate_subscriptions.short_description = 'Деактивувати вибрані підписки'


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    """
    Розширена адмін-панель для медіафайлів
    """
    list_display = [
        'title', 
        'article', 
        'get_file_type_badge',
        'get_preview',
        'uploaded_by', 
        'created_at'
    ]
    list_filter = ['file_type', 'created_at', 'article__category']
    search_fields = ['title', 'article__title', 'description']
    readonly_fields = ['created_at', 'get_preview']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('article', 'file', 'file_type')
        }),
        ('Опис', {
            'fields': ('title', 'description')
        }),
        ('Попередній перегляд', {
            'fields': ('get_preview',),
            'classes': ('collapse',)
        }),
        ('Мета інформація', {
            'fields': ('uploaded_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_file_type_badge(self, obj):
        """Відобразити тип файлу"""
        colors = {
            'image': '#17a2b8',
            'video': '#6f42c1'
        }
        icons = {
            'image': '🖼️',
            'video': '🎥'
        }
        return format_html(
            '{} <span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            icons.get(obj.file_type, '📄'),
            colors.get(obj.file_type, '#6c757d'),
            obj.get_file_type_display()
        )
    get_file_type_badge.short_description = 'Тип'
    get_file_type_badge.admin_order_field = 'file_type'
    
    def get_preview(self, obj):
        """Попередній перегляд медіафайлу"""
        if obj.file_type == 'image':
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px;" />',
                obj.file.url
            )
        elif obj.file_type == 'video':
            return format_html(
                '<video width="300" controls><source src="{}" type="video/mp4"></video>',
                obj.file.url
            )
        return 'Немає попереднього перегляду'
    get_preview.short_description = 'Попередній перегляд'
    
    def save_model(self, request, obj, form, change):
        """Автоматично встановити користувача при завантаженні"""
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


admin.site.site_header = "Адміністрування блогу"
admin.site.site_title = "Адмін-панель"
admin.site.index_title = "Панель управління"