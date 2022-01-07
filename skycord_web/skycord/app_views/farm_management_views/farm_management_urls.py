from django.urls import path

from . import farm_management_views

g_start_url = 'farm_management/'

url_list = [
    
    path(g_start_url + '', farm_management_views.Farm_Management, name='Farm_Management'),

    path(g_start_url + 'detail/<int:farm_id>/', farm_management_views.Farm_Detail, name='Farm_Detail'),

    path(g_start_url + 'create/', farm_management_views.Farm_Create, name='Farm_Create'),
    path(g_start_url + 'delete/<int:farm_id>/', farm_management_views.Farm_Delete, name='Farm_Delete'),
]