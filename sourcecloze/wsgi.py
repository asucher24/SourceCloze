"""
WSGI config for sourcecloze project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import sys
import site

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_DIR = os.path.join(BASE_DIR, 'sourceclozeenv/')
# Add the site-packages of the chosen virtualenv to work with
# site.addsitedir(BASE_DIR+'/sourceclozeenv/local/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append(BASE_DIR)
sys.path.append(VENV_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sourcecloze.settings")

# Activate your virtual env
activate_env=os.path.expanduser(os.path.join(VENV_DIR, "bin/activate_this.py"))
exec(open(activate_env).read(), {'__file__': activate_env})


application = get_wsgi_application()

from sourcecloze.settings_base import SU_UNAME, SU_NAME, SU_MAIL, SU_PW
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
user, created = User.objects.get_or_create(
    username=SU_UNAME,
    )
print("Got user: ", user)
print("Created: ", created)
if created:
    user.email=SU_MAIL
    user.first_name=SU_NAME[0]
    user.last_name=SU_NAME[1]
    user.set_password(SU_PW)
    user.is_active=True
    user.is_staff=True
    user.is_superuser=True
    # user.set_password(SU_PW)
    user.save()

from sourcecloze.settings_base import DEFAULT_FORBIDDEN_REGEX_FILE
from poll_api.models import ForbiddenExecText
import json, re
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(BASE_DIR, DEFAULT_FORBIDDEN_REGEX_FILE)

data = {}
with open(FILE, 'r', encoding="utf8") as f:
    data = json.loads(re.sub("//.*","",f.read(),flags=re.MULTILINE))
for (lang, regex_list) in data.items():
    for regex in regex_list:
        item, created = ForbiddenExecText.objects\
            .get_or_create(language=lang, regex=regex)
        if created:
            item.save()