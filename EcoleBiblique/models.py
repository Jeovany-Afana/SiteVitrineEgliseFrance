from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.utils import timezone

class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('information', 'Demande d\'information'),
        ('prayer', 'Demande de prière'),
        ('visit', 'Planifier une visite'),
        ('volunteer', 'Devenir bénévole'),
        ('donation', 'Information sur les dons'),
        ('other', 'Autre'),
    ]

    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('read', 'Lu'),
        ('replied', 'Répondu'),
        ('archived', 'Archivé'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Adresse email")
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Numéro de téléphone",
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Format de téléphone invalide")]
    )
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")

    # Métadonnées
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Statut")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%d/%m/%Y')})"


class ChurchLocation(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom du lieu")
    address = models.TextField(verbose_name="Adresse complète")
    city = models.CharField(max_length=100, verbose_name="Ville")
    country = models.CharField(max_length=100, verbose_name="Pays", default="France")
    pastor_in_charge = models.CharField(
        "Pasteur responsable", max_length=255, blank=True, null=True
    )
    sort_order = models.PositiveIntegerField(
        "Ordre d’affichage", default=0, db_index=True
    )

    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email")

    # Coordonnées GPS pour la carte
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitude")

    # Horaires
    opening_hours = models.TextField(verbose_name="Horaires d'ouverture")

    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Lieu d'église"
        verbose_name_plural = "Lieux d'église"
        ordering = ["sort_order", "name"]  # optionnel

    def __str__(self):
        return f"{self.name} - {self.city}"


class Event(models.Model):
    EVENT_CATEGORIES = [
        ('special', 'Événement Spécial'),
        ('conference', 'Conférence'),
        ('youth', 'Jeunesse'),
        ('monthly', 'Mensuel'),
        ('prayer', 'Prière'),
        ('worship', 'Adoration'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    category = models.CharField(max_length=20, choices=EVENT_CATEGORIES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    max_participants = models.IntegerField(default=0)
    current_participants = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    registration_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()

    @property
    def is_featured(self):
        return self.featured

    @property
    def available_spots(self):
        return self.max_participants - self.current_participants

    @property
    def available_spots(self):
        """Nombre de places disponibles"""
        if self.max_participants == 0:
            return float('inf')  # Places illimitées
        return max(0, self.max_participants - self.current_participants)

    @property
    def registration_count(self):
        """Nombre total d'inscriptions (tous statuts confondus)"""
        return self.registrations.count()

    @property
    def confirmed_registrations(self):
        """Inscriptions confirmées"""
        return self.registrations.filter(status='confirmed')

    @property
    def confirmed_participants_count(self):
        """Nombre de participants confirmés"""
        return sum(reg.number_of_participants for reg in self.confirmed_registrations())

    @property
    def waiting_list_count(self):
        """Nombre de personnes en liste d'attente"""
        return self.registrations.filter(status='waiting_list').count()

    @property
    def is_full(self):
        """L'événement est-il complet ?"""
        return self.available_spots <= 0

    @property
    def registration_rate(self):
        """Taux de remplissage en pourcentage"""
        if self.max_participants == 0:
            return 0
        return (self.current_participants / self.max_participants) * 100

    def can_register(self, number_of_participants=1):
        """Vérifier si une inscription est possible"""
        if self.max_participants == 0:
            return True
        return self.available_spots >= number_of_participants

    def add_to_waiting_list(self, registration):
        """Ajouter une inscription en liste d'attente"""
        registration.status = 'waiting_list'
        registration.save()

    class Meta:
        ordering = ['start_date']


class FAQ(models.Model):
    question = models.CharField(max_length=300, verbose_name="Question")
    answer = models.TextField(verbose_name="Réponse")
    category = models.CharField(max_length=100, verbose_name="Catégorie")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.question



class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
        ('waiting_list', 'Liste d\'attente'),
    ]

    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='Événement'
    )

    # Informations du participant
    full_name = models.CharField(
        max_length=200,
        verbose_name='Nom complet'
    )
    email = models.EmailField(
        verbose_name='Adresse email'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Numéro de téléphone'
    )

    # Détails de l'inscription
    number_of_participants = models.PositiveIntegerField(
        default=1,
        verbose_name='Nombre de participants'
    )
    special_requests = models.TextField(
        blank=True,
        verbose_name='Demandes spéciales'
    )

    # Statut et métadonnées
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Statut'
    )
    registration_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'inscription"
    )
    confirmation_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de confirmation'
    )

    # Informations techniques
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Adresse IP'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )

    class Meta:
        verbose_name = 'Inscription à un événement'
        verbose_name_plural = 'Inscriptions aux événements'
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['email', 'registration_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(number_of_participants__gt=0),
                name='positive_number_of_participants'
            ),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.event.title}"

    @property
    def is_confirmed(self):
        return self.status == 'confirmed'

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_cancelled(self):
        return self.status == 'cancelled'

    @property
    def total_price(self):
        """Calculer le prix total si l'événement est payant"""
        if self.event.price > 0:
            return self.event.price * self.number_of_participants
        return 0

    def confirm_registration(self):
        """Confirmer l'inscription"""
        if self.status == 'pending':
            self.status = 'confirmed'
            self.confirmation_date = timezone.now()
            self.save()

            # Mettre à jour le compteur de participants
            self.event.current_participants += self.number_of_participants
            self.event.save()

    def cancel_registration(self):
        """Annuler l'inscription"""
        if self.status in ['pending', 'confirmed']:
            old_status = self.status
            self.status = 'cancelled'
            self.save()

            # Si c'était confirmé, réduire le compteur
            if old_status == 'confirmed':
                self.event.current_participants = max(0, self.event.current_participants - self.number_of_participants)
                self.event.save()


