from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import Location
from django.contrib.auth.models import User
User = get_user_model()

class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    tin = models.CharField(max_length=50, blank=True, null=True)
    supply = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_supply(self):
        return sum(h.amount for h in self.supply_history.all())

    @property
    def total_payment(self):
        return sum(p.amount for p in self.payments.all())

    @property
    def last_payment(self):
        return self.payments.order_by('-date').first()

    @property
    def balance_color(self):
        if self.balance > 1000:
            return 'green'
        elif 0 < self.balance <= 1000:
            return 'yellow'
        else:
            return 'red'

    def __str__(self):
        return self.name



class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('mobile', 'Mobile Money')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    notes = models.CharField(max_length=255, blank=True)
    
    date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        c = self.customer
        c.balance = (c.balance or 0) - (self.amount or 0)
        c.save()


class Expense(models.Model):
    name = models.CharField(max_length=255)  # Name of the expense
    notes = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(auto_now_add=False)  # or just omit auto_now_add
 
    def __str__(self):
        return self.name


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transactions')
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    customer_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    wholesale = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    debt = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    accounts = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_sales(self):
        return (self.paid or 0) + (self.customer_balance or 0) + (self.wholesale or 0)

    @property
    def total_cashout(self):
        return (self.debt or 0) + (self.cash or 0) + (self.accounts or 0) + (self.expenses or 0)

    @property
    def difference(self):
        return self.total_sales - self.total_cashout

    @property
    def less_excess(self):
        return self.difference - (self.opening_balance or 0)

from django.db import models

class ExpenseName(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class SupplyHistory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='supply_history')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Only update customer supply/balance when a new record is added
            self.customer.supply += self.amount
            self.customer.balance += self.amount
            self.customer.save()
