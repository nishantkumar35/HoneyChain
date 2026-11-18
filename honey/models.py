"""
Honey Models — HoneyBatch and BlockchainRecord
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apiaries.models import Apiary


def generate_batch_id():
    """Generate a unique, human-readable batch ID like HC-2024-A3F9."""
    uid = uuid.uuid4().hex[:6].upper()
    year = timezone.now().year
    return f"HC-{year}-{uid}"


class HoneyBatch(models.Model):
    """
    Represents a single honey production batch.
    Once registered on blockchain, core fields are locked.
    """

    HONEY_SOURCE_CHOICES = [
        ('Mustard',     'Mustard'),
        ('Eucalyptus',  'Eucalyptus'),
        ('Wildflower',  'Wildflower'),
        ('Litchi',      'Litchi'),
        ('Acacia',      'Acacia'),
        ('Jamun',       'Jamun'),
        ('Sunflower',   'Sunflower'),
        ('Multifloral', 'Multifloral'),
        ('Other',       'Other'),
    ]

    STATUS_CHOICES = [
        ('Harvested',   'Harvested'),
        ('Processing',  'Processing'),
        ('Packaged',    'Packaged'),
        ('Available',   'Available'),
    ]

    # --- Core Identifiers ---
    batch_id = models.CharField(
        max_length=30,
        unique=True,
        default=generate_batch_id,
        editable=False,
        help_text='Auto-generated unique batch identifier'
    )
    beekeeper = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='honeybatch_set'
    )
    apiary = models.ForeignKey(
        Apiary,
        on_delete=models.CASCADE,
        related_name='honeybatch_set'
    )

    # --- Batch Details ---
    honey_source = models.CharField(
        max_length=50,
        choices=HONEY_SOURCE_CHOICES,
        help_text='Type of honey / floral source'
    )
    harvest_date = models.DateField(
        help_text='Date when honey was harvested'
    )
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text='Harvested quantity in kilograms'
    )
    location = models.CharField(
        max_length=300,
        help_text='Production/harvest location'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Harvested'
    )

    # --- Blockchain Fields ---
    data_hash = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text='SHA-256 hash of the batch data (stored on blockchain)'
    )
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        help_text='QR code image for customer traceability'
    )
    is_registered_on_blockchain = models.BooleanField(
        default=False,
        help_text='Whether this batch has been recorded on the blockchain'
    )

    # --- Timestamps ---
    created_at  = models.DateTimeField(default=timezone.now)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Honey Batch'
        verbose_name_plural = 'Honey Batches'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.batch_id} — {self.honey_source} ({self.status})"

    def get_data_dict(self):
        """
        Return a deterministic dictionary of batch data used for SHA-256 hashing.
        Keys are SORTED to ensure hash reproducibility.
        """
        return {
            'apiary_name':    self.apiary.name,
            'batch_id':       self.batch_id,
            'beekeeper_name': self.beekeeper.get_full_name() or self.beekeeper.username,
            'harvest_date':   str(self.harvest_date),
            'honey_source':   self.honey_source,
            'location':       self.location,
            'quantity':       str(self.quantity),
        }


class BlockchainRecord(models.Model):
    """
    Stores blockchain transaction details for a registered HoneyBatch.
    One-to-one relationship: one batch → one blockchain record.
    """

    VERIFICATION_STATUS_CHOICES = [
        ('Verified',             'Verified'),
        ('Verification Failed',  'Verification Failed'),
        ('Pending',              'Pending'),
    ]

    honey_batch = models.OneToOneField(
        HoneyBatch,
        on_delete=models.CASCADE,
        related_name='blockchain_record'
    )
    transaction_hash = models.CharField(
        max_length=66,
        help_text='Ethereum transaction hash (0x...)'
    )
    block_number = models.PositiveBigIntegerField(
        help_text='Block number where transaction was mined'
    )
    blockchain_hash = models.CharField(
        max_length=66,
        help_text='Hash stored on blockchain (hex-encoded)'
    )
    verification_status = models.CharField(
        max_length=30,
        choices=VERIFICATION_STATUS_CHOICES,
        default='Pending'
    )
    registered_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Blockchain Record'
        verbose_name_plural = 'Blockchain Records'
        ordering = ['-registered_at']

    def __str__(self):
        return f"Blockchain Record for {self.honey_batch.batch_id}"

