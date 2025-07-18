# organization_auth/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views # Django's built-in auth views
from .views import OrganizationRegisterView, OrganizationLoginView, register_success

app_name = 'organization_auth' # Namespace for URLs

urlpatterns = [
    path('register/', OrganizationRegisterView.as_view(), name='register'),
    path('register/success/', register_success, name='register_success'),
    path('login/', OrganizationLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'), # Redirects to home after logout
]