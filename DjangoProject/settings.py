from pathlib import Path

# --- Chemins de base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Mode dev local (aucun .env requis) ---
DEBUG = True
SECRET_KEY = "dev-secret-key-do-not-use-in-prod"

if DEBUG:
    SECURE_PROXY_SSL_HEADER = None

# --- Hosts / CSRF (local) ---
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "0.0.0.0"]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
]

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

# --- Middlewares (simple pour le local) ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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

# --- Base de données (SQLite local) ---
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

# --- Fichiers statiques (dev) ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]     # tes sources CSS/JS/images
STATIC_ROOT = BASE_DIR / "staticfiles"       # utile si tu fais collectstatic un jour

# Stockage statique simple pour le dev
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

# --- Sécurité (dev) ---
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
