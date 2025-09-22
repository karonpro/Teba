from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('customer-info/<int:pk>/', views.customer_info, name='customer_info'),
    path('add/', views.transaction_add, name='add'),
    path('<int:pk>/edit/', views.transaction_edit, name='edit'),
    path('<int:pk>/delete/', views.transaction_delete, name='delete'),

    # Customers
    path('customers/', views.customers_list, name='customers'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('customers/<int:customer_id>/add_supply/', views.add_supply, name='add_supply'),
    path('customers/export/', views.export_customers_csv, name='export_customers_csv'),

    # Payments
    path('payments/add/', views.payment_add, name='payment_add'),

    # Expenses
    path('expenses/', views.expenses_list, name='expenses'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('expenses/edit/<int:pk>/', views.expense_edit, name='expense_edit'),
    path('expenses/delete/<int:pk>/', views.expense_delete, name='expense_delete'),

    # Reports
    path('reports/daily/', views.daily_report, name='report_daily'),
    path('reports/daily/export/', views.daily_export, name='report_daily_export'),
    path('reports/', views.report_home, name='report_home'),
    path('reports/customers/', views.customer_report, name='customer_report'),
    path('reports/expenses/', views.expense_report, name='expense_report'),
    path('reports/transactions/', views.transaction_report, name='transaction_report'),

    # Transactions
    path('', views.transaction_list, name='list'),
    path('<int:pk>/', views.transaction_detail, name='transaction_detail'),
]
