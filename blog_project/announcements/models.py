from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


class Announcement(models.Model):
    """
    Модель оголошення (повідомлення для всіх користувачів)
    """
    TYPE_CHOICES = [
        ('info', 'Інформація'),
        ('warning', 'Попередження'),
        ('success', 'Успіх'),
        ('danger', 'Важливе'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    content = models.TextField(
        verbose_name='Текст оголошення'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='info',
        verbose_name='Тип'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активне'
    )
    is_pinned = models.BooleanField(
        default=False,
        verbose_name='Закріплене'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='announcements',
        verbose_name='Створив'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата закінчення'
    )
    
    class Meta:
        verbose_name = 'Оголошення'
        verbose_name_plural = 'Оголошення'
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'expires_at']),
            models.Index(fields=['is_pinned', 'created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def clean(self):
        """Валідація оголошення"""
        # Перевірка дати закінчення
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError('Дата закінчення не може бути в минулому')
        
        # Перевірка довжини заголовка
        if len(self.title.strip()) < 5:
            raise ValidationError('Заголовок повинен містити мінімум 5 символів')
        
        # Перевірка контенту
        if len(self.content.strip()) < 10:
            raise ValidationError('Текст оголошення повинен містити мінімум 10 символів')
    
    def is_expired(self):
        """Перевірка чи оголошення прострочене"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def is_visible(self):
        """Перевірка чи оголошення видиме"""
        return self.is_active and not self.is_expired()
    
    def get_type_badge_class(self):
        """Отримати CSS клас для значка типу"""
        badge_classes = {
            'info': 'badge-info',
            'warning': 'badge-warning',
            'success': 'badge-success',
            'danger': 'badge-danger',
        }
        return badge_classes.get(self.type, 'badge-secondary')
    
    def save(self, *args, **kwargs):
        """Автоматично деактивувати прострочені оголошення"""
        if self.is_expired():
            self.is_active = False
        super().save(*args, **kwargs)
    
    @staticmethod
    def get_active_announcements():
        """Отримати всі активні оголошення"""
        return Announcement.objects.filter(
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        )
    
    @staticmethod
    def get_pinned_announcements():
        """Отримати закріплені оголошення"""
        return Announcement.get_active_announcements().filter(is_pinned=True)