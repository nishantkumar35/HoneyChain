"""
Colonies Forms
"""

from django import forms
from .models import BeeColony
from apiaries.models import Apiary

INPUT_CLASS = 'w-full px-4 py-3 rounded-xl border border-amber-200 focus:outline-none focus:ring-2 focus:ring-amber-400 bg-amber-50'


class BeeColonyForm(forms.ModelForm):
    """Form to create and edit a BeeColony."""

    class Meta:
        model = BeeColony
        fields = ['apiary', 'colony_name', 'colony_type', 'establishment_date', 'health_status']
        widgets = {
            'apiary': forms.Select(attrs={'class': INPUT_CLASS}),
            'colony_name': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'e.g., Hive Alpha'
            }),
            'colony_type': forms.Select(attrs={'class': INPUT_CLASS}),
            'establishment_date': forms.DateInput(attrs={
                'class': INPUT_CLASS,
                'type': 'date'
            }),
            'health_status': forms.Select(attrs={'class': INPUT_CLASS}),
        }
        labels = {
            'apiary': 'Select Apiary',
            'colony_name': 'Colony Name',
            'colony_type': 'Colony / Bee Type',
            'establishment_date': 'Establishment Date',
            'health_status': 'Health Status',
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict apiary choices to beekeepers's own apiaries
        if user is not None:
            self.fields['apiary'].queryset = Apiary.objects.filter(beekeeper=user)

