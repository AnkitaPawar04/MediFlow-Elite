from django.urls import path
from . import views

app_name = 'admin_management'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('user/<int:user_id>/<str:action>/', views.user_actions, name='user_action'),
    path('manage-doctors/', views.manage_doctors, name='manage_doctors'),
    path('doctor/<int:approval_id>/<str:action>/', views.doctor_actions, name='doctor_action'),
    path('system-logs/', views.system_logs, name='system_logs'),
    
    # Departments
    path('departments/', views.departments, name='departments'),
    path('department/<int:dept_id>/', views.department_detail, name='department_detail'),
    path('department/<int:dept_id>/<str:action>/', views.department_actions, name='department_action'),
    
    # Specializations
    path('specializations/', views.specializations, name='specializations'),
    path('specialization/<int:spec_id>/', views.specialization_detail, name='specialization_detail'),
    path('specialization/<int:spec_id>/<str:action>/', views.specialization_actions, name='specialization_action'),
    
    # Transactions & Profile
    path('transactions/', views.transactions, name='transactions'),
    path('profile/', views.edit_profile, name='edit_profile'),
]
