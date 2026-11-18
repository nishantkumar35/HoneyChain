"""
blockchain/verification.py — Public-facing verification helpers
used by the traceability app (no login required).
"""

import logging
from .services import verify_batch_on_blockchain
from .contract import is_blockchain_available

logger = logging.getLogger(__name__)


def get_public_verification_status(batch) -> dict:
    """
    Get the verification status of a batch for the public verification page.

    This function is safe to call without authentication.
    It does NOT expose private keys or deployer information.

    Returns a dict with:
        - status:            'Verified' | 'Verification Failed' | 'Not Registered' | 'Node Offline'
        - tx_hash:           str or None
        - block_number:      int or None
        - blockchain_online: bool
        - message:           user-friendly message
    """
    blockchain_online = is_blockchain_available()

    if not batch.is_registered_on_blockchain:
        return {
            'status':           'Not Registered',
            'tx_hash':          None,
            'block_number':     None,
            'blockchain_online': blockchain_online,
            'message':          'This batch has not been registered on the blockchain yet.',
        }

    # Retrieve stored blockchain record
    record = getattr(batch, 'blockchain_record', None)

    if not blockchain_online:
        # Return stored status if node is offline
        stored_status = record.verification_status if record else 'Unknown'
        return {
            'status':            stored_status,
            'tx_hash':           record.transaction_hash if record else None,
            'block_number':      record.block_number if record else None,
            'blockchain_online': False,
            'message':           (
                'Blockchain node is currently offline. '
                'Showing last known verification status.'
            ),
        }

    # Node is online — do a live verification
    result = verify_batch_on_blockchain(batch)

    if not result['success']:
        return {
            'status':            'Error',
            'tx_hash':           record.transaction_hash if record else None,
            'block_number':      record.block_number if record else None,
            'blockchain_online': True,
            'message':           f"Verification error: {result.get('error', 'Unknown error')}",
        }

    status = 'Verified' if result['verified'] else 'Verification Failed'
    message = (
        '✅ This batch is authentic. The data matches the blockchain record.'
        if result['verified']
        else '❌ Warning: The batch data does NOT match the blockchain record. It may have been tampered with.'
    )

    return {
        'status':            status,
        'tx_hash':           record.transaction_hash if record else None,
        'block_number':      record.block_number if record else None,
        'blockchain_online': True,
        'message':           message,
    }

