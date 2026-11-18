"""
Accounts Views — Registration, Login, Logout, Dashboard, Profile.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from .forms import RegistrationForm, LoginForm, ProfileUpdateForm
from .models import BeekeeperProfile


def register_view(request):
    """
    Handle beekeeper registration.
    GET  → show empty registration form
    POST → validate, create user & profile, redirect to dashboard
    """
    # If already logged in, go to dashboard
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in right after registration
            login(request, user)
            messages.success(
                request,
                f'Welcome to HoneyChain, {user.first_name}! Your account has been created.'
            )
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handle beekeeper login.
    GET  → show login form
    POST → authenticate, log in, redirect to dashboard (or next)
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            # Honour the ?next= parameter
            next_url = request.GET.get('next', 'accounts:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


@require_POST
@login_required
def logout_view(request):
    """
    Secure logout — only accepts POST to prevent CSRF-based logout attacks.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard_view(request):
    """
    Beekeeper dashboard — shows summary statistics and recent activity.
    """
    profile = request.user.beekeeper_profile

    # Import here to avoid circular imports
    from apiaries.models import Apiary
    from colonies.models import BeeColony
    from honey.models import HoneyBatch

    apiaries = Apiary.objects.filter(beekeeper=request.user).order_by('-created_at')
    colonies = BeeColony.objects.filter(apiary__beekeeper=request.user)
    batches  = HoneyBatch.objects.filter(beekeeper=request.user).order_by('-created_at')

    context = {
        'profile': profile,
        'total_apiaries':  apiaries.count(),
        'total_colonies':  colonies.count(),
        'total_batches':   batches.count(),
        'verified_batches': batches.filter(is_registered_on_blockchain=True).count(),
        'recent_apiaries': apiaries[:3],
        'recent_batches':  batches[:5],
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    """View and update the beekeeper's profile."""
    profile = request.user.beekeeper_profile

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            # Update User fields (first_name, last_name, email)
            request.user.first_name = form.cleaned_data.get('first_name', request.user.first_name)
            request.user.last_name  = form.cleaned_data.get('last_name', request.user.last_name)
            request.user.email      = form.cleaned_data.get('email', request.user.email)
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(
            instance=profile,
            initial={
                'first_name': request.user.first_name,
                'last_name':  request.user.last_name,
                'email':      request.user.email,
            }
        )

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})

