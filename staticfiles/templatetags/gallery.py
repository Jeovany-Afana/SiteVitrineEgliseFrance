# ton_app/templatetags/gallery.py
import json
from django import template
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.safestring import mark_safe

register = template.Library()
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")

def _collect(prefix: str):
    # prefix du type "images/ecolePrimaire"
    urls = []
    try:
        dirs, files = staticfiles_storage.listdir(prefix)
    except Exception:
        return urls  # retourne vide si le dossier n’existe pas
    # fichiers du dossier courant
    for f in files:
        if f.lower().endswith(IMAGE_EXTS):
            urls.append(staticfiles_storage.url(f"{prefix}/{f}"))
    # descente récursive dans les sous-dossiers
    for d in dirs:
        urls += _collect(f"{prefix}/{d}")
    return urls

@register.simple_tag
def images_in(prefix: str):
    """
    Retourne un JSON (safe) de toutes les URLs d’images trouvées
    sous le dossier statique `prefix` (ex: 'images/ecolePrimaire').
    Compatible ManifestStaticFilesStorage (URLs hashées).
    """
    prefix = prefix.strip("/")
    urls = _collect(prefix)
    urls.sort()  # tri alpha simple
    return mark_safe(json.dumps(urls))
