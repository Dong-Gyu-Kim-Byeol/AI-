from django.urls import path

from . import views

urlpatterns = [
    path('image_echo/', views.image_echo.as_view()),
    path('image_list_predict/', views.image_list_predict.as_view()),
]