from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Location(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SaleEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    date = models.DateField()

    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')

    opening_cash = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    customer_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Credit sales added today")
    wholesale = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    retail_sale = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bank_deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Stored for reporting; auto-computed before save
    cash_difference = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    daily_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-id']
        unique_together = ('user', 'date', 'id')

    def compute_daily_total(self) -> Decimal:
        return (self.customer_balance or 0) + (self.wholesale or 0) + (self.retail_sale or 0)

    def compute_cash_difference(self) -> Decimal:
        # Per user instruction: opening + wholesale + retail + customer balance - expenses
        # Track bank_deposit separately (it does not change 'cash difference' here).
        return (self.opening_cash or 0) + self.compute_daily_total() - (self.expenses or 0)

    @property
    def net_cash_after_deposit(self) -> Decimal:
        # A helpful derived metric for reconciliation
        return self.compute_cash_difference() - (self.bank_deposit or 0)

    def save(self, *args, **kwargs):
        self.daily_total = self.compute_daily_total()
        self.cash_difference = self.compute_cash_difference()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
