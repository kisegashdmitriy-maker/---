from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Course, Application, Review


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'full_name', 'email', 'telephone', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'full_name', 'email', 'telephone')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('full_name', 'telephone', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'full_name', 'telephone', 'email', 'password1', 'password2'),
        }),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_weeks', 'price', 'image_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    fields = ('title', 'description', 'duration_weeks', 'price', 'image')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;">', obj.image.url)
        return '—'

    image_preview.short_description = 'Изображение'


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'user', 'course_name', 'preferred_date', 'payment_method', 'status', 'status_badge', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('user__username', 'user__full_name', 'course_name')
    ordering = ('-applied_at',)
    readonly_fields = ('applied_at', 'updated_at', 'user')
    list_editable = ('status',)

    fieldsets = (
        ('Заявка', {'fields': ('user', 'course_name', 'preferred_date', 'payment_method', 'status')}),
        ('Даты', {'fields': ('applied_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    actions = ['mark_as_training', 'mark_as_completed']

    def status_badge(self, obj):
        colors = {'new': 'primary', 'training': 'warning', 'completed': 'success'}
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = 'Статус'

    def mark_as_training(self, request, queryset):
        updated = queryset.update(status='training')
        self.message_user(request, f'{updated} заявок переведено в "Идет обучение"')

    mark_as_training.short_description = 'Перевести в "Идет обучение"'

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} заявок переведено в "Обучение завершено"')

    mark_as_completed.short_description = 'Перевести в "Обучение завершено"'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'application', 'rating_stars', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'comment')

    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span class="text-warning">{}</span>', stars)

    rating_stars.short_description = 'Оценка'