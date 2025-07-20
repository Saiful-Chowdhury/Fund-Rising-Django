# core/forms.py

from django import forms
from .models import Campaign, DonationTransaction, CustomUser, Organization # Import Organization
from django.contrib.auth.forms import UserCreationForm as AuthUserCreationForm

class UserRegistrationForm(AuthUserCreationForm):
    user_role = forms.ChoiceField(choices=CustomUser.USER_ROLES, initial='Donor')

    class Meta(AuthUserCreationForm.Meta):
        model = CustomUser
        fields = AuthUserCreationForm.Meta.fields + ('user_role',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_role = self.cleaned_data['user_role']
        if commit:
            user.save()
        return user

class CampaignForm(forms.ModelForm):
    requested_organization_for_approval = forms.ModelChoiceField(
        queryset=Organization.objects.none(), # Start with an empty queryset
        required=True, # Still required as per your last change
        empty_label="--- Select an Organization ---",
        help_text="Select an approved organization to request their approval for this campaign."
        # --- REMOVE OR COMMENT OUT THIS LINE ---
        # label_from_instance=lambda obj: f"{obj.organization_name} ({obj.organization_email})"
    )

    class Meta:
        model = Campaign
        fields = [
            'campaign_name', 'description', 'target_amount',
            'start_date', 'end_date', 'requested_organization_for_approval'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['requested_organization_for_approval'].queryset = Organization.objects.filter(status='Approved')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', "End date cannot be before start date.")

        return cleaned_data
    # Add a ModelChoiceField for selecting the organization
    # This will display a dropdown of organizations.
    # The queryset will be filtered in the __init__ method.
    requested_organization_for_approval = forms.ModelChoiceField(
        queryset=Organization.objects.none(), # Start with an empty queryset
        required=True, # Make it optional if a campaign doesn't need org approval
        empty_label="No specific organization (Site Admin approval)",
        help_text="Select an organization to request their approval for this campaign. If none is selected, it will be subject to site admin approval."
    )

    class Meta:
        model = Campaign
        fields = [
            'campaign_name', 'description', 'target_amount',
            'start_date', 'end_date', 'requested_organization_for_approval' # Add the new field here
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter the queryset for 'requested_organization_for_approval'
        # to only show organizations that are 'Approved'
        self.fields['requested_organization_for_approval'].queryset = Organization.objects.filter(status='Approved')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', "End date cannot be before start date.")

        return cleaned_data


class DonationForm(forms.ModelForm):
    # Define your payment method choices
    PAYMENT_METHOD_CHOICES = [
        ('Card', 'Credit/Debit Card'),
        ('Mobile Banking', 'Mobile Banking (e.g., Bkash, Nagad)'),
        ('Bank Transfer', 'Bank Transfer'),
        ('PayPal', 'PayPal'),
        # Add more if needed
    ]

    # Add the payment_method field explicitly as a ChoiceField
    # This overrides the default field Django would create from the model
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        label="Select Payment Method",
        widget=forms.Select(attrs={'class': 'form-select'}) # Add Bootstrap class for styling
    )

    class Meta:
        model = DonationTransaction
        fields = ['amount', 'payment_method']
        # You can add widgets for other fields if you want custom styling for 'amount'
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
        }