# models.py
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    first_name = models.CharField(max_length=100, blank=True, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, blank=True, verbose_name="Nom")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")

    class Meta:
        verbose_name = "Abonné à la newsletter"
        verbose_name_plural = "Abonnés à la newsletter"
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


# models.py
class EventAlertSubscription(models.Model):
    LOCATION_CHOICES = [
        ('all', 'Tous les lieux'),
        ('cergy', 'Cergy'),
        ('paris', 'Paris'),
        ('yaounde', 'Yaoundé'),
        ('douala', 'Douala'),
    ]

    CATEGORY_CHOICES = [
        ('all', 'Tous les événements'),
        ('special', 'Événements spéciaux'),
        ('conference', 'Conférences'),
        ('youth', 'Jeunesse'),
        ('prayer', 'Prière'),
        ('worship', 'Adoration'),
    ]

    email = models.EmailField(verbose_name="Adresse email")
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='all', verbose_name="Lieu préféré")
    categories = models.JSONField(default=list, verbose_name="Catégories préférées")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    token = models.CharField(max_length=100, unique=True, verbose_name="Token de sécurité")

    class Meta:
        verbose_name = "Abonnement aux alertes événements"
        verbose_name_plural = "Abonnements aux alertes événements"
        ordering = ['-subscribed_at']

    def __str__(self):
        return f"{self.email} - {self.get_location_display()}"

    def save(self, *args, **kwargs):
        if not self.token:
            import secrets
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)


class CalendarEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('regular', 'Régulier'),
        ('special', 'Spécial'),
        ('conference', 'Conférence'),
        ('prayer', 'Prière'),
        ('youth', 'Jeunesse'),
        ('social', 'Social'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, verbose_name="Type d'événement")
    location = models.ForeignKey('ChurchLocation', on_delete=models.CASCADE, verbose_name="Lieu")  # Utilise le premier ChurchLocation
    start_date = models.DateTimeField(verbose_name="Date et heure de début")
    end_date = models.DateTimeField(verbose_name="Date et heure de fin")
    is_recurring = models.BooleanField(default=False, verbose_name="Événement récurrent")
    recurrence_pattern = models.CharField(max_length=100, blank=True, verbose_name="Modèle de récurrence")
    image = models.ImageField(upload_to='calendar/', blank=True, null=True, verbose_name="Image")
    registration_required = models.BooleanField(default=False, verbose_name="Inscription requise")
    registration_url = models.URLField(blank=True, verbose_name="Lien d'inscription")
    max_participants = models.IntegerField(default=0, verbose_name="Nombre maximum de participants")
    is_featured = models.BooleanField(default=False, verbose_name="En vedette")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        verbose_name = "Événement calendrier"
        verbose_name_plural = "Événements calendrier"
        ordering = ['start_date']

    def __str__(self):
        return f"{self.title} - {self.location.city} - {self.start_date.strftime('%d/%m/%Y')}"

    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.start_date > timezone.now()