# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Campaign, CampaignUpdate, DonationTransaction, Notification, AnalyticsData, Organization
from django.utils import timezone
from django.utils.html import format_html # Import for displaying images/links

# Correct way to register CustomUser with CustomUserAdmin
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('User Role', {'fields': ('user_role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('User Role', {'fields': ('user_role',)}),
    )
    list_display = ('username', 'email', 'user_role', 'is_staff', 'is_active')
    list_filter = ('user_role', 'is_staff', 'is_active')
    search_fields = ('username', 'email') # Add search for custom user

admin.site.register(CustomUser, CustomUserAdmin)

# --- Organization Admin ---
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'organization_admin_display', 'status', 'logo_thumbnail', 'verification_doc_link', 'created_at', 'approved_at')
    list_filter = ('status', 'created_at')
    search_fields = ('organization_name', 'contact_email', 'organization_admin__username')
    raw_id_fields = ('organization_admin',) # Useful for selecting the associated CustomUser

    readonly_fields = ('created_at', 'approved_at') # Fields automatically set

    fieldsets = (
        (None, {
            'fields': ('organization_name', 'contact_email', 'contact_phone', 'address', 'description', 'organization_admin')
        }),
        ('Documents and Status', {
            'fields': ('logo', 'verification_document', 'status', 'admin_comment', 'approved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    # Custom field to display the logo image
    def logo_thumbnail(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.logo.url)
        return "No Image"
    logo_thumbnail.short_description = 'Logo'

    # Custom field to display a link to the verification document
    def verification_doc_link(self, obj):
        if obj.verification_document:
            return format_html('<a href="{}" target="_blank">View Document</a>', obj.verification_document.url)
        return "No Document"
    verification_doc_link.short_description = 'Verification Doc'

    def organization_admin_display(self, obj):
        return obj.organization_admin.username if obj.organization_admin else 'N/A'
    organization_admin_display.short_description = 'Org Admin User'


    # Add custom actions for approval and rejection
    actions = ['approve_organizations', 'reject_organizations']

    def approve_organizations(self, request, queryset):
        # Filter to ensure only pending organizations are approved
        updated_count = queryset.filter(status='Pending Approval').update(status='Approved', approved_at=timezone.now(), admin_comment='Approved by superuser admin.')
        self.message_user(request, f'{updated_count} organization(s) successfully approved.')
    approve_organizations.short_description = "Approve selected pending organizations"

    def reject_organizations(self, request, queryset):
        # For simplicity, we'll just set status to Rejected without specific reason input in action
        # In a real app, you might want an intermediate page for admins to input a rejection reason.
        updated_count = queryset.filter(status='Pending Approval').update(status='Rejected', admin_comment='Rejected by superuser admin action.')
        self.message_user(request, f'{updated_count} organization(s) successfully rejected.')
    reject_organizations.short_description = "Reject selected pending organizations"

# --- Campaign Admin ---
@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = (
        'campaign_name', 'campaign_manager', 'organization', 'requested_organization_for_approval',
        'status', 'organization_approval_status',
        'target_amount', 'current_amount', 'start_date', 'end_date', 'created_at'
    )
    list_filter = ('status', 'organization_approval_status', 'created_at', 'start_date', 'end_date', 'organization')
    search_fields = ('campaign_name', 'description', 'campaign_manager__username', 'organization__organization_name')
    raw_id_fields = ('campaign_manager', 'organization', 'requested_organization_for_approval') # Include new FKs

    actions = ['approve_campaigns', 'reject_campaigns']

    # Adjusting the default admin actions for clarity/consistency
    def approve_campaigns(self, request, queryset):
        # This action is for the site superuser to set the *main* campaign status to Approved
        updated_count = queryset.filter(status__in=['Draft', 'Pending Approval']).update(status='Approved', approval_date=timezone.now())
        self.message_user(request, f'{updated_count} campaign(s) successfully approved by site admin.')
    approve_campaigns.short_description = "Approve selected campaigns (Site Admin)"

    def reject_campaigns(self, request, queryset):
        updated_count = queryset.filter(status__in=['Draft', 'Pending Approval']).update(status='Rejected', rejection_reason='Rejected by site admin action')
        self.message_user(request, f'{updated_count} campaign(s) successfully rejected by site admin.')
    reject_campaigns.short_description = "Reject selected campaigns (Site Admin)"

# --- Other Model Admins (unchanged for now) ---
@admin.register(CampaignUpdate)
class CampaignUpdateAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'title', 'posted_at')
    list_filter = ('posted_at', 'campaign')
    search_fields = ('title', 'content', 'campaign__campaign_name')
    raw_id_fields = ('campaign',)

@admin.register(DonationTransaction)
class DonationTransactionAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'donor', 'amount', 'transaction_date', 'payment_method', 'transaction_status')
    list_filter = ('transaction_status', 'payment_method', 'transaction_date')
    search_fields = ('campaign__campaign_name', 'donor__username', 'donor_name', 'donor_email')
    raw_id_fields = ('campaign', 'donor',)
    readonly_fields = ('transaction_date',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'recipient__username')
    search_fields = ('message', 'recipient__username')
    raw_id_fields = ('recipient',)

@admin.register(AnalyticsData)
class AnalyticsDataAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'campaign', 'organization', 'timestamp', 'ip_address') # Added 'organization'
    list_filter = ('event_type', 'timestamp', 'user', 'campaign', 'organization') # Added 'organization'
    search_fields = ('event_type', 'details')
    raw_id_fields = ('user', 'campaign', 'organization',) # Added 'organization'
    readonly_fields = ('timestamp',)