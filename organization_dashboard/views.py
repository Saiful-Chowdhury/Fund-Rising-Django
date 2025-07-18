# organization_dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, UpdateView
from django.contrib import messages
from django.utils import timezone

from .mixins import OrganizationAdminRequiredMixin
from .forms import CampaignApprovalForm
from core.models import Campaign, Organization, AnalyticsData # Import AnalyticsData

# Create a dummy home view if you don't have one in your main project urls
def home_view(request):
    return render(request, 'base_home.html') # A very basic home page for redirection

class OrganizationDashboardView(OrganizationAdminRequiredMixin, TemplateView):
    template_name = 'organization_dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The mixin ensures request.user.managed_organization exists and is approved
        organization = self.request.user.managed_organization
        context['organization'] = organization

        # Get campaigns related to this organization
        # Campaigns that explicitly requested approval from this organization
        context['campaigns_pending_review'] = Campaign.objects.filter(
            requested_organization_for_approval=organization,
            organization_approval_status='Pending Organization Review'
        ).order_by('-created_at')

        # Campaigns that this organization has officially taken under management (approved)
        context['approved_managed_campaigns'] = Campaign.objects.filter(
            organization=organization, # The 'organization' ForeignKey means it's approved/managed by them
            status__in=['Approved', 'Active', 'Completed']
        ).order_by('-organization_approved_at')

        # Campaigns this organization has rejected
        context['rejected_campaigns_by_org'] = Campaign.objects.filter(
            requested_organization_for_approval=organization,
            organization_approval_status='Rejected by Organization'
        ).order_by('-organization_approved_at')

        # Log analytics event
        AnalyticsData.objects.create(
            event_type='Organization Dashboard View',
            user=self.request.user,
            organization=organization,
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        return context

class CampaignsPendingApprovalView(OrganizationAdminRequiredMixin, ListView):
    model = Campaign
    template_name = 'organization_dashboard/campaign_list.html'
    context_object_name = 'campaigns'

    def get_queryset(self):
        organization = self.request.user.managed_organization
        # Filter for campaigns that requested approval from this specific organization
        # and are still pending review by the organization.
        queryset = Campaign.objects.filter(
            requested_organization_for_approval=organization,
            organization_approval_status='Pending Organization Review'
        ).order_by('-created_at')

        # Log analytics event
        AnalyticsData.objects.create(
            event_type='Organization Pending Campaigns View',
            user=self.request.user,
            organization=organization,
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_title'] = "Campaigns Awaiting Your Review"
        context['action_url_name'] = 'organization_dashboard:campaign_approve_reject' # URL for action
        return context


class OrganizationManagedCampaignsView(OrganizationAdminRequiredMixin, ListView):
    model = Campaign
    template_name = 'organization_dashboard/campaign_list.html'
    context_object_name = 'campaigns'

    def get_queryset(self):
        organization = self.request.user.managed_organization
        # Campaigns where this organization is the assigned manager (approved them)
        queryset = Campaign.objects.filter(
            organization=organization
        ).order_by('-created_at')

        # Log analytics event
        AnalyticsData.objects.create(
            event_type='Organization Managed Campaigns View',
            user=self.request.user,
            organization=organization,
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_title'] = "Campaigns Managed by Your Organization"
        context['show_approval_status'] = True # To display org-specific status
        return context


class CampaignApprovalUpdateView(OrganizationAdminRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignApprovalForm
    template_name = 'organization_dashboard/campaign_approval.html'
    success_url = reverse_lazy('organization_dashboard:campaigns_pending_approval') # Redirect after action

    def get_queryset(self):
        # Ensure that an organization admin can only approve/reject campaigns
        # that *specifically requested* approval from their organization.
        organization = self.request.user.managed_organization
        return Campaign.objects.filter(
            requested_organization_for_approval=organization,
            organization_approval_status='Pending Organization Review'
        )

    def form_valid(self, form):
        campaign = form.save(commit=False)
        organization = self.request.user.managed_organization

        original_status = campaign.organization_approval_status # Get original status

        if campaign.organization_approval_status == 'Approved by Organization':
            campaign.organization = organization # Assign this organization as the manager
            campaign.organization_approved_at = timezone.now()
            # Optionally, you can also set the main status to 'Approved'
            # if the site admin relies solely on org approval for a certain type of campaign.
            # campaign.status = 'Approved'
            messages.success(self.request, f"Campaign '{campaign.campaign_name}' has been approved by your organization.")
            AnalyticsData.objects.create(
                event_type='Campaign Approved by Organization',
                user=self.request.user,
                organization=organization,
                campaign=campaign,
                ip_address=self.request.META.get('REMOTE_ADDR'),
                details={'status_change_from': original_status, 'status_change_to': 'Approved by Organization'}
            )
        elif campaign.organization_approval_status == 'Rejected by Organization':
            campaign.organization = None # Do not link if rejected
            campaign.organization_approved_at = None
            # Optionally, set main status to 'Rejected'
            # campaign.status = 'Rejected'
            messages.warning(self.request, f"Campaign '{campaign.campaign_name}' has been rejected by your organization.")
            AnalyticsData.objects.create(
                event_type='Campaign Rejected by Organization',
                user=self.request.user,
                organization=organization,
                campaign=campaign,
                ip_address=self.request.META.get('REMOTE_ADDR'),
                details={'status_change_from': original_status, 'status_change_to': 'Rejected by Organization', 'comment': campaign.organization_approval_comment}
            )

        campaign.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.get_object()
        return context