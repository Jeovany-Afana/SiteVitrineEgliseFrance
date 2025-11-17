import os
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from EcoleBiblique.models import FAQ, ChurchLocation, ContactMessage, Event, EventRegistration, NewsletterSubscriber, \
    CalendarEvent, EventAlertSubscription
from django.utils import timezone
from django.contrib import messages

# Create your views here.
def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def gallery(request):
    return render(request, 'gallery.html')


def ministeres(request):
    return render(request, 'ministeres.html')


def contact(request):
    return render(request, 'contact.html')


def evenements(request):
    """Vue pour la page événements - utilise events_view"""
    return events_view(request)


def equipes(request):
    return render(request, 'equipes.html')


def api_gallery_images(request):
    """API pour récupérer les images de la galerie"""
    images_data = []

    # Répertoires à scanner
    directories = [

        ('images/egliseCameroun', ['missions', 'international']),
        ('images/missionKairos', ['missions', 'international']),
        ('images/ecolePrimaire', ['missions', 'social']),
        ('images/egliseEst', ['missions', 'international']),
        ('images/missionKairos', ['missions', 'communautaire']),
    ]

    image_counter = 1
    sizes = ['regular', 'wide', 'tall', 'large']
    size_index = 0

    for directory, categories in directories:
        dir_path = os.path.join(settings.STATICFILES_DIRS[0], directory)

        if os.path.exists(dir_path):
            for filename in os.listdir(dir_path):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    images_data.append({
                        'id': image_counter,
                        'image': f'/static/{directory}/{filename}',
                        'category': categories,
                        'title': f"Mission - {directory.replace('images/', '').title()}",
                        'description': f"Photo de notre mission {directory.replace('images/', '').replace('_', ' ')}",
                        'size': sizes[size_index % len(sizes)]
                    })
                    image_counter += 1
                    size_index += 1

    return JsonResponse(images_data, safe=False)


def contact_page(request):
    """Page de contact principale"""
    locations = ChurchLocation.objects.filter(is_active=True)
    faqs = FAQ.objects.filter(is_active=True)

    context = {
        'locations': locations,
        'faqs': faqs,
    }
    return render(request, 'contact/contact.html', context)


@require_POST
@csrf_exempt
def submit_contact(request):
    """API pour soumettre le formulaire de contact"""
    try:
        data = json.loads(request.body)

        # Création du message
        message = ContactMessage(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone', ''),
            subject=data.get('subject'),
            message=data.get('message'),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        message.save()

        # Envoi d'email de notification (optionnel)
        if settings.EMAIL_HOST_USER:
            send_notification_email(message)

        return JsonResponse({
            'success': True,
            'message': 'Votre message a été envoyé avec succès !'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Une erreur est survenue. Veuillez réessayer.'
        }, status=400)


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_notification_email(contact_message):
    """Envoie un email de notification"""
    subject = f"Nouveau message de contact - {contact_message.subject}"
    message = f"""
    Nouveau message de contact reçu :

    Nom: {contact_message.name}
    Email: {contact_message.email}
    Téléphone: {contact_message.phone}
    Sujet: {contact_message.get_subject_display()}

    Message:
    {contact_message.message}

    ---
    Cet email a été envoyé automatiquement depuis le site web.
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.CONTACT_EMAIL],  # À définir dans settings.py
        fail_silently=True,
    )


def events_view(request):
    """Vue principale pour les événements"""
    # Récupérer tous les événements à venir
    upcoming_events = Event.objects.filter(
        start_date__gte=timezone.now()
    ).order_by('start_date')

    # Événements spéciaux (featured)
    featured_events = Event.objects.filter(
        featured=True,
        start_date__gte=timezone.now()
    ).order_by('start_date')[:2]

    # Événements par catégorie
    events_by_category = {
        'all': upcoming_events,
        'upcoming': upcoming_events,
        'special': upcoming_events.filter(category='special'),
        'conference': upcoming_events.filter(category='conference'),
        'youth': upcoming_events.filter(category='youth'),
        'monthly': upcoming_events.filter(category='monthly'),  # CORRIGÉ : upcoming_events au lieu de upcoming_models
    }

    context = {
        'upcoming_events': upcoming_events,
        'featured_events': featured_events,
        'events_by_category': events_by_category,
    }

    return render(request, 'evenements.html', context)  # CORRIGÉ : 'evenements.html' au lieu de 'events.html'


def event_detail(request, event_id):
    """Vue pour les détails d'un événement spécifique"""
    event = get_object_or_404(Event, id=event_id)

    context = {
        'event': event,
    }
    return render(request, 'event_detail.html', context)


def event_registration(request, event_id):
    """Vue pour l'inscription à un événement"""
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        # Récupérer les données du formulaire
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        number_of_participants = int(request.POST.get('participants', 1))
        special_requests = request.POST.get('message', '')

        # Vérifier la disponibilité
        if not event.can_register(number_of_participants):
            messages.error(request,
                           f"Désolé, il ne reste pas assez de places pour {number_of_participants} personne(s).")
            return redirect('event_registration', event_id=event.id)

        try:
            # Créer l'inscription
            registration = EventRegistration(
                event=event,
                full_name=full_name,
                email=email,
                phone=phone,
                number_of_participants=number_of_participants,
                special_requests=special_requests,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            # Vérifier si on peut confirmer directement
            if event.can_register(number_of_participants):
                registration.confirm_registration()
                status_message = "Votre inscription a été confirmée !"
                email_subject = f"Confirmation d'inscription - {event.title}"
            else:
                registration.status = 'waiting_list'
                registration.save()
                status_message = "Vous avez été ajouté à la liste d'attente."
                email_subject = f"Inscription en liste d'attente - {event.title}"

            # Envoyer un email de confirmation
            send_registration_email(registration, email_subject)

            messages.success(request, status_message)
            return redirect('event_detail', event_id=event.id)

        except Exception as e:
            messages.error(request, "Une erreur est survenue lors de l'inscription. Veuillez réessayer.")
            print(f"Erreur d'inscription: {e}")

    context = {
        'event': event,
    }
    return render(request, 'event_registration.html', context)


def send_registration_email(registration, subject):
    """Envoyer un email de confirmation d'inscription"""
    event = registration.event

    message = f"""
    Bonjour {registration.full_name},

    {subject}

    Détails de votre inscription :
    - Événement : {event.title}
    - Date : {event.start_date.strftime('%d/%m/%Y')}
    - Heure : {event.start_date.strftime('%H:%M')} - {event.end_date.strftime('%H:%M')}
    - Lieu : {event.location}
    - Nombre de participants : {registration.number_of_participants}

    {"STATUT : INSCRIPTION CONFIRMÉE" if registration.is_confirmed else "STATUT : LISTE D'ATTENTE"}

    {"Votre inscription a été confirmée. Nous avons hâte de vous voir !" if registration.is_confirmed else "Votre inscription est en liste d'attente. Nous vous contacterons si des places se libèrent."}

    Informations importantes :
    {event.description}

    Pour toute question, n'hésitez pas à nous contacter.

    Cordialement,
    L'équipe de l'Église Missionnaire Propulsion
    """

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [registration.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erreur d'envoi d'email: {e}")


def event_registrations_list(request, event_id):
    """Vue pour voir toutes les inscriptions d'un événement (admin)"""
    event = get_object_or_404(Event, id=event_id)
    registrations = event.registrations.all().order_by('-registration_date')

    context = {
        'event': event,
        'registrations': registrations,
    }
    return render(request, 'event_registrations_list.html', context)


@require_POST
@csrf_exempt
def subscribe_newsletter(request):
    """API pour s'inscrire à la newsletter"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if not email:
            return JsonResponse({
                'success': False,
                'message': 'L\'adresse email est obligatoire.'
            }, status=400)

        # Vérifier si l'email existe déjà
        if NewsletterSubscriber.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'Cette adresse email est déjà inscrite.'
            }, status=400)

        # Créer l'abonné
        subscriber = NewsletterSubscriber(
            email=email,
            first_name=first_name,
            last_name=last_name,
            ip_address=get_client_ip(request)
        )
        subscriber.save()

        return JsonResponse({
            'success': True,
            'message': 'Inscription réussie ! Merci de vous être abonné à notre newsletter.'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Une erreur est survenue. Veuillez réessayer.'
        }, status=500)




def events_calendar(request):
    """Vue pour le calendrier complet des événements"""
    # Récupérer les paramètres de filtrage
    location_slug = request.GET.get('location', 'all')
    event_type = request.GET.get('type', 'all')
    month = request.GET.get('month', timezone.now().month)
    year = request.GET.get('year', timezone.now().year)

    # Filtrer les événements
    calendar_events = CalendarEvent.objects.filter(
        start_date__gte=timezone.now()
    ).select_related('location')

    if location_slug != 'all':
        calendar_events = calendar_events.filter(location__city_slug=location_slug)

    if event_type != 'all':
        calendar_events = calendar_events.filter(event_type=event_type)

    # Grouper par mois
    events_by_month = {}
    for event in calendar_events:
        month_key = event.start_date.strftime('%Y-%m')
        if month_key not in events_by_month:
            events_by_month[month_key] = {
                'name': event.start_date.strftime('%B %Y'),
                'events': []
            }
        events_by_month[month_key]['events'].append(event)

    # Lieux disponibles
    locations = ChurchLocation.objects.filter(is_active=True)

    context = {
        'calendar_events': calendar_events,
        'events_by_month': events_by_month,
        'locations': locations,
        'current_location': location_slug,
        'current_event_type': event_type,
    }

    return render(request, 'events_calendar.html', context)


@require_POST
@csrf_exempt
def subscribe_event_alerts(request):
    """API pour s'inscrire aux alertes événements"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        phone = data.get('phone', '')
        location = data.get('location', 'all')
        categories = data.get('categories', [])

        if not email:
            return JsonResponse({
                'success': False,
                'message': 'L\'adresse email est obligatoire.'
            }, status=400)

        # Vérifier si l'email existe déjà
        if EventAlertSubscription.objects.filter(email=email, is_active=True).exists():
            return JsonResponse({
                'success': False,
                'message': 'Vous êtes déjà inscrit aux alertes événements.'
            }, status=400)

        # Désactiver les anciennes inscriptions du même email
        EventAlertSubscription.objects.filter(email=email).update(is_active=False)

        # Créer la nouvelle inscription
        subscription = EventAlertSubscription(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            location=location,
            categories=categories,
            ip_address=get_client_ip(request)
        )
        subscription.save()

        return JsonResponse({
            'success': True,
            'message': 'Félicitations ! Vous êtes maintenant inscrit aux alertes événements.'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Une erreur est survenue. Veuillez réessayer.'
        }, status=500)


def get_upcoming_events_api(request):
    """API pour récupérer les événements à venir"""
    location = request.GET.get('location', 'all')
    limit = int(request.GET.get('limit', 10))

    events = CalendarEvent.objects.filter(
        start_date__gte=timezone.now()
    ).select_related('location').order_by('start_date')[:limit]

    if location != 'all':
        events = events.filter(location__city_slug=location)

    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'event_type': event.event_type,
            'location': {
                'name': event.location.name,
                'city': event.location.city,
                'address': event.location.address
            },
            'start_date': event.start_date.isoformat(),
            'end_date': event.end_date.isoformat(),
            'image_url': event.image.url if event.image else None,
            'registration_required': event.registration_required,
            'registration_url': event.registration_url,
        })

    return JsonResponse(events_data, safe=False)