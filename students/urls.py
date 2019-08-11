from django.urls import path
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'student'
urlpatterns = [
    path('regist/', views.regist, name='regist'),
    path('login/', views.login, name='login'),
    path('logout/<student_id>/', views.logout, name='logout'),
    path('index/<student_id>/', views.index, name='index'),
    path('superuser',views.superuser, name='superuser'),
    path('submit/<student_id>', views.submit, name='submit'),
    path('worktime/export_excel',views.export_excel, name='export_excel'),
    path('', views.login, name='login'),
]
