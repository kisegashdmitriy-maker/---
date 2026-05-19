from django.urls import path
from . import views

app_name = 'uchis_rf'

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),

    # Курсы
    path('courses/', views.courses_list, name='courses'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),

    # Авторизация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Личный кабинет
    path('profile/', views.profile, name='profile'),
    path('apply/', views.apply_for_course, name='apply'),
    path('review/<int:application_id>/', views.add_review, name='add_review'),

    # Админ-панель
    path('admin-panel/', views.admin_panel, name='admin_panel'),
]