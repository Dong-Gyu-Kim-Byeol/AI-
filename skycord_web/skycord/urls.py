from django.urls import path
from django.urls import include

from . import views
from .app_views.login_views import login_urls
from .app_views.state_views import state_urls
from .app_views.farm_views import farm_urls

from .app_views.farm_management_views import farm_management_urls
from .app_views.device_management_views import device_management_urls

app_name = 'skycord'

urlpatterns = [
    
]

def Add_URL(url_list):
    isinstance(url_list, list)

    for url in url_list:
        urlpatterns.append(url)

Add_URL(login_urls.url_list)
Add_URL(state_urls.url_list)


Add_URL(farm_management_urls.url_list)
Add_URL(device_management_urls.url_list)