# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db import transaction, models # <--- ADD 'models' HERE
from django.contrib import messages
from .forms import CampaignForm, DonationForm, UserRegistrationForm
from .models import CustomUser, Campaign, CampaignUpdate, DonationTransaction, Notification, AnalyticsData

def is_campaign_manager(user):
    return user.is_authenticated and user.user_role == 'Campaign Manager'

def is_donor(user):
    return user.is_authenticated and user.user_role == 'Donor'

def is_admin(user):
    return user.is_authenticated and user.user_role == 'Admin'

# --- General Views ---
def home(request):
    # Log analytics data for home page view (example)
    if request.user.is_authenticated:
        AnalyticsData.objects.create(
            event_type='Home Page View',
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            details={'user_role': request.user.user_role}
        )
    else:
        AnalyticsData.objects.create(
            event_type='Home Page View - Guest',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    user_role = request.user.user_role
    context = {
        'user_role': user_role,
        'username': request.user.username,
    }

    if user_role == 'Campaign Manager':
        context['pending_approval_campaigns'] = Campaign.objects.filter(campaign_manager=request.user, status='Pending Approval').count()
        context['active_campaigns'] = Campaign.objects.filter(campaign_manager=request.user, status='Active').count()
        context['completed_campaigns'] = Campaign.objects.filter(campaign_manager=request.user, status='Completed').count()
    elif user_role == 'Donor':
        context['total_donations'] = DonationTransaction.objects.filter(donor=request.user, transaction_status='Successful').count()
        context['total_amount_donated'] = DonationTransaction.objects.filter(donor=request.user, transaction_status='Successful').aggregate(models.Sum('amount'))['amount__sum'] or 0
    elif user_role == 'Admin':
        context['pending_campaigns_for_review'] = Campaign.objects.filter(status='Pending Approval').count()
        context['total_active_campaigns'] = Campaign.objects.filter(status='Active').count()
        context['total_donations_count'] = DonationTransaction.objects.filter(transaction_status='Successful').count()

    return render(request, 'core/dashboard.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login') # Redirect to login after successful registration
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                AnalyticsData.objects.create(event_type='User Login', user=user, ip_address=request.META.get('REMOTE_ADDR'))
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def user_logout(request):
    AnalyticsData.objects.create(event_type='User Logout', user=request.user, ip_address=request.META.get('REMOTE_ADDR'))
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

# --- Campaign Manager Views ---
@login_required
@user_passes_test(is_campaign_manager)
def create_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.campaign_manager = request.user
            campaign.save()
            messages.success(request, 'Campaign submitted for approval!')
            AnalyticsData.objects.create(event_type='Campaign Created', user=request.user, campaign=campaign)
            return redirect('my_campaigns')
    else:
        form = CampaignForm()
    return render(request, 'core/create_campaign.html', {'form': form})

@login_required
@user_passes_test(is_campaign_manager)
def my_campaigns(request):
    campaigns = Campaign.objects.filter(campaign_manager=request.user).order_by('-created_at')
    return render(request, 'core/my_campaigns.html', {'campaigns': campaigns})

@login_required
@user_passes_test(is_campaign_manager)
def edit_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, campaign_manager=request.user)
    if request.method == 'POST':
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            # If a rejected campaign is resubmitted, change status back to pending
            if campaign.status == 'Rejected':
                campaign.status = 'Pending Approval'
                campaign.rejection_reason = None # Clear rejection reason on resubmit
            form.save()
            messages.success(request, 'Campaign updated successfully!')
            AnalyticsData.objects.create(event_type='Campaign Edited', user=request.user, campaign=campaign)
            return redirect('my_campaigns')
    else:
        form = CampaignForm(instance=campaign)
    return render(request, 'core/edit_campaign.html', {'form': form, 'campaign': campaign})

