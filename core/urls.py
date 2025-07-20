# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'), # Added logout

    # Campaign Manager URLs
    path('campaigns/create/', views.create_campaign, name='create_campaign'),
    path('campaigns/my/', views.my_campaigns, name='my_campaigns'),
    path('campaigns/<int:campaign_id>/edit/', views.edit_campaign, name='edit_campaign'),
    path('campaigns/<int:campaign_id>/update/post/', views.post_campaign_update, name='post_campaign_update'),

    # Donor URLs
    path('campaigns/active/', views.list_active_campaigns, name='list_active_campaigns'),
    path('campaigns/<int:campaign_id>/', views.campaign_details, name='campaign_details'), # Renamed for clarity
    path('campaigns/<int:campaign_id>/donate/', views.donate_to_campaign, name='donate'), # Renamed for clarity

    # Admin URLs
    path('admin/review-campaigns/', views.admin_review_submitted_campaigns, name='admin_review_submitted_campaigns'),
    path('admin/campaigns/<int:campaign_id>/approve/', views.admin_approve_campaign, name='admin_approve_campaign'),
    path('admin/campaigns/<int:campaign_id>/reject/', views.admin_reject_campaign, name='admin_reject_campaign'),
    path('admin/monitor-data/', views.admin_monitor_data, name='admin_monitor_data'),
    path('admin/reports/', views.admin_generate_reports, name='admin_generate_reports'),
]