"""
blockchain/services.py — High-level functions that Django views call
to register and verify honey batches on the blockchain.
"""

import logging
from django.conf import settings
from django.utils import timezone

from .contract import get_web3, get_contract, is_blockchain_available
from .utils import generate_batch_hash

logger = logging.getLogger(__name__)


def register_batch_on_blockchain(batch) -> dict:
    """
    Register a honey batch on the HoneyChain smart contract.

    Steps:
    1. Generate the SHA-256 hash of batch data.
    2. Call registerBatch() on the smart contract.
    3. Wait for the transaction receipt.
    4. Store tx_hash, block_number, and blockchain_hash in BlockchainRecord.
    5. Mark batch as is_registered_on_blockchain = True.

    Returns:
        dict with keys: success (bool), tx_hash, block_number, error (str)
    """
    if not is_blockchain_available():
        return {
            'success': False,
            'error': (
                'Blockchain node is not reachable. '
                'Start Hardhat with: cd smart_contract && npx hardhat node'
            )
        }

    contract = get_contract()
    if contract is None:
        return {
            'success': False,
            'error': 'Smart contract not loaded. Check CONTRACT_ADDRESS in your .env file.'
        }

    w3 = get_web3()
    private_key = settings.DEPLOYER_PRIVATE_KEY

    if not private_key:
        return {
            'success': False,
            'error': 'DEPLOYER_PRIVATE_KEY is not set in .env. Cannot sign transactions.'
        }

    try:
        # Recompute hash to ensure accuracy
        data_hash = generate_batch_hash(batch)
        batch_id  = batch.batch_id

        # Get the deployer account from the private key
        account = w3.eth.account.from_key(private_key)

        # Build the transaction
        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.registerBatch(
            batch_id,
            f"0x{data_hash}"   # Pass as hex string with 0x prefix
        ).build_transaction({
            'from':     account.address,
            'nonce':    nonce,
            'gas':      200000,
            'gasPrice': w3.eth.gas_price,
        })

        # Sign and send the transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash   = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for the transaction to be mined (up to 120 seconds)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if receipt['status'] != 1:
            return {
                'success': False,
                'error': 'Transaction was reverted by the smart contract.'
            }

        tx_hash_hex  = tx_hash.to_0x_hex() if hasattr(tx_hash, 'to_0x_hex') else (f"0x{tx_hash.hex()}" if not str(tx_hash).startswith("0x") else str(tx_hash))
        block_number = receipt['blockNumber']

        # Save blockchain record to Django database
        from honey.models import BlockchainRecord
        record, created = BlockchainRecord.objects.update_or_create(
            honey_batch=batch,
            defaults={
                'transaction_hash':   tx_hash_hex,
                'block_number':       block_number,
                'blockchain_hash':    f"0x{data_hash}",
                'verification_status': 'Verified',
                'registered_at':      timezone.now(),
            }
        )

        # Update the batch
        batch.data_hash = data_hash
        batch.is_registered_on_blockchain = True
        batch.save(update_fields=['data_hash', 'is_registered_on_blockchain'])

        logger.info(
            f"Batch {batch_id} registered on blockchain. "
            f"TX: {tx_hash_hex}, Block: {block_number}"
        )

        return {
            'success':      True,
            'tx_hash':      tx_hash_hex,
            'block_number': block_number,
        }

    except Exception as e:
        logger.error(f"Blockchain registration error for batch {batch.batch_id}: {e}")
        return {
            'success': False,
            'error':   str(e)
        }


def verify_batch_on_blockchain(batch) -> dict:
    """
    Verify a batch by comparing the current SHA-256 hash with the on-chain hash.

    Returns:
        dict with keys: success (bool), verified (bool), error (str)
    """
    if not is_blockchain_available():
        return {
            'success': False,
            'verified': False,
            'error': 'Blockchain node is not reachable.'
        }

    contract = get_contract()
    if contract is None:
        return {
            'success': False,
            'verified': False,
            'error': 'Smart contract not loaded.'
        }

    try:
        # Recompute current hash from batch data
        current_hash_hex = f"0x{generate_batch_hash(batch)}"

        # Query the smart contract verifyBatch method
        is_verified_on_chain, is_registered_on_chain = contract.functions.verifyBatch(
            batch.batch_id,
            current_hash_hex
        ).call()

        # Also fetch the stored on-chain hash for display
        raw_on_chain_hash = contract.functions.getBatchHash(batch.batch_id).call()
        if hasattr(raw_on_chain_hash, 'to_0x_hex'):
            on_chain_hash = raw_on_chain_hash.to_0x_hex()
        elif isinstance(raw_on_chain_hash, (bytes, bytearray)):
            on_chain_hash = f"0x{raw_on_chain_hash.hex()}"
        else:
            on_chain_hash = str(raw_on_chain_hash)

        verified = bool(is_verified_on_chain)

        # Update verification status in the database
        if hasattr(batch, 'blockchain_record'):
            record = batch.blockchain_record
            record.verification_status = 'Verified' if verified else 'Verification Failed'
            record.save(update_fields=['verification_status'])

        logger.info(
            f"Verification for batch {batch.batch_id}: "
            f"{'PASS' if verified else 'FAIL'} "
            f"(current={current_hash_hex[:10]}..., on-chain={on_chain_hash[:10]}...)"
        )

        return {
            'success':        True,
            'verified':       verified,
            'is_registered':  is_registered_on_chain,
            'current_hash':   current_hash_hex,
            'on_chain_hash':  on_chain_hash,
        }

    except Exception as e:
        logger.error(f"Verification error for batch {batch.batch_id}: {e}")
        return {
            'success':  False,
            'verified': False,
            'error':    str(e)
        }

