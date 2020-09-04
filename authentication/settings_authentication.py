"""
Django settings for sourcecloze project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

from sourcecloze.settings_base import INSTALLED_APPS, TEMPLATES

# Do not edit the following lines
# Gitlab OAuth2 Settings for lib: social_djangos
LOGIN_REDIRECT_URL = "/views/"
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
AUTH_USER_MODEL = 'authentication.User'
SOCIAL_AUTH_USER_MODEL = 'authentication.User'
SOCIAL_AUTH_URL_NAMESPACE = 'auth:social'
INSTALLED_APPS += ['social_django']
TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'social_django.context_processors.backends',
    'social_django.context_processors.login_redirect'
]


######################################################################
####################### AUTHENTICATION SETTINGS ######################
######################################################################
########## GITLAB ##########
SOCIAL_AUTH_GITLAB_API_URL = 'https://gitlab.xyz.net/'
SOCIAL_AUTH_GITLAB_KEY = 'xxxxxxx'
SOCIAL_AUTH_GITLAB_SECRET = 'xxxxxxx'
AUTHENTICATION_BACKENDS += tuple(['social_core.backends.gitlab.GitLabOAuth2'])


########## OTHER ##########
# take a look into: https://python-social-auth.readthedocs.io/en/latest/backends/index.html#social-backends
# do not forget, to add buttons into view

# 'social_core.backends.open_id.OpenIdAuth',
# 'social_core.backends.google.GoogleOpenId',
# 'social_core.backends.google.GoogleOAuth2',
# 'social_core.backends.google.GoogleOAuth',
# 'social_core.backends.twitter.TwitterOAuth',
# 'social_core.backends.yahoo.YahooOpenId',
# ...


