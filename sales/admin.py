from django.contrib import admin
from .models import SaleEntry

@admin.register(SaleEntry)
class SaleEntryAdmin(admin.ModelAdmin):
    list_display = ('date','user','opening_cash','wholesale','retail_sale','customer_balance','expenses','bank_deposit','daily_total','cash_difference')
    list_filter = ('date','user')
    search_fields = ('user__username',)
