from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ContactMessage, ChurchLocation, FAQ, Event, EventRegistration, NewsletterSubscriber, CalendarEvent, \
    EventAlertSubscription


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at', 'admin_actions']
    list_filter = ['status', 'subject', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'user_agent']
    list_per_page = 20

    fieldsets = (
        ('Informations du contact', {
            'fields': ('name', 'email', 'phone', 'subject')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Métadonnées', {
            'fields': ('status', 'ip_address', 'user_agent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Actions')
    def admin_actions(self, obj):
        # CORRECTION : Utilise 'EcoleBiblique' au lieu de 'contact'
        url = reverse('admin:EcoleBiblique_contactmessage_change', args=[obj.pk])
        return format_html('<a class="button" href="{}">Voir</a>', url)


@admin.register(ChurchLocation)
class ChurchLocationAdmin(admin.ModelAdmin):
    # Montrer les colonnes existantes du modèle
    list_display = ['name', 'city', 'country', 'pastor_in_charge', 'phone', 'is_active', 'sort_order']
    # Le premier lien cliquable (NE DOIT PAS être dans list_editable)
    list_display_links = ['name']
    # On n’édite que des champs RÉELS du modèle et présents dans list_display
    list_editable = ['is_active', 'sort_order']

    list_filter = ['country', 'city', 'is_active']
    search_fields = ['name', 'city', 'pastor_in_charge', 'address']

    fieldsets = (
        ('Informations principales', {
            # Remplacer 'order' par 'sort_order'
            'fields': ('name', 'pastor_in_charge', 'is_active', 'sort_order')
        }),
        ('Adresse', {
            'fields': ('address', 'city', 'country')
        }),
        ('Coordonnées', {
            'fields': ('phone', 'email')
        }),
        ('Coordonnées GPS', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Horaires', {
            'fields': ('opening_hours',)
        }),
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'start_date', 'location', 'featured', 'is_upcoming']
    list_filter = ['category', 'featured', 'start_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'event',
        'number_of_participants',
        'status',
        'registration_date',
        'total_price_display'
    ]

    list_filter = [
        'status',
        'event',
        'registration_date',
    ]

    search_fields = [
        'full_name',
        'email',
        'event__title',
    ]

    readonly_fields = [
        'registration_date',
        'ip_address',
        'user_agent',
    ]

    fieldsets = (
        ('Événement', {
            'fields': ('event', 'status')
        }),
        ('Informations du participant', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Détails de l\'inscription', {
            'fields': ('number_of_participants', 'special_requests')
        }),
        ('Métadonnées', {
            'fields': ('registration_date', 'confirmation_date', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )

    def total_price_display(self, obj):
        if obj.total_price > 0:
            return f"{obj.total_price} €"
        return "Gratuit"

    total_price_display.short_description = 'Prix total'

    actions = ['confirm_registrations', 'cancel_registrations']

    def confirm_registrations(self, request, queryset):
        for registration in queryset:
            registration.confirm_registration()
        self.message_user(request, f"{queryset.count()} inscriptions confirmées.")

    confirm_registrations.short_description = "Confirmer les inscriptions sélectionnées"

    def cancel_registrations(self, request, queryset):
        for registration in queryset:
            registration.cancel_registration()
        self.message_user(request, f"{queryset.count()} inscriptions annulées.")

    cancel_registrations.short_description = "Annuler les inscriptions sélectionnées"

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['subscribed_at', 'ip_address']

# admin.py
@admin.register(EventAlertSubscription)
class EventAlertSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'get_location_display', 'is_active', 'subscribed_at']
    list_filter = ['location', 'is_active', 'subscribed_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['subscribed_at', 'ip_address', 'token']
    list_editable = ['is_active']

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'location', 'start_date', 'is_featured', 'is_upcoming']
    list_filter = ['event_type', 'location', 'is_featured', 'start_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_date'
    list_editable = ['is_featured']

# Customisation de l'admin
admin.site.site_header = "Église Missionnaire Propulsion - Administration"
admin.site.site_title = "Admin Propulsion"
admin.site.index_title = "Tableau de bord"