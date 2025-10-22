from pathlib import Path
import os
import dj_database_url

# Chemins de base
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Sécurité / Debug via variables d'environnement ---
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me-in-prod")

# --- Hosts/CSRF (Render) ---
ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".onrender.com"]
render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_host:
    ALLOWED_HOSTS.append(render_host)

# CSRF exige les schémas complets
CSRF_TRUSTED_ORIGINS = ["https://*.onrender.com"]
if render_host:
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
        "DIRS": [BASE_DIR / "templates"],  # répertoire de templates global
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
# Utilise DATABASE_URL (Postgres Render) si présent, sinon SQLite local.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=bool(os.getenv("RENDER", "")),  # SSL pour Render
    )
}

# --- Internationalisation ---
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# --- Fichiers statiques ---
# /static = URL ; sources dans BASE_DIR/static ; collectstatic vers BASE_DIR/staticfiles
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]       # (CSS/JS/images source)
STATIC_ROOT = BASE_DIR / "staticfiles"         # (destination collectstatic)

# WhiteNoise (compression, SANS manifest pour éviter l'erreur de fichier manquant)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"
    },
}

# --- Sécurité derrière proxy HTTPS (Render) ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

# --- Divers ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
