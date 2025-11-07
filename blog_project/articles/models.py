from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import uuid


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
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
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
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
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
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'slug': self.slug})
    
    def is_published(self):
        return self.status == 'published'
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def get_average_rating(self):
        """Отримати середню оцінку статті"""
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.score for r in ratings) / ratings.count(), 1)
        return 0
    
    def get_ratings_count(self):
        """Отримати кількість оцінок"""
        return self.ratings.count()


class Rating(models.Model):
    """
    Модель оцінки статті
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Стаття'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Користувач'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Оцінка не може бути меншою за 1'),
            MaxValueValidator(5, message='Оцінка не може бути більшою за 5')
        ],
        verbose_name='Оцінка'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення'
    )
    
    class Meta:
        verbose_name = 'Оцінка'
        verbose_name_plural = 'Оцінки'
        unique_together = ['article', 'user']  # Один користувач - одна оцінка
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} оцінив "{self.article.title}" на {self.score}'
    
    def clean(self):
        """Валідація оцінки"""
        if self.score < 1 or self.score > 5:
            raise ValidationError('Оцінка повинна бути від 1 до 5')


class Subscription(models.Model):
    """
    Модель підписки на новини блогу
    """
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subscription',
        verbose_name='Користувач'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )
    unsubscribe_token = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name='Токен відписки'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата підписки'
    )
    
    class Meta:
        verbose_name = 'Підписка'
        verbose_name_plural = 'Підписки'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        """Автоматично генерувати токен для відписки"""
        if not self.unsubscribe_token:
            self.unsubscribe_token = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    def get_unsubscribe_url(self):
        """URL для відписки"""
        return reverse('articles:unsubscribe', kwargs={'token': self.unsubscribe_token})


class Media(models.Model):
    """
    Модель мультимедійних файлів (фото та відео)
    """
    FILE_TYPE_CHOICES = [
        ('image', 'Зображення'),
        ('video', 'Відео'),
    ]
    
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='media_files',
        verbose_name='Стаття'
    )
    file = models.FileField(
        upload_to='articles/media/%Y/%m/%d/',
        verbose_name='Файл'
    )
    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES,
        verbose_name='Тип файлу'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Назва'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Опис'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_media',
        verbose_name='Завантажив'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата завантаження'
    )
    
    class Meta:
        verbose_name = 'Медіафайл'
        verbose_name_plural = 'Медіафайли'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_file_type_display()} для "{self.article.title}"'
    
    def clean(self):
        """Валідація файлу"""
        if self.file:
            # Перевірка розміру файлу (максимум 10 МБ)
            if self.file.size > 10 * 1024 * 1024:
                raise ValidationError('Розмір файлу не повинен перевищувати 10 МБ')
            
            # Перевірка типу файлу
            allowed_extensions = {
                'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
                'video': ['.mp4', '.mov', '.avi', '.webm']
            }
            
            file_ext = self.file.name.lower().split('.')[-1]
            if self.file_type == 'image' and f'.{file_ext}' not in allowed_extensions['image']:
                raise ValidationError('Невірний формат зображення')
            elif self.file_type == 'video' and f'.{file_ext}' not in allowed_extensions['video']:
                raise ValidationError('Невірний формат відео')