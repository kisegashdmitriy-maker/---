from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings

login_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9]{6,}$',
    message='Логин должен содержать только латинские буквы и цифры, минимум 6 символов'
)

fio_validator = RegexValidator(
    regex=r'^[А-Яа-яёЁ\s\-]+$',
    message='ФИО должно содержать только русские буквы, пробелы и дефис'
)

phone_validator = RegexValidator(
    regex=r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$',
    message='Телефон должен быть в формате 8(XXX)XXX-XX-XX'
)


class User(AbstractUser):
    """Модель пользователя"""
    username = models.CharField(
        max_length=20,
        unique=True,
        validators=[login_validator],
        verbose_name='Логин'
    )
    full_name = models.CharField(
        max_length=150,
        validators=[fio_validator],
        verbose_name='ФИО'
    )
    telephone = models.CharField(
        max_length=16,
        validators=[phone_validator],
        verbose_name='Телефон'
    )
    email = models.EmailField(unique=True, verbose_name='Email')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Course(models.Model):
    """Модель курса"""
    title = models.CharField(max_length=200, verbose_name='Название курса')
    description = models.TextField(verbose_name='Описание')
    duration_weeks = models.PositiveIntegerField(verbose_name='Длительность (недели)')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    image = models.ImageField(upload_to='course_images/', verbose_name='Изображение', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class Application(models.Model):
    """Модель заявки на курс"""
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('training', 'Идет обучение'),
        ('completed', 'Обучение завершено'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Наличными'),
        ('transfer', 'Перевод по номеру телефона'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Пользователь'
    )
    course_name = models.CharField(max_length=200, verbose_name='Название курса')
    preferred_date = models.DateField(verbose_name='Желаемая дата начала')
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_CHOICES,
        verbose_name='Способ оплаты'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подачи')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return f"{self.user.username} - {self.course_name}"

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-applied_at']


class Review(models.Model):
    """Модель отзыва"""
    RATING_CHOICES = [
        (5, 'Отлично'),
        (4, 'Хорошо'),
        (3, 'Нормально'),
        (2, 'Плохо'),
        (1, 'Ужасно'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пользователь'
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Заявка'
    )
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='Оценка')
    comment = models.TextField(verbose_name='Отзыв', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')

    def __str__(self):
        return f"Отзыв от {self.user.username} - {self.get_rating_display()}"

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']