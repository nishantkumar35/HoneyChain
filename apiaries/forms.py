"""
Apiaries Forms
"""

from django import forms
from .models import Apiary

INPUT_CLASS = 'w-full px-4 py-3 rounded-xl border border-amber-200 focus:outline-none focus:ring-2 focus:ring-amber-400 bg-amber-50'


class ApiaryForm(forms.ModelForm):
    """Form to create and edit an Apiary."""

    class Meta:
        model = Apiary
        fields = ['name', 'location', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'e.g., Sunflower Farm Apiary'
            }),
            'location': forms.TextInput(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'e.g., Village Road, Amritsar, Punjab'
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Describe your apiary (optional)',
                'rows': 4
            }),
        }
        labels = {
            'name': 'Apiary Name',
            'location': 'Location',
            'description': 'Description',
        }

