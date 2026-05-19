from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ApplicationForm, ReviewForm
from .models import Course, Application, Review


def home(request):
    """Главная страница"""
    courses = Course.objects.all()

    paginator = Paginator(courses, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'courses': page_obj.object_list,
    }
    return render(request, 'uchis_rf/home.html', context)


def register_view(request):
    """Страница регистрации"""
    if request.user.is_authenticated:
        return redirect('uchis_rf:profile')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрированы!')
            return redirect('uchis_rf:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CustomUserCreationForm()

    return render(request, 'uchis_rf/register.html', {'form': form})


def login_view(request):
    """Страница входа"""
    if request.user.is_authenticated:
        return redirect('uchis_rf:profile')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('uchis_rf:profile')
            else:
                messages.error(request, 'Неверный логин или пароль')
        else:
            messages.error(request, 'Неверный логин или пароль')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'uchis_rf/login.html', {'form': form})


@login_required
def logout_view(request):
    """Выход"""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('uchis_rf:home')


@login_required
def profile(request):
    """Личный кабинет - просмотр заявок"""
    user_applications = Application.objects.filter(user=request.user).order_by('-applied_at')

    total = user_applications.count()
    new_count = user_applications.filter(status='new').count()
    training = user_applications.filter(status='training').count()
    completed = user_applications.filter(status='completed').count()

    paginator = Paginator(user_applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total': total,
        'new_count': new_count,
        'training': training,
        'completed': completed,
    }
    return render(request, 'uchis_rf/profile.html', context)


@login_required
def apply_for_course(request):
    """Формирование заявки"""
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.course_name = form.cleaned_data['course_name']
            application.save()
            messages.success(request, 'Ваша заявка отправлена на рассмотрение администратору!')
            return redirect('uchis_rf:profile')
        else:
            messages.error(request, 'Пожалуйста, заполните все поля корректно.')
    else:
        form = ApplicationForm()

    return render(request, 'uchis_rf/apply.html', {'form': form})


@login_required
def add_review(request, application_id):
    """Добавить отзыв к заявке"""
    application = Application.objects.get(id=application_id, user=request.user)

    # Проверить, что обучение завершено
    if application.status != 'completed':
        messages.error(request, 'Отзыв можно оставить только после завершения обучения')
        return redirect('uchis_rf:profile')

    # Проверить, что отзыва ещё нет
    if hasattr(application, 'reviews') and application.reviews.exists():
        messages.error(request, 'Вы уже оставили отзыв на эту заявку')
        return redirect('uchis_rf:profile')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.application = application
            review.save()
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect('uchis_rf:profile')
    else:
        form = ReviewForm()

    return render(request, 'uchis_rf/review.html', {
        'form': form,
        'application': application
    })


def courses_list(request):
    """Список курсов"""
    courses = Course.objects.all()
    search_query = request.GET.get('q')

    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'uchis_rf/courses.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })


def course_detail(request, course_id):
    """Детали курса"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        messages.error(request, 'Курс не найден')
        return redirect('uchis_rf:home')

    return render(request, 'uchis_rf/course_detail.html', {'course': course})


@login_required
def admin_panel(request):
    """Админ-панель для управления заявками"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к админ-панели')
        return redirect('uchis_rf:profile')

    applications = Application.objects.select_related('user').order_by('-applied_at')

    status_filter = request.GET.get('status')
    if status_filter and status_filter in ['new', 'training', 'completed']:
        applications = applications.filter(status=status_filter)

    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        new_status = request.POST.get('status')
        if app_id and new_status:
            try:
                app = Application.objects.get(id=app_id)
                app.status = new_status
                app.save()
                messages.success(request, f'Статус заявки #{app_id} обновлён')
            except Application.DoesNotExist:
                messages.error(request, 'Заявка не найдена')

    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'uchis_rf/admin_panel.html', context)