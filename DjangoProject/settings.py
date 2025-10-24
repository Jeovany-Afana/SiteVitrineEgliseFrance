from pathlib import Path
import os
import dj_database_url

# === Chemins de base ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Détection auto de l'environnement ===
# Prod si Render/DATABASE_URL est présent, sinon Local (dev)
DATABASE_URL = (os.getenv("DATABASE_URL") or "").strip()
IS_RENDER = bool(os.getenv("RENDER") or os.getenv("RENDER_EXTERNAL_HOSTNAME"))
IS_PROD = bool(DATABASE_URL) or IS_RENDER

# === Debug / Secret ===
if IS_PROD:
    # Par défaut False en prod (mets DJANGO_DEBUG=True si tu veux débugger Render)
    DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
    # Mets une vraie clé dans le Dashboard Render (env var DJANGO_SECRET_KEY)
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "set-this-on-render")
else:
    DEBUG = True
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key-do-not-use-in-prod")

# === Hosts / CSRF ===
ALLOWED_HOSTS = []
CSRF_TRUSTED_ORIGINS = []

if IS_PROD:
    ALLOWED_HOSTS += [".onrender.com"]
    render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if render_host:
        ALLOWED_HOSTS.append(render_host)
        CSRF_TRUSTED_ORIGINS.append(f"https://{render_host}")
    CSRF_TRUSTED_ORIGINS += ["https://*.onrender.com"]
else:
    # Local (HTTP)
    ALLOWED_HOSTS += ["localhost", "127.0.0.1", "[::1]", "0.0.0.0"]
    CSRF_TRUSTED_ORIGINS += [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://0.0.0.0:8000",
    ]

# === Applications ===
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "EcoleBiblique.apps.EcolebibliqueConfig",
]

# === Middlewares (WhiteNoise OK en dev/prod) ===
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # sert /static en prod
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

# === Base de données ===
if IS_PROD and DATABASE_URL:
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

# === Internationalisation ===
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# === Fichiers statiques ===
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]      # sources CSS/JS/images
STATIC_ROOT = BASE_DIR / "staticfiles"        # destination collectstatic (prod)

# Stockage statique (simple en dev, compressé en prod)
if IS_PROD:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"
        },
    }
else:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }

# === Sécurité / Proxy HTTPS ===
if IS_PROD:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    # Active la redirection HTTPS uniquement si tu n'es pas en mode DEBUG sur Render
    SECURE_SSL_REDIRECT = not DEBUG
    CSRF_COOKIE_SECURE = not DEBUG
    SESSION_COOKIE_SECURE = not DEBUG
else:
    SECURE_PROXY_SSL_HEADER = None
    SECURE_SSL_REDIRECT = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
