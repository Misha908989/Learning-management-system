from django.contrib import admin
from .models import Article, Category, Tag


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
    list_display = ['title', 'author', 'category', 'status', 'views_count', 'created_at']
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
    
    def save_model(self, request, obj, form, change):
        """Автоматично встановити автора при створенні"""
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)