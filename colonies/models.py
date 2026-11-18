"""
Colonies Models
"""

from django.db import models
from django.utils import timezone
from apiaries.models import Apiary


class BeeColony(models.Model):
    """
    Represents a single bee colony (hive) within an apiary.
    """

    COLONY_TYPE_CHOICES = [
        ('Italian',        'Italian Honey Bee'),
        ('Carniolan',      'Carniolan Honey Bee'),
        ('Buckfast',       'Buckfast Bee'),
        ('Russian',        'Russian Honey Bee'),
        ('Caucasian',      'Caucasian Honey Bee'),
        ('Indian',         'Indian Honey Bee (Apis cerana)'),
        ('Giant',          'Giant Honey Bee (Apis dorsata)'),
        ('Other',          'Other'),
    ]

    HEALTH_STATUS_CHOICES = [
        ('Excellent', 'Excellent'),
        ('Good',      'Good'),
        ('Fair',      'Fair'),
        ('Poor',      'Poor'),
        ('Critical',  'Critical'),
    ]

    apiary = models.ForeignKey(
        Apiary,
        on_delete=models.CASCADE,
        related_name='beecolony_set',
        help_text='The apiary this colony belongs to'
    )
    colony_name = models.CharField(
        max_length=200,
        help_text='Unique name or identifier for this colony'
    )
    colony_type = models.CharField(
        max_length=50,
        choices=COLONY_TYPE_CHOICES,
        default='Italian',
        help_text='Bee species / subspecies'
    )
    establishment_date = models.DateField(
        help_text='When was this colony established?'
    )
    health_status = models.CharField(
        max_length=20,
        choices=HEALTH_STATUS_CHOICES,
        default='Good',
        help_text='Current health status of the colony'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Bee Colony'
        verbose_name_plural = 'Bee Colonies'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.colony_name} @ {self.apiary.name}"

