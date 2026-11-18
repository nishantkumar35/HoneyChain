"""
Honey Views — Batch CRUD + Blockchain Registration + QR Code generation.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .models import HoneyBatch, BlockchainRecord
from .forms import HoneyBatchForm
from blockchain.services import register_batch_on_blockchain, verify_batch_on_blockchain
from blockchain.utils import generate_batch_hash, generate_qr_code


@login_required
def batch_list(request):
    """List all honey batches for the logged-in beekeeper."""
    batches = HoneyBatch.objects.filter(beekeeper=request.user).select_related('apiary')
    return render(request, 'honey/batch_list.html', {'batches': batches})


@login_required
def batch_create(request):
    """Create a new honey batch."""
    if request.method == 'POST':
        form = HoneyBatchForm(user=request.user, data=request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.beekeeper = request.user
            # Generate SHA-256 hash of batch data BEFORE saving
            batch.save()  # Save first to get batch_id
            batch.data_hash = generate_batch_hash(batch)
            # Generate QR code pointing to the public verification URL
            generate_qr_code(batch, request)
            batch.save()
            messages.success(request, f'Honey batch {batch.batch_id} created successfully!')
            return redirect('honey:detail', pk=batch.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HoneyBatchForm(user=request.user)

    return render(request, 'honey/batch_form.html', {
        'form': form,
        'title': 'Create New Honey Batch',
        'button_text': 'Create Batch',
    })


@login_required
def batch_edit(request, pk):
    """
    Edit a honey batch.
    Once registered on blockchain, editing is prevented to preserve data integrity.
    """
    batch = get_object_or_404(HoneyBatch, pk=pk)

    if batch.beekeeper != request.user:
        raise PermissionDenied

    # Prevent editing blockchain-registered batches
    if batch.is_registered_on_blockchain:
        messages.warning(
            request,
            f'Batch {batch.batch_id} is registered on the blockchain and cannot be edited. '
            'Create a new batch if corrections are needed.'
        )
        return redirect('honey:detail', pk=pk)

    if request.method == 'POST':
        form = HoneyBatchForm(user=request.user, data=request.POST, instance=batch)
        if form.is_valid():
            batch = form.save(commit=False)
            # Regenerate hash when data changes
            batch.data_hash = generate_batch_hash(batch)
            generate_qr_code(batch, request)
            batch.save()
            messages.success(request, f'Batch {batch.batch_id} updated successfully!')
            return redirect('honey:detail', pk=batch.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HoneyBatchForm(user=request.user, instance=batch)

    return render(request, 'honey/batch_form.html', {
        'form': form,
        'batch': batch,
        'title': f'Edit Batch {batch.batch_id}',
        'button_text': 'Save Changes',
    })


@login_required
def batch_detail(request, pk):
    """View full details of a honey batch including blockchain record."""
    batch = get_object_or_404(HoneyBatch, pk=pk)

    if batch.beekeeper != request.user:
        raise PermissionDenied

    blockchain_record = getattr(batch, 'blockchain_record', None)

    return render(request, 'honey/batch_detail.html', {
        'batch': batch,
        'blockchain_record': blockchain_record,
    })


@login_required
def batch_delete(request, pk):
    """Delete a batch. Blockchain-registered batches cannot be deleted."""
    batch = get_object_or_404(HoneyBatch, pk=pk)

    if batch.beekeeper != request.user:
        raise PermissionDenied

    if batch.is_registered_on_blockchain:
        messages.error(request, 'Blockchain-registered batches cannot be deleted.')
        return redirect('honey:detail', pk=pk)

    if request.method == 'POST':
        batch_id = batch.batch_id
        batch.delete()
        messages.success(request, f'Batch {batch_id} deleted successfully.')
        return redirect('honey:list')

    return render(request, 'honey/batch_confirm_delete.html', {'batch': batch})


@login_required
def batch_register_blockchain(request, pk):
    """
    Register a honey batch on the blockchain.
    This calls the Hardhat smart contract via Web3.py.
    POST only.
    """
    batch = get_object_or_404(HoneyBatch, pk=pk)

    if batch.beekeeper != request.user:
        raise PermissionDenied

    if batch.is_registered_on_blockchain:
        messages.warning(request, f'Batch {batch.batch_id} is already registered on the blockchain.')
        return redirect('honey:detail', pk=pk)

    if request.method == 'POST':
        result = register_batch_on_blockchain(batch)

        if result['success']:
            messages.success(
                request,
                f'✅ Batch {batch.batch_id} successfully registered on the blockchain! '
                f'Transaction: {result["tx_hash"][:20]}...'
            )
        else:
            messages.error(
                request,
                f'❌ Blockchain registration failed: {result["error"]}. '
                'Make sure your Hardhat node is running and the contract is deployed.'
            )

    return redirect('honey:detail', pk=pk)


@login_required
def batch_verify_blockchain(request, pk):
    """
    Verify a batch against the blockchain.
    Compares the current SHA-256 hash with the hash stored on-chain.
    """
    batch = get_object_or_404(HoneyBatch, pk=pk)

    if batch.beekeeper != request.user:
        raise PermissionDenied

    if not batch.is_registered_on_blockchain:
        messages.warning(request, 'This batch has not been registered on the blockchain yet.')
        return redirect('honey:detail', pk=pk)

    result = verify_batch_on_blockchain(batch)

    if result['success']:
        if result['verified']:
            messages.success(request, '✅ Verification successful! Batch data matches the blockchain record.')
        else:
            messages.error(request, '❌ Verification failed! The batch data has been tampered with.')
    else:
        messages.error(request, f'Verification error: {result["error"]}')

    return redirect('honey:detail', pk=pk)

