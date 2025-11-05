from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    """
    Модель категорії статей
    """
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name='Назва'
    )
    slug = models.SlugField(
        max_length=100, 
        unique=True, 
        blank=True,
        verbose_name='URL'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Опис'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення'
    )
    
    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Автоматично генерувати slug з назви"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """URL категорії"""
        return reverse('articles:category', kwargs={'slug': self.slug})


class Tag(models.Model):
    """
    Модель тега для статей
    """
    name = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='Назва'
    )
    slug = models.SlugField(
        max_length=50, 
        unique=True, 
        blank=True,
        verbose_name='URL'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення'
    )
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Автоматично генерувати slug з назви"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """URL тега"""
        return reverse('articles:tag', kwargs={'slug': self.slug})


class Article(models.Model):
    """
    Модель статті блогу
    """
    STATUS_CHOICES = [
        ('draft', 'Чернетка'),
        ('published', 'Опублікована'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    slug = models.SlugField(
        max_length=200, 
        unique=True, 
        blank=True,
        verbose_name='URL'
    )
    content = models.TextField(
        verbose_name='Контент'
    )
    excerpt = models.TextField(
        max_length=500, 
        blank=True,
        verbose_name='Короткий опис'
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='articles',
        verbose_name='Автор'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='articles',
        verbose_name='Категорія'
    )
    tags = models.ManyToManyField(
        Tag, 
        blank=True,
        related_name='articles',
        verbose_name='Теги'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name='Статус'
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Кількість переглядів'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата оновлення'
    )
    published_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Дата публікації'
    )
    
    class Meta:
        verbose_name = 'Стаття'
        verbose_name_plural = 'Статті'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Автоматично генерувати slug з заголовка"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """URL статті"""
        return reverse('articles:detail', kwargs={'slug': self.slug})
    
    def is_published(self):
        """Перевірка чи стаття опублікована"""
        return self.status == 'published'
    
    def increment_views(self):
        """Збільшити кількість переглядів"""
        self.views_count += 1
        self.save(update_fields=['views_count'])