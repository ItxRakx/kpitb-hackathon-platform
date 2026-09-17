import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kpitb_hackathon.settings")

application = get_wsgi_application()
