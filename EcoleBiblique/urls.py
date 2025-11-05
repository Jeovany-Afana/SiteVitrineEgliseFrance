from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
path('api/gallery-images/', views.api_gallery_images, name='api_gallery_images'),

    path('ministeres/', views.ministeres, name='ministeres'),
    path('contact/', views.contact, name='contact'),
path('contact/submit/', views.submit_contact, name='submit_contact'),

    path('evenements/', views.evenements, name='evenements'),
path('evenements/<int:event_id>/', views.event_detail, name='event_detail'),
    path('evenements/<int:event_id>/inscription/', views.event_registration, name='event_registration'),
path('admin/evenements/<int:event_id>/inscriptions/', views.event_registrations_list, name='event_registrations_list'),
# urls.py
path('evenements/calendrier/', views.events_calendar, name='events_calendar'),
path('api/event-alerts/subscribe/', views.subscribe_event_alerts, name='subscribe_event_alerts'),
path('api/upcoming-events/', views.get_upcoming_events_api, name='upcoming_events_api'),
    path('calendrier/', views.events_calendar, name='events_calendar'),

    path('equipes/', views.equipes, name='equipes'),
# urls.py
path('newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
]