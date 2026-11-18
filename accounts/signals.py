"""
Accounts Signals — auto-create BeekeeperProfile when a new User is created.
"""

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import BeekeeperProfile


@receiver(post_save, sender=User)
def create_beekeeper_profile(sender, instance, created, **kwargs):
    """Automatically create a BeekeeperProfile when a User is created."""
    if created:
        BeekeeperProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_beekeeper_profile(sender, instance, **kwargs):
    """Save the BeekeeperProfile whenever the User is saved."""
    if hasattr(instance, 'beekeeper_profile'):
        instance.beekeeper_profile.save()

