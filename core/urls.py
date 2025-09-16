from django.urls import path
from . import views
app_name='core'
urlpatterns=[path('locations/',views.location_list,name='location_list'),path('locations/add/',views.location_add,name='location_add'),path('locations/create/',views.location_create_api,name='location_create_api')]
