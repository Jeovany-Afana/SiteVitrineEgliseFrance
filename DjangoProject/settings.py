from pathlib import Path
import os
import dj_database_url

# --- Chemins de base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Debug / Secret (pilotés par variables d'env) ---
# En prod sur Render : DJANGO_DEBUG=False ; SECRET_KEY défini dans le Dashboard
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me-in-prod")

# --- Hosts / CSRF (inclut Render) ---
ALLOWED_HOSTS = [".onrender.com"]
if DEBUG:
    # pratique pour tests locaux si tu remets DJANGO_DEBUG=True
    ALLOWED_HOSTS += ["localhost", "127.0.0.1", "[::1]", "0.0.0.0"]

CSRF_TRUSTED_ORIGINS = ["https://*.onrender.com"]
render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_host:
    ALLOWED_HOSTS.append(render_host)
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_host}")

# --- Applications ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "EcoleBiblique.apps.EcolebibliqueConfig",
]

# --- Middlewares (WhiteNoise juste après SecurityMiddleware) ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # sert les /static en prod
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "DjangoProject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "DjangoProject.wsgi.application"

# --- Base de données ---
# Sur Render : DATABASE_URL est fourni (Postgres). En local, SQLite.
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,  # SSL pour Postgres Render
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Internationalisation ---
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# --- Fichiers statiques ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]   # tes sources (CSS/JS/images)
STATIC_ROOT = BASE_DIR / "staticfiles"     # collectstatic en prod

# Stockage statique : compression WhiteNoise, SANS manifest (évite les erreurs de refs manquantes)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# --- Sécurité derrière proxy HTTPS (Render) ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
