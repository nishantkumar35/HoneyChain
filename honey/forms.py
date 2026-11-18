"""
Honey Forms — Create and Edit Honey Batches.
"""

from django import forms
from .models import HoneyBatch
from apiaries.models import Apiary

INPUT_CLASS = 'w-full px-4 py-3 rounded-xl border border-amber-200 focus:outline-none focus:ring-2 focus:ring-amber-400 bg-amber-50'


class HoneyBatchForm(forms.ModelForm):
    """
    Form for creating and editing honey batches.
    Once a batch is registered on the blockchain, editing is restricted.
    """

    class Meta:
        model = HoneyBatch
        fields = ['apiary', 'honey_source', 'harvest_date', 'quantity', 'location', 'status']
        widgets = {
            'apiary': forms.Select(attrs={'class': INPUT_CLASS}),
            'honey_source': forms.Select(attrs={'class': INPUT_CLASS}),
            'harvest_date': forms.DateInput(attrs={
                'class': INPUT_CLASS,
                'type': 'date'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'e.g., 25.5',
                'step': '0.01',
                'min': '0.01',
            }),
            'location': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'e.g., Mustard Fields, Amritsar, Punjab'
            }),
            'status': forms.Select(attrs={'class': INPUT_CLASS}),
        }
        labels = {
            'apiary':       'Select Apiary',
            'honey_source': 'Honey Source (Floral Type)',
            'harvest_date': 'Harvest Date',
            'quantity':     'Quantity (kg)',
            'location':     'Production Location',
            'status':       'Batch Status',
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show the beekeeper's own apiaries
        if user is not None:
            self.fields['apiary'].queryset = Apiary.objects.filter(beekeeper=user)

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

