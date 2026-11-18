"""
Apiaries Views — CRUD for Apiary management.
All views require login. Beekeepers can only access their own apiaries.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .models import Apiary
from .forms import ApiaryForm


@login_required
def apiary_list(request):
    """List all apiaries owned by the logged-in beekeeper."""
    apiaries = Apiary.objects.filter(beekeeper=request.user)
    return render(request, 'apiaries/apiary_list.html', {'apiaries': apiaries})


@login_required
def apiary_add(request):
    """Add a new apiary."""
    if request.method == 'POST':
        form = ApiaryForm(request.POST)
        if form.is_valid():
            apiary = form.save(commit=False)
            apiary.beekeeper = request.user  # Assign to logged-in beekeeper
            apiary.save()
            messages.success(request, f'Apiary "{apiary.name}" added successfully!')
            return redirect('apiaries:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ApiaryForm()

    return render(request, 'apiaries/apiary_form.html', {
        'form': form,
        'title': 'Add New Apiary',
        'button_text': 'Add Apiary',
    })


@login_required
def apiary_edit(request, pk):
    """Edit an existing apiary. Only the owner can edit."""
    apiary = get_object_or_404(Apiary, pk=pk)

    # Ownership check — prevent cross-user access
    if apiary.beekeeper != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = ApiaryForm(request.POST, instance=apiary)
        if form.is_valid():
            form.save()
            messages.success(request, f'Apiary "{apiary.name}" updated successfully!')
            return redirect('apiaries:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ApiaryForm(instance=apiary)

    return render(request, 'apiaries/apiary_form.html', {
        'form': form,
        'apiary': apiary,
        'title': f'Edit {apiary.name}',
        'button_text': 'Save Changes',
    })


@login_required
def apiary_delete(request, pk):
    """Delete an apiary. Only the owner can delete."""
    apiary = get_object_or_404(Apiary, pk=pk)

    if apiary.beekeeper != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        name = apiary.name
        apiary.delete()
        messages.success(request, f'Apiary "{name}" deleted successfully.')
        return redirect('apiaries:list')

    return render(request, 'apiaries/apiary_confirm_delete.html', {'apiary': apiary})


@login_required
def apiary_detail(request, pk):
    """View details of a specific apiary including its colonies and batches."""
    apiary = get_object_or_404(Apiary, pk=pk)

    if apiary.beekeeper != request.user:
        raise PermissionDenied

    colonies = apiary.beecolony_set.all()
    batches  = apiary.honeybatch_set.all()

    return render(request, 'apiaries/apiary_detail.html', {
        'apiary': apiary,
        'colonies': colonies,
        'batches': batches,
    })