@login_required
@user_passes_test(is_campaign_manager)
def post_campaign_update(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, campaign_manager=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            CampaignUpdate.objects.create(campaign=campaign, title=title, content=content)
            messages.success(request, 'Campaign update posted successfully!')
            AnalyticsData.objects.create(event_type='Campaign Update Posted', user=request.user, campaign=campaign)
            return redirect('campaign_details', campaign_id=campaign.id)
        else:
            messages.error(request, 'Title and content cannot be empty.')
    return render(request, 'core/post_campaign_update.html', {'campaign': campaign})

# --- Donor Views ---
@login_required
@user_passes_test(is_donor)
def list_active_campaigns(request):
    campaigns = Campaign.objects.filter(status='Active').order_by('-created_at')
    return render(request, 'core/list_active_campaigns.html', {'campaigns': campaigns})

@login_required
def campaign_details(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    updates = CampaignUpdate.objects.filter(campaign=campaign).order_by('-posted_at')
    donations = DonationTransaction.objects.filter(campaign=campaign, transaction_status='Successful').order_by('-transaction_date')[:5] # Last 5 donations
    progress_percentage = (campaign.current_amount / campaign.target_amount * 100) if campaign.target_amount > 0 else 0
    progress_percentage = min(100, progress_percentage) # Cap at 100%

    AnalyticsData.objects.create(event_type='View Campaign Details', user=request.user, campaign=campaign, ip_address=request.META.get('REMOTE_ADDR'))

    context = {
        'campaign': campaign,
        'updates': updates,
        'donations': donations,
        'progress_percentage': round(progress_percentage, 2)
    }
    return render(request, 'core/campaign_details.html', context)

@login_required
@user_passes_test(is_donor)
def donate_to_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, status='Active')
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment_method = form.cleaned_data['payment_method']

            with transaction.atomic():
                # Simulate payment processing (replace with actual payment gateway)
                is_payment_successful = True # In a real app, this comes from a payment gateway API call

                if is_payment_successful:
                    donation = DonationTransaction.objects.create(
                        campaign=campaign,
                        donor=request.user,
                        amount=amount,
                        payment_method=payment_method,
                        transaction_status='Successful',
                        donor_name=request.user.username,
                        donor_email=request.user.email
                    )
                    campaign.current_amount += amount
                    campaign.save()

                    # Check if campaign completed
                    if campaign.current_amount >= campaign.target_amount and campaign.status == 'Active':
                        campaign.status = 'Completed'
                        campaign.save()
                        # Trigger disburse funds and notify (could be a separate task)
                        Notification.objects.create(
                            recipient=campaign.campaign_manager,
                            message=f"Your campaign '{campaign.campaign_name}' has reached its target and is completed!"
                        )
                        messages.info(request, f"Campaign '{campaign.campaign_name}' is now completed!")

                    messages.success(request, f'Donation of ${amount} successful to {campaign.campaign_name}!')
                    AnalyticsData.objects.create(event_type='Donation Successful', user=request.user, campaign=campaign, details={'amount': float(amount)})
                    # Optionally, create a notification for the donor
                    Notification.objects.create(
                        recipient=request.user,
                        message=f"Thank you for your donation of ${amount} to '{campaign.campaign_name}'!"
                    )
                    return redirect('campaign_details', campaign_id=campaign.id)
                else:
                    DonationTransaction.objects.create(
                        campaign=campaign,
                        donor=request.user,
                        amount=amount,
                        payment_method=payment_method,
                        transaction_status='Failed',
                        donor_name=request.user.username,
                        donor_email=request.user.email
                    )
                    messages.error(request, 'Payment failed. Please try again.')
                    AnalyticsData.objects.create(event_type='Donation Failed', user=request.user, campaign=campaign, details={'amount': float(amount)})
    else:
        form = DonationForm()
    return render(request, 'core/donate.html', {'campaign': campaign, 'form': form})


# --- Admin Views ---
@login_required
@user_passes_test(is_admin)
def admin_review_submitted_campaigns(request):
    campaigns_to_review = Campaign.objects.filter(status='Pending Approval').order_by('-created_at')
    return render(request, 'core/admin/review_campaigns.html', {'campaigns': campaigns_to_review})

@login_required
@user_passes_test(is_admin)
def admin_approve_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, status='Pending Approval')
    campaign.status = 'Active' # Approved campaigns become active
    campaign.approval_date = timezone.now()
    campaign.save()
    messages.success(request, f'Campaign "{campaign.campaign_name}" approved and is now active.')
    Notification.objects.create(
        recipient=campaign.campaign_manager,
        message=f"Your campaign '{campaign.campaign_name}' has been approved and is now active!"
    )
    AnalyticsData.objects.create(event_type='Campaign Approved', user=request.user, campaign=campaign)
    return redirect('admin_review_submitted_campaigns')

@login_required
@user_passes_test(is_admin)
def admin_reject_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id, status='Pending Approval')
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', 'No reason provided.')
        campaign.status = 'Rejected'
        campaign.rejection_reason = rejection_reason
        campaign.save()
        messages.warning(request, f'Campaign "{campaign.campaign_name}" rejected.')
        Notification.objects.create(
            recipient=campaign.campaign_manager,
            message=f"Your campaign '{campaign.campaign_name}' has been rejected. Reason: {rejection_reason}"
        )
        AnalyticsData.objects.create(event_type='Campaign Rejected', user=request.user, campaign=campaign, details={'reason': rejection_reason})
        return redirect('admin_review_submitted_campaigns')
    return render(request, 'core/admin/reject_campaign.html', {'campaign': campaign})

@login_required
@user_passes_test(is_admin)
def admin_monitor_data(request):
    total_campaigns = Campaign.objects.count()
    active_campaigns = Campaign.objects.filter(status='Active').count()
    completed_campaigns = Campaign.objects.filter(status='Completed').count()
    total_donations_count = DonationTransaction.objects.filter(transaction_status='Successful').count()
    total_donated_amount = DonationTransaction.objects.filter(transaction_status='Successful').aggregate(models.Sum('amount'))['amount__sum'] or 0

    latest_donations = DonationTransaction.objects.filter(transaction_status='Successful').order_by('-transaction_date')[:10]
    latest_campaign_updates = CampaignUpdate.objects.order_by('-posted_at')[:10]

    context = {
        'total_campaigns': total_campaigns,
        'active_campaigns': active_campaigns,
        'completed_campaigns': completed_campaigns,
        'total_donations_count': total_donations_count,
        'total_donated_amount': total_donated_amount,
        'latest_donations': latest_donations,
        'latest_campaign_updates': latest_campaign_updates,
    }
    return render(request, 'core/admin/monitor_data.html', context)

@login_required
@user_passes_test(is_admin)
def admin_generate_reports(request):
    # This would be more complex, potentially involving dynamic filtering, CSV/PDF export
    # For now, a placeholder that lists some summary data
    campaigns_by_status = Campaign.objects.values('status').annotate(count=models.Count('id'))
    donations_by_method = DonationTransaction.objects.values('payment_method').annotate(total_amount=models.Sum('amount'))

    context = {
        'campaigns_by_status': campaigns_by_status,
        'donations_by_method': donations_by_method,
        # Add more report data here
    }
    return render(request, 'core/admin/generate_reports.html', context)