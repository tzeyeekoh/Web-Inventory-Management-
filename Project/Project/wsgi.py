"""
WSGI config for Project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os, sys
sys.path.append('/opt/djangostack-3.0.8-0/apps/django/django_projects/Project')
os.environ.setdefault("PYTHON_EGG_CACHE", "/opt/djangostack-3.0.8-0/apps/django/django_projects/Project/egg_cache")


from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')

application = get_wsgi_application()
