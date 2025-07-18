# organization_dashboard/urls.py
from django.urls import path
from .views import (
    OrganizationDashboardView,
    CampaignsPendingApprovalView,
    CampaignApprovalUpdateView,
    OrganizationManagedCampaignsView,
    home_view # Assuming a simple home view for redirection purposes
)

app_name = 'organization_dashboard'

urlpatterns = [
    path('', OrganizationDashboardView.as_view(), name='dashboard'),
    path('campaigns/pending/', CampaignsPendingApprovalView.as_view(), name='campaigns_pending_approval'),
    path('campaigns/managed/', OrganizationManagedCampaignsView.as_view(), name='campaigns_managed'),
    path('campaigns/<int:pk>/approve-reject/', CampaignApprovalUpdateView.as_view(), name='campaign_approve_reject'),
    path('home/', home_view, name='home'), # A dummy home URL to redirect unauth/wrong role users
]