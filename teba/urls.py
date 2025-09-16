from django.contrib import admin
from transactions import views as transactions_views
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔑 Authentication routes
    path('accounts/login/', auth_views.LoginView.as_view(template_name='transactions/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # App routes
    path('', transactions_views.home, name='home'),
    path('reports/', include(('transactions.reports_urls', 'reports'), namespace='reports')),
    path('core/', include(('core.urls', 'core'), namespace='core')),
    path('transactions/', include(('transactions.urls', 'transactions'), namespace='transactions')),
]
