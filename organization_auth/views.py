# organization_auth/views.py
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import OrganizationRegistrationForm
from core.models import Organization # <--- Add this line
class OrganizationRegisterView(SuccessMessageMixin, CreateView):
    model = Organization
    form_class = OrganizationRegistrationForm
    template_name = 'organization_auth/register.html'
    success_url = reverse_lazy('organization_auth:register_success') # Redirect to a success page
    success_message = "Your organization registration request has been submitted successfully and is awaiting admin approval."

    def get(self, request, *args, **kwargs):
        # If an Organization Admin is already logged in, redirect them
        if request.user.is_authenticated and request.user.user_role == 'Organization Admin':
            return redirect('organization_dashboard:dashboard')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        # The form's save method handles creating the CustomUser and linking it
        response = super().form_valid(form)
        return response

class OrganizationLoginView(DjangoLoginView):
    template_name = 'organization_auth/login.html'
    redirect_authenticated_user = True # Redirects if user is already logged in

    def get_success_url(self):
        # Redirect Organization Admins to their dashboard, others to default
        if self.request.user.is_authenticated and self.request.user.user_role == 'Organization Admin':
            return reverse_lazy('organization_dashboard:dashboard')
        return super().get_success_url()

def register_success(request):
    return render(request, 'organization_auth/register_success.html')