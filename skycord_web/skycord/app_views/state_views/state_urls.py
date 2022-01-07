from django.urls import path

from . import state_views

g_start_url = 'state/'

url_list = [
    path('main/', state_views.Main_Index, name='Main_Index'),

    path(g_start_url + 'farm/', state_views.Farm_State, name='Farm_State'),
    path(g_start_url + 'farm/<int:farm_id>/device/', state_views.Device_State, name='Device_State'),
    path(g_start_url + 'device/<int:device_id>', state_views.Device_Image_List, name='Device_Image_List'),

    path(g_start_url + 'split_image_show/<int:split_image_id>', state_views.Split_Image_Show, name='Split_Image_Show'),
    
]