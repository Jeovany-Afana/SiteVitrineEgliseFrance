from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),

    path('ministeres/', views.ministeres, name='ministeres'),
    path('contact/', views.contact, name='contact'),

    path('evenements/', views.evenements, name='evenements'),
]