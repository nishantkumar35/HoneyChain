"""
Colonies Views — CRUD for Bee Colony management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .models import BeeColony
from .forms import BeeColonyForm


@login_required
def colony_list(request):
    """List all colonies owned by the logged-in beekeeper (across all apiaries)."""
    colonies = BeeColony.objects.filter(apiary__beekeeper=request.user)
    return render(request, 'colonies/colony_list.html', {'colonies': colonies})


@login_required
def colony_add(request):
    """Add a new bee colony."""
    if request.method == 'POST':
        form = BeeColonyForm(user=request.user, data=request.POST)
        if form.is_valid():
            colony = form.save()
            messages.success(request, f'Colony "{colony.colony_name}" added successfully!')
            return redirect('colonies:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-select apiary from query param if provided
        initial = {}
        apiary_pk = request.GET.get('apiary')
        if apiary_pk:
            initial['apiary'] = apiary_pk
        form = BeeColonyForm(user=request.user, initial=initial)

    return render(request, 'colonies/colony_form.html', {
        'form': form,
        'title': 'Add New Colony',
        'button_text': 'Add Colony',
    })


@login_required
def colony_edit(request, pk):
    """Edit an existing colony. Ownership verified through apiary."""
    colony = get_object_or_404(BeeColony, pk=pk)

    if colony.apiary.beekeeper != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = BeeColonyForm(user=request.user, data=request.POST, instance=colony)
        if form.is_valid():
            form.save()
            messages.success(request, f'Colony "{colony.colony_name}" updated successfully!')
            return redirect('colonies:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BeeColonyForm(user=request.user, instance=colony)

    return render(request, 'colonies/colony_form.html', {
        'form': form,
        'colony': colony,
        'title': f'Edit {colony.colony_name}',
        'button_text': 'Save Changes',
    })


@login_required
def colony_delete(request, pk):
    """Delete a colony."""
    colony = get_object_or_404(BeeColony, pk=pk)

    if colony.apiary.beekeeper != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        name = colony.colony_name
        colony.delete()
        messages.success(request, f'Colony "{name}" deleted successfully.')
        return redirect('colonies:list')

    return render(request, 'colonies/colony_confirm_delete.html', {'colony': colony})

