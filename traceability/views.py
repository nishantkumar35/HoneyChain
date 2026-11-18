"""
Traceability Views — Public customer batch verification (no login required).
"""

from django.shortcuts import render, get_object_or_404
from honey.models import HoneyBatch
from blockchain.verification import get_public_verification_status


def batch_verify_public(request, batch_id):
    """
    Public verification page for a honey batch.
    Accessible via QR code scan or direct URL.
    Does NOT expose private beekeeper information.
    """
    batch = get_object_or_404(HoneyBatch, batch_id=batch_id)

    # Get blockchain verification status
    verification = get_public_verification_status(batch)

    # Only expose public-safe information
    context = {
        'batch_id':       batch.batch_id,
        'beekeeper_name': batch.beekeeper.get_full_name() or batch.beekeeper.username,
        'apiary_name':    batch.apiary.name,
        'location':       batch.location,
        'honey_source':   batch.honey_source,
        'harvest_date':   batch.harvest_date,
        'quantity':       batch.quantity,
        'status':         batch.status,
        'verification':   verification,
    }
    return render(request, 'traceability/verify.html', context)


def batch_search(request):
    """
    Allow customers to search for a batch by its ID.
    """
    batch_id = request.GET.get('batch_id', '').strip().upper()
    batch = None
    not_found = False

    if batch_id:
        try:
            batch = HoneyBatch.objects.get(batch_id=batch_id)
            # Redirect to the full verification page
            from django.shortcuts import redirect
            return redirect('traceability:verify', batch_id=batch_id)
        except HoneyBatch.DoesNotExist:
            not_found = True

    return render(request, 'traceability/search.html', {
        'batch_id': batch_id,
        'not_found': not_found,
    })

