# organization_dashboard/forms.py
from django import forms
from core.models import Campaign # Make sure to import your Campaign model

class CampaignApprovalForm(forms.ModelForm):
    # This form is used by an Organization Admin to approve/reject a campaign
    # It focuses on changing the organization_approval_status
    
    # Explicitly define the organization_approval_status field
    # We use forms.ChoiceField to allow explicit control over choices and widget
    organization_approval_status = forms.ChoiceField(
        # The choices are pulled directly from the Campaign model, ensuring consistency
        choices=Campaign.ORG_APPROVAL_STATUS_CHOICES,
        widget=forms.RadioSelect, # Renders as radio buttons
        label="Organization's Approval Decision"
    )

    # Define the organization_approval_comment field
    organization_approval_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False, # It will be conditionally required in the clean method
        help_text="Optional comments regarding the approval, rejection, or status change."
    )

    class Meta:
        model = Campaign
        fields = ['organization_approval_status', 'organization_approval_comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter the choices displayed to the organization admin
        # We exclude 'N/A' as the admin is making an active decision
        # We also exclude 'Pending Organization Approval' as they are now acting on it
        self.fields['organization_approval_status'].choices = [
            (choice, label) for choice, label in Campaign.ORG_APPROVAL_STATUS_CHOICES
            if choice not in ['N/A', 'Pending Organization Approval']
        ]

        # Optional: You can explicitly order the choices if desired for UI
        # For example, to put 'Approved' and 'Active' first:
        # self.fields['organization_approval_status'].choices = [
        #     ('Approved by Organization', 'Approve Campaign'),
        #     ('Active (Org)', 'Set Active'),
        #     ('Inactive (Org)', 'Set Inactive'),
        #     ('Rejected by Organization', 'Reject Campaign'),
        # ]


    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('organization_approval_status')
        comment = cleaned_data.get('organization_approval_comment')

        # Enforce comment for 'Rejected by Organization' AND 'Inactive (Org)' statuses
        if status in ['Rejected by Organization', 'Inactive (Org)'] and not comment:
            self.add_error('organization_approval_comment', "A comment is required when rejecting or setting a campaign as inactive.")

        return cleaned_data