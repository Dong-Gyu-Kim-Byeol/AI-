from django.urls import path
from . import views

urlpatterns = [
    path('communication/', views.communication),
    path('setting/<str:email>/<str:pwd>/<str:phone>/<str:farm_name>/<str:rasp_name>/', views.settings),
    path('deleteData/<int:user_id>/<int:farm_id>/<int:rasp_id>/',views.deleteDB),
]
