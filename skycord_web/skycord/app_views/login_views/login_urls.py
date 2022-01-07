from django.urls import path

from . import login_views

g_start_url = ''

url_list = [
    path(g_start_url, login_views.login_Index, name='login_Index'),
    path(g_start_url + 'sign_up/',login_views.sign_up,name='sign_up'),
    path(g_start_url + 'logout/',login_views.logout,name='logout'),
]