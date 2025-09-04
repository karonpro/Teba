from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [

    path('locations/', views.locations_list, name='locations'),
    path('locations/add/', views.location_create, name='location_add'),
    path('locations/<int:pk>/edit/', views.location_edit, name='location_edit'),
    path('locations/<int:pk>/delete/', views.location_delete, name='location_delete'),
    path('reports/', views.reports_view, name='reports'),

    path('', views.SaleListView.as_view(), name='list'),
    path('add/', views.SaleCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', views.SaleUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.SaleDeleteView.as_view(), name='delete'),
    path('export.csv', views.export_csv, name='export_csv'),
    path('clear/', views.clear_all, name='clear_all'),
]
