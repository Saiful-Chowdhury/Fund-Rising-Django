# organization_auth/forms.py
from django import forms
from core.models import Organization, CustomUser
from django.db import transaction # For atomic operations

class OrganizationRegistrationForm(forms.ModelForm):
    # Fields for CustomUser
    username = forms.CharField(max_length=150, help_text="Username for the organization's admin account.")
    email = forms.EmailField(help_text="Email for the organization's admin account.")
    password = forms.CharField(widget=forms.PasswordInput, help_text="Password for the organization's admin account.")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = Organization
        fields = [
            'organization_name', 'contact_email', 'contact_phone',
            'address', 'description', 'logo', 'verification_document'
        ]
        # Make contact_email in Organization form required if it's not already
        # and ensure it's different from the user's login email if preferred
        widgets = {
            'contact_email': forms.EmailInput(attrs={'placeholder': 'Organization main contact email'}),
        }


    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return password_confirm

    def save(self, commit=True):
        # Create CustomUser first, then Organization
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                user_role='Organization Admin', # Assign the specific role
                is_staff=False, # Organization admins are not Django admin staff
                is_active=True # Can be false if you want email verification first
            )
            organization = super().save(commit=False)
            organization.organization_admin = user # Link the user to the organization
            organization.status = 'Pending Approval' # Default status
            if commit:
                organization.save()
            return organization