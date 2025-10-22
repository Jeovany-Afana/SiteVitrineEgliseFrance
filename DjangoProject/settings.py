from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Sécurité / Debug via variables d'environnement ---
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me-in-prod")

# Render fournit RENDER_EXTERNAL_HOSTNAME -> on l’autorise
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_host:
    ALLOWED_HOSTS.append(render_host)
    # évite les erreurs CSRF en prod
    CSRF_TRUSTED_ORIGINS = [f"https://{render_host}"]

# --- Apps ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'EcoleBiblique.apps.EcolebibliqueConfig',
]

# --- Middlewares (ajout WhiteNoise juste après SecurityMiddleware) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # << IMPORTANT pour /static en prod
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DjangoProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # tu l'avais déjà
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'DjangoProject.wsgi.application'

# --- Base de données ---
# Utilise DATABASE_URL si présent (Postgres Render), sinon SQLite local
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=bool(os.getenv("RENDER", "")),
    )
}

# --- Internationalisation (tu peux passer en fr-fr si tu veux) ---
LANGUAGE_CODE = 'en-us'   # 'fr-fr' si besoin
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Fichiers statiques ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # ton dossier source (CSS/JS/images)
STATIC_ROOT = BASE_DIR / 'staticfiles'    # dossier de sortie pour collectstatic

# Django 4.2+ / 5.x : API STORAGES (WhiteNoise compression + manifest)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Conseillé derrière proxy HTTPS (Render)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
