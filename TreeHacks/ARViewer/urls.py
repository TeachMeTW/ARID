from django.urls import path
from . import views

urlpatterns = [
    path('cam/', views.cam, name='cam'),
    path('add-id/', views.addID, name="add-id"),
    path('', views.index, name='index'),   
]
