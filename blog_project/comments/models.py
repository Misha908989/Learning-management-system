from django.db import models
from django.contrib.auth.models import User
from articles.models import Article
from django.core.exceptions import ValidationError


class Comment(models.Model):
    """
    Модель коментаря до статті
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Стаття'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Користувач'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Батьківський коментар'
    )
    content = models.TextField(
        max_length=1000,
        verbose_name='Текст коментаря'
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name='Схвалено'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата оновлення'
    )
    
    class Meta:
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f'Коментар від {self.user.username} до "{self.article.title}"'
    
    def clean(self):
        """Валідація коментаря"""
        # Перевірка довжини контенту
        if len(self.content.strip()) < 3:
            raise ValidationError('Коментар повинен містити мінімум 3 символи')
        
        # Перевірка на порожній контент
        if not self.content.strip():
            raise ValidationError('Коментар не може бути порожнім')
        
        # Перевірка батьківського коментаря
        if self.parent:
            # Батьківський коментар має належати тій самій статті
            if self.parent.article != self.article:
                raise ValidationError('Батьківський коментар має належати тій самій статті')
            
            # Заборона вкладеності більше 2 рівнів
            if self.parent.parent is not None:
                raise ValidationError('Максимальна глибина вкладеності коментарів - 2 рівні')
    
    def get_replies(self):
        """Отримати відповіді на коментар"""
        return self.replies.filter(is_approved=True)
    
    def is_reply(self):
        """Перевірка чи є коментар відповіддю"""
        return self.parent is not None
    
    def can_be_moderated_by(self, user):
        """Перевірка чи користувач може модерувати коментар"""
        # Адміністратори можуть модерувати всі коментарі
        if user.is_staff or user.profile.is_admin():
            return True
        # Автори можуть модерувати коментарі до своїх статей
        if self.article.author == user and user.profile.is_author():
            return True
        return False