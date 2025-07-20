# core/models.py
from django.contrib.auth.models import AbstractUser

# core/models.py (ensure these imports are present)
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone # Add this for approval_date
# ... (rest of your models from previous response)
class CustomUser(AbstractUser):
    USER_ROLES = (
        ('Donor', 'Donor'),
        ('Campaign Manager', 'Campaign Manager'),
        ('Admin', 'Admin'),
    )
    user_role = models.CharField(max_length=50, choices=USER_ROLES, default='Donor')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


from django.db import models
from django.conf import settings # To get AUTH_USER_MODEL

# --- New Organization Model ---
class Organization(models.Model):
    ORGANIZATION_STATUS_CHOICES = [
        ('Pending Approval', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    organization_name = models.CharField(max_length=255, unique=True)
    contact_email = models.EmailField(unique=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    verification_document = models.FileField(upload_to='organization_docs/', blank=True, null=True, help_text="Upload a PDF document for verification.")
    status = models.CharField(max_length=20, choices=ORGANIZATION_STATUS_CHOICES, default='Pending Approval')
    admin_comment = models.TextField(blank=True, null=True, help_text="Comments by site superuser admin regarding approval/rejection.")

    # Link to the CustomUser who is the 'Organization Admin' for this organization
    organization_admin = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_organization',
                                              help_text="The user account that manages this organization's panel.")

    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        permissions = [
            ("can_manage_organization_approvals", "Can approve/reject organizations"),
        ]

    def __str__(self):
        return self.organization_name

    def is_approved(self):
        return self.status == 'Approved'

# --- Modified Campaign Model ---
class Campaign(models.Model):
    CAMPAIGN_STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending Approval', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    campaign_name = models.CharField(max_length=255)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    campaign_manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='managed_campaigns')
    status = models.CharField(max_length=20, choices=CAMPAIGN_STATUS_CHOICES, default='Draft')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    # NEW: Link campaign to an approved Organization
    # A campaign can belong to an organization, meaning that org has oversight/approved it.
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_campaigns_by_org',
                                     help_text="The organization officially managing or endorsing this campaign.")

    # NEW: For a campaigner to request approval from a specific organization
    # This is for the *initial request* by the campaigner to an organization.
    requested_organization_for_approval = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='campaigns_pending_org_approval',
        help_text="If this campaign needs approval from a specific organization."
    )
    
    # NEW: Status specifically for organization's internal review of campaign
    ORG_APPROVAL_STATUS_CHOICES = [
        ('Pending Organization Review', 'Pending Organization Review'),
        ('Approved by Organization', 'Approved by Organization'),
        ('Rejected by Organization', 'Rejected by Organization'),
        ('Active (Org)', 'Active (Organization Approved)'),
        ('N/A', 'N/A'), # For campaigns not needing org approval
    ]
    organization_approval_status = models.CharField(max_length=30, choices=ORG_APPROVAL_STATUS_CHOICES, default='N/A')
    organization_approval_comment = models.TextField(blank=True, null=True)
    organization_approved_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"
        ordering = ['-created_at']

    def __str__(self):
        return self.campaign_name

    def save(self, *args, **kwargs):
        # Example: Automatically set main status to Pending Approval if an org is requested
        if self.requested_organization_for_approval and self.status == 'Draft':
            self.status = 'Pending Approval'
            self.organization_approval_status = 'Pending Organization Review'
        super().save(*args, **kwargs)

# --- Other existing models (CampaignUpdate, DonationTransaction, Notification, AnalyticsData) ---
# (Make sure these are still in your core/models.py, unchanged unless you want to link them to Organization)

class CampaignUpdate(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='updates')
    title = models.CharField(max_length=255)
    content = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f"Update for {self.campaign.campaign_name}: {self.title}"

class DonationTransaction(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='donations')
    donor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations_made')
    donor_name = models.CharField(max_length=255, blank=True, null=True, help_text="Name if not a registered user or anonymous.")
    donor_email = models.EmailField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50) # e.g., 'Stripe', 'PayPal', 'Bank Transfer'
    TRANSACTION_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    transaction_status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='Pending')
    transaction_id = models.CharField(max_length=255, unique=True, blank=True, null=True)

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f"Donation of {self.amount} for {self.campaign.campaign_name} by {self.donor or self.donor_name}"

class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.message[:50]}..."

class AnalyticsData(models.Model):
    EVENT_CHOICES = [
        ('Page View', 'Page View'),
        ('Campaign View', 'Campaign View'),
        ('Donation Attempt', 'Donation Attempt'),
        ('Donation Success', 'Donation Success'),
        ('Login', 'Login'),
        ('Registration', 'Registration'),
        ('Campaign Create', 'Campaign Create'),
        ('Organization Registration', 'Organization Registration'),
        ('Organization Dashboard View', 'Organization Dashboard View'), # Added in previous response
        ('Organization Pending Campaigns View', 'Organization Pending Campaigns View'), # Added in previous response
        ('Campaign Approved by Organization', 'Campaign Approved by Organization'), # Added in previous response
        ('Campaign Rejected by Organization', 'Campaign Rejected by Organization'), # Added in previous response
        # Add more event types as needed
    ]
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events')
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True, help_text="Store additional event details as JSON.")
    
    # --- ADD THIS LINE ---
    user_agent = models.CharField(max_length=255, blank=True, null=True, help_text="User-Agent string from the browser.")

    class Meta:
        verbose_name = "Analytics Datum"
        verbose_name_plural = "Analytics Data"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} by {self.user or self.ip_address} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    EVENT_CHOICES = [
        ('Page View', 'Page View'),
        ('Campaign View', 'Campaign View'),
        ('Donation Attempt', 'Donation Attempt'),
        ('Donation Success', 'Donation Success'),
        ('Login', 'Login'),
        ('Registration', 'Registration'),
        ('Campaign Create', 'Campaign Create'),
        ('Organization Registration', 'Organization Registration'),
        # Add more event types as needed
    ]
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events')
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events')
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events') # Added for organization events
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True, help_text="Store additional event details as JSON.")

    class Meta:
        verbose_name = "Analytics Datum" # Singular name
        verbose_name_plural = "Analytics Data"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} by {self.user or self.ip_address} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"