from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('', views.dashboard, name='dashboard'), path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'), path('logout/', views.logout_view, name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='core/password_reset.html', email_template_name='core/password_reset_email.txt'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),
    path('assets/', views.assets, name='assets'), path('assets/new/', views.asset_create, name='asset_create'), path('assets/export/', views.export_assets, name='export_assets'),
    path('assets/<int:pk>/status/', views.asset_status_update, name='asset_status_update'),
    path('bookings/', views.bookings, name='bookings'), path('maintenance/', views.maintenance, name='maintenance'), path('transfers/', views.transfers, name='transfers'),
    path('notifications/', views.notifications, name='notifications'), path('notifications/<int:pk>/open/', views.notification_open, name='notification_open'), path('approvals/', views.approvals, name='approvals'),
    path('directory/', views.directory, name='directory'), path('departments/', views.departments, name='departments'), path('reports/', views.reports, name='reports'), path('reports/export/', views.export_report, name='export_report')]
