from django import forms
from .models import Transaction, Customer, Payment, Expense


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'tin', 'phone', 'email', 'address', 'location', 'supply', 'balance']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }



class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['customer', 'amount', 'method', 'notes', 'date']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'method': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'notes', 'amount', 'location', 'date']  # ✅ add date
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter expense name'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter location'}),
            'date': forms.DateInput(attrs={'type': 'date'}),  # ✅ HTML date picker
        }


class TransactionForm(forms.ModelForm):
    # Computed fields (readonly display only)
    total_sales = forms.DecimalField(
        label="Total Sales", required=False, disabled=True,
        decimal_places=2, max_digits=12
    )
    total_cashout = forms.DecimalField(
        label="Total Cashout", required=False, disabled=True,
        decimal_places=2, max_digits=12
    )
    difference = forms.DecimalField(
        label="Difference", required=False, disabled=True,
        decimal_places=2, max_digits=12
    )
    less_excess = forms.DecimalField(
        label="Less/Excess", required=False, disabled=True,
        decimal_places=2, max_digits=12
    )

    class Meta:
        model = Transaction
        fields = [
            'date', 'location', 'opening_balance', 'customer_balance',
            'paid', 'wholesale', 'debt', 'cash', 'accounts', 'expenses',
            'notes',
            # readonly totals
            'total_sales', 'total_cashout', 'difference', 'less_excess'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'customer_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'wholesale': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'debt': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cash': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'accounts': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expenses': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate readonly totals if editing an existing transaction
        if self.instance and self.instance.pk:
            self.fields['total_sales'].initial = self.instance.total_sales
            self.fields['total_cashout'].initial = self.instance.total_cashout
            self.fields['difference'].initial = self.instance.difference
            self.fields['less_excess'].initial = self.instance.less_excess

from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'notes', 'amount', 'location', 'date']  # ✅ add date
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter expense name'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter location'}),
            'date': forms.DateInput(attrs={'type': 'date'}),  # ✅ HTML date picker
        }

