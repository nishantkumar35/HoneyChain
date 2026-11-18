"""
blockchain/utils.py — SHA-256 hashing and QR code generation.

These utilities do NOT require Web3.py, so they always work
even when the blockchain node is offline.
"""

import hashlib
import json
import os
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse


def generate_batch_hash(batch) -> str:
    """
    Generate a deterministic SHA-256 hash for a HoneyBatch.

    Uses sorted JSON serialisation so the hash is always the same
    for the same batch data regardless of insertion order.

    Returns:
        A 64-character hex string (SHA-256 hash).
    """
    data_dict = batch.get_data_dict()
    # Sort keys for determinism
    json_string = json.dumps(data_dict, sort_keys=True, ensure_ascii=True)
    hash_bytes = hashlib.sha256(json_string.encode('utf-8')).digest()
    return hash_bytes.hex()


def generate_qr_code(batch, request=None):
    """
    Generate a QR code image for the batch's public verification URL
    and save it to the batch's qr_code ImageField.

    Args:
        batch:   A HoneyBatch instance (must already be saved so batch_id exists).
        request: The current HTTP request (used to build an absolute URL).
    """
    # Build the public verification URL
    path = reverse('traceability:verify', kwargs={'batch_id': batch.batch_id})

    if request is not None:
        url = request.build_absolute_uri(path)
    else:
        # Fallback for non-request contexts (e.g., management commands)
        from django.conf import settings
        base_url = getattr(settings, 'SITE_BASE_URL', 'http://localhost:8000')
        url = f"{base_url}{path}"

    # Create QR code with honey-orange fill
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color='#573A34', back_color='#F8E8D9')

    # Save the image to Django's media storage
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    file_name = f"qr_{batch.batch_id}.png"
    batch.qr_code.save(file_name, ContentFile(buffer.read()), save=False)

