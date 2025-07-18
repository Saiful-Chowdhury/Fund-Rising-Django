# organization_dashboard/forms.py
from django import forms
from core.models import Campaign

class CampaignApprovalForm(forms.ModelForm):
    # This form is used by an Organization Admin to approve/reject a campaign
    # It focuses on changing the organization_approval_status
    
    organization_approval_status = forms.ChoiceField(
        choices=Campaign.ORG_APPROVAL_STATUS_CHOICES,
        widget=forms.RadioSelect, # Or forms.Select if you prefer a dropdown
        label="Organization's Approval Decision"
    )
    organization_approval_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        help_text="Optional comments regarding the approval or rejection."
    )

    class Meta:
        model = Campaign
        fields = ['organization_approval_status', 'organization_approval_comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude 'N/A' from choices for the organization admin, as they are making a decision
        self.fields['organization_approval_status'].choices = [
            (choice, label) for choice, label in Campaign.ORG_APPROVAL_STATUS_CHOICES
            if choice != 'N/A'
        ]

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('organization_approval_status')
        comment = cleaned_data.get('organization_approval_comment')

        if status == 'Rejected by Organization' and not comment:
            # You can enforce a comment for rejection if needed
            # raise forms.ValidationError("Rejection requires a comment.")
            pass # For now, allow empty comment even for rejection

        return cleaned_data