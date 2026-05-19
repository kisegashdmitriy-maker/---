from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinLengthValidator
from django.core import validators
from .models import Course, Application, Review

User = get_user_model()

# Валидатор для логина (латиница + цифры, мин 6 символов)
login_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9]{6,}$',
    message='Логин должен содержать только латинские буквы и цифры, минимум 6 символов'
)

# Валидатор для ФИО (кириллица и пробелы)
fio_validator = RegexValidator(
    regex=r'^[А-Яа-яёЁ\s\-]+$',
    message='ФИО должно содержать только русские буквы, пробелы и дефис'
)

# Валидатор для телефона (формат 8(XXX)XXX-XX-XX)
phone_validator = RegexValidator(
    regex=r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$',
    message='Телефон должен быть в формате 8(XXX)XXX-XX-XX'
)


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    full_name = forms.CharField(
        max_length=150,
        required=True,
        validators=[fio_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Сафин Райхан Булатович',
            'data-mask': '8(999)999-99-99'
        }),
        label='ФИО *'
    )
    telephone = forms.CharField(
        max_length=16,
        required=True,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '8(123)456-78-90',
            'data-mask': '8(999)999-99-99'
        }),
        label='Телефон *'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'example@mail.ru'
        }),
        label='Email *'
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'full_name', 'telephone', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs.update({
                'class': 'form-control form-control-lg'
            })
        self.fields['username'].widget.attrs['placeholder'] = 'user123'
        self.fields['password1'].widget.attrs['placeholder'] = 'Минимум 8 символов'
        self.fields['password2'].widget.attrs['placeholder'] = 'Повторите пароль'


        self.fields['username'].validators.append(login_validator)

        self.fields['password1'].validators.append(MinLengthValidator(8))


class CustomAuthenticationForm(AuthenticationForm):
    """Форма входа"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ваш логин'
        }),
        label='Логин'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ваш пароль'
        }),
        label='Пароль'
    )


class ApplicationForm(forms.ModelForm):
    """Форма подачи заявки"""
    COURSE_CHOICES = [
        ('Повышение квалификации', 'Повышение квалификации'),
        ('Курс переподготовки', 'Курс переподготовки'),
        ('Курс по охране труда', 'Курс по охране труда'),
    ]

    course_name = forms.ChoiceField(
        choices=COURSE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg'
        }),
        label='Наименование курса *'
    )

    PAYMENT_CHOICES = [
        ('cash', 'Наличными'),
        ('transfer', 'Перевод по номеру телефона'),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg'
        }),
        label='Способ оплаты *'
    )

    class Meta:
        model = Application
        fields = ['preferred_date', 'payment_method']
        widgets = {
            'preferred_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'type': 'date'
                },
                format='%Y-%m-%d'
            ),
        }
        labels = {
            'preferred_date': 'Желаемая дата начала обучения *',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class ReviewForm(forms.ModelForm):
    """Форма отзыва"""

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-select form-select-lg'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Напишите ваш отзыв о качестве образовательных услуг...'
            }),
        }
        labels = {
            'rating': 'Оценка *',
            'comment': 'Отзыв',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].choices = [
            (5, '★★★★★ - Отлично'),
            (4, '★★★★☆ - Хорошо'),
            (3, '★★★☆☆ - Нормально'),
            (2, '★★☆☆☆ - Плохо'),
            (1, '★☆☆☆☆ - Ужасно'),
        ]