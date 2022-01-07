from django.urls import path

from . import device_management_views

g_start_url = 'farm_management/detail/<int:farm_id>/device_management/'

url_list = [
    
    path(g_start_url + '', device_management_views.Device_Management, name='Device_Management'),

    path(g_start_url + 'detail/<int:raspberry_id>/', device_management_views.Device_Detail, name='Device_Detail'),

    path(g_start_url + 'create/', device_management_views.Device_Create, name='Device_Create'),
    path(g_start_url + 'delete/<int:raspberry_id>/', device_management_views.Device_Delete, name='Device_Delete'),
]