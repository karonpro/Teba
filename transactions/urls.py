
from django.urls import path
from . import views
app_name='transactions'
urlpatterns=[
    path('customer-info/<int:pk>/', views.customer_info, name='customer_info'),
    # path('', views.transaction_list, name='list'),  # Duplicate, removed
    path('add/', views.transaction_add, name='add'),
    path('<int:pk>/edit/', views.transaction_edit, name='edit'),
    path('<int:pk>/delete/', views.transaction_delete, name='delete'),
    path('customers/', views.customers_list, name='customers'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('payments/add/', views.payment_add, name='payment_add'),
    path('expenses/', views.expenses_list, name='expenses'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('reports/daily/', views.daily_report, name='report_daily'),
    path('reports/daily/export/', views.daily_export, name='report_daily_export'),
     path('<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('', views.transaction_list, name='list'),
    path('reports/', views.report_home, name='report_home'),
    path('reports/customers/', views.customer_report, name='customer_report'),
    path('reports/expenses/', views.expense_report, name='expense_report'),
    path('reports/transactions/', views.transaction_report, name='transaction_report'),
     path('expenses/', views.expenses_list, name='expenses_list'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('expenses/edit/<int:pk>/', views.expense_edit, name='expense_edit'),
    path('expenses/delete/<int:pk>/', views.expense_delete, name='expense_delete'),
]



