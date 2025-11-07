from django.contrib import admin
from .models import Article, Category, Tag, Rating, Subscription, Media


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Налаштування адмін-панелі для категорій
    """
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Налаштування адмін-панелі для тегів
    """
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Налаштування адмін-панелі для статей
    """
    list_display = ['title', 'author', 'category', 'status', 'views_count', 'get_rating', 'created_at']
    list_filter = ['status', 'category', 'created_at', 'author']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'views_count']
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Контент', {
            'fields': ('excerpt', 'content')
        }),
        ('Теги', {
            'fields': ('tags',)
        }),
        ('Статистика', {
            'fields': ('views_count', 'created_at', 'updated_at', 'published_at')
        }),
    )
    
    def get_rating(self, obj):
        """Показати середню оцінку"""
        avg = obj.get_average_rating()
        count = obj.get_ratings_count()
        return f'{avg} ⭐ ({count})'
    get_rating.short_description = 'Рейтинг'
    
    def save_model(self, request, obj, form, change):
        """Автоматично встановити автора при створенні"""
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """
    Налаштування адмін-панелі для оцінок
    """
    list_display = ['user', 'article', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    search_fields = ['user__username', 'article__title']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('article', 'user', 'score')
        }),
        ('Дати', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Налаштування адмін-панелі для підписок
    """
    list_display = ['email', 'user', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email', 'user__username']
    readonly_fields = ['created_at', 'unsubscribe_token']
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('email', 'user', 'is_active')
        }),
        ('Технічна інформація', {
            'fields': ('unsubscribe_token', 'created_at')
        }),
    )
    
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
    Налаштування адмін-панелі для медіафайлів
    """
    list_display = ['title', 'article', 'file_type', 'uploaded_by', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['title', 'article__title', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('article', 'file', 'file_type')
        }),
        ('Опис', {
            'fields': ('title', 'description')
        }),
        ('Мета інформація', {
            'fields': ('uploaded_by', 'created_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Автоматично встановити користувача при завантаженні"""
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)