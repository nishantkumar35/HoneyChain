"""
Apiaries Models
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Apiary(models.Model):
    """
    Represents a physical beekeeping location (apiary/farm).
    Each apiary belongs to a single beekeeper (User).
    """
    beekeeper = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='apiary_set',
        help_text='The beekeeper who owns this apiary'
    )
    name = models.CharField(
        max_length=200,
        help_text='Name of the apiary (e.g., "Sunflower Farm Apiary")'
    )
    location = models.CharField(
        max_length=300,
        help_text='Geographic location or address of the apiary'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Optional description of the apiary'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Apiary'
        verbose_name_plural = 'Apiaries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.location})"

    def get_colony_count(self):
        """Return the number of bee colonies in this apiary."""
        return self.beecolony_set.count()

    def get_batch_count(self):
        """Return the number of honey batches from this apiary."""
        return self.honeybatch_set.count()

