from django import forms
from .models import SaleEntry

class SaleEntryForm(forms.ModelForm):
    class Meta:
        model = SaleEntry
        fields = [
            'date','opening_cash','customer_balance','wholesale','retail_sale',
            'expenses','bank_deposit','location'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'opening_cash': forms.NumberInput(attrs={'step': '0.01'}),
            'customer_balance': forms.NumberInput(attrs={'step': '0.01'}),
            'wholesale': forms.NumberInput(attrs={'step': '0.01'}),
            'retail_sale': forms.NumberInput(attrs={'step': '0.01'}),
            'expenses': forms.NumberInput(attrs={'step': '0.01'}),
            'bank_deposit': forms.NumberInput(attrs={'step': '0.01'}),
        }
