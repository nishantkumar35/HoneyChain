"""
Accounts Models — BeekeeperProfile
Extends Django's built-in User model with beekeeper-specific information.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class BeekeeperProfile(models.Model):
    """
    One-to-one extension of the Django User model.
    Stores additional beekeeper information.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='beekeeper_profile'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Contact phone number'
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text='Physical address of the beekeeper'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Beekeeper Profile'
        verbose_name_plural = 'Beekeeper Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"

    def get_total_apiaries(self):
        """Return count of apiaries owned by this beekeeper."""
        return self.user.apiary_set.count()

    def get_total_colonies(self):
        """Return total bee colonies across all apiaries."""
        from colonies.models import BeeColony
        return BeeColony.objects.filter(apiary__beekeeper=self.user).count()

    def get_total_batches(self):
        """Return count of honey batches created by this beekeeper."""
        return self.user.honeybatch_set.count()

    def get_verified_batches(self):
        """Return count of blockchain-verified batches."""
        return self.user.honeybatch_set.filter(is_registered_on_blockchain=True).count()

