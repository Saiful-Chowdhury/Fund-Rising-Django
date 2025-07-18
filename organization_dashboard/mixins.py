# organization_dashboard/mixins.py
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages

class OrganizationAdminRequiredMixin(AccessMixin):
    """
    Mixin to ensure the user is logged in AND has the 'Organization Admin' role,
    AND their associated organization is 'Approved'.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect(reverse_lazy('organization_auth:login'))

        if request.user.user_role != 'Organization Admin':
            messages.error(request, "You do not have the necessary permissions to access this page.")
            return redirect(reverse_lazy('home')) # Redirect to a generic home or error page

        # Check if the associated organization exists and is approved
        # Assuming one-to-one relationship via 'managed_organization'
        if not hasattr(request.user, 'managed_organization') or not request.user.managed_organization.is_approved():
            messages.warning(request, "Your organization's registration is pending approval or has been rejected. You cannot access the dashboard yet.")
            # Optionally, log out the user or redirect to a status page
            # For simplicity, we'll just redirect to login (they can try logging in again to see status)
            return redirect(reverse_lazy('organization_auth:login'))

        return super().dispatch(request, *args, **kwargs)