from django.urls import path

from . import farm_views

g_start_url = 'farm_list/'

url_list = [
    path(g_start_url, farm_views.get_ras_list, name='get_ras_list'),
    #path(g_start_url + 'sign_up/',login_views.sign_up,name='sign_up'),
    #path(g_start_url + 'logout/',login_views.logout,name='log_out'),
]