"""
Django settings for goweb project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
#DEBUG = False

TEMPLATE_DEBUG = True
#TEMPLATE_DEBUG = False
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cron',
    'debug_toolbar',
    'bootstrapform',
    'gomail',
    'logging',
    'goview',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

CRON_CLASSES = [
    "goview.cron.UpdateCronJob",
]

ROOT_URLCONF = 'goweb.urls'

WSGI_APPLICATION = 'goweb.wsgi.application'

ADMINS = (('Fridolin Pokorny', 'fpokorny@redhat.com'))


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': BASE_DIR + '/mysql.conf',
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Prague'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = BASE_DIR + '/static/'
STATIC_URL = '/static/'

# email settings
EMAIL_HOST = 'smtp.server'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'gofed-web@smtp-server'
EMAIL_HOST_PASSWORD = 'yoursecretpassword'
DEFAULT_FROM_EMAIL = 'gofed-web@smtp-server'
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False

REPO_PATH = BASE_DIR + '/cache/'
GOLANG_REPOS = BASE_DIR + '/golang.repos'

# Max number of entries in a response
MAX_REPLY_COUNT = 100

