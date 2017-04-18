# Django settings for casp project.

import os
from os.path import abspath, basename, dirname, join, normpath

from configurations import Configuration, values

import logging
logger = logging.getLogger(__name__)


class Common(Configuration):

    DEBUG = True
    TEMPLATE_DEBUG = DEBUG

    ENVIRONMENT = values.Value(environ_prefix=None, default='development')

    # Make this unique, and don't share it with anybody.
    # CONFIG.get('SECRET_KEY', 'PleaseDontTellEve')
    SECRET_KEY = values.SecretValue(environ_prefix=None)

    # Absolute filesystem path to the Django project directory:
    DJANGO_ROOT = dirname(abspath(__file__))

    # Absolute filesystem path to the top-level project folder:
    SITE_ROOT = dirname(DJANGO_ROOT)

    # Site name:
    SITE_NAME = basename(DJANGO_ROOT)

    # Database Settings
    DATABASES = values.DatabaseURLValue(
        'sqlite:///{}'.format(os.path.join(SITE_ROOT, 'db.sqlite3')))

    # Get the latest head commit
    HEAD_COMMIT_ID = os.environ.get('HEAD_COMMIT_ID', 'BAD_HEAD_COMMIT')[:15]
    TEMPLATE_VISIBLE_SETTINGS = ('HEAD_COMMIT_ID',)

    ALLOWED_HOSTS = [
        'localhost',
        'casp-staging.herokuapp.com',
        'casp-production.herokuapp.com'
    ]

    ADMINS = (
        ('Casp', 'casp@ml42.com'),
        ('Gerardo','geremora@gmail.com'),
        ('Francisco','torlanco@gmail.com '),
    )

    QUALITY_ASSURANCE = [
      #  'ihquinones@casp.pr.gov'
      'geremora@gmail.com',
      'torlanco@gmail.com',
      'casp@ml42.com'
    ]

    MANAGERS = ADMINS

    # Local time zone for this installation. Choices can be found here:
    # http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
    # although not all choices may be available on all operating systems.
    # In a Windows environment this must be set to your system time zone.
    TIME_ZONE = 'America/Puerto_Rico'

    # Language code for this installation. All choices can be found here:
    # http://www.i18nguy.com/unicode/language-identifiers.html
    LANGUAGE_CODE = 'en-us'

    SITE_ID = 1

    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = True

    # If you set this to False, Django will not format dates, numbers and
    # calendars according to the current locale.
    USE_L10N = True

    # If you set this to False, Django will not use timezone-aware datetimes.
    USE_TZ = True

    # Absolute filesystem path to the directory that will hold user-uploaded files.
    # Example: "/home/media/media.lawrence.com/media/"
    MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))

    # URL that handles the media served from MEDIA_ROOT. Make sure to use a
    # trailing slash.
    # Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
    MEDIA_URL = '/media/'

    # Absolute path to the directory static files should be collected to.
    # Don't put anything in this directory yourself; store your static files
    # in apps' "static/" subdirectories and in STATICFILES_DIRS.
    # Example: "/home/media/media.lawrence.com/static/"
    STATIC_ROOT = ''

    # URL prefix for static files.
    # Example: "http://media.lawrence.com/static/"
    STATIC_URL = '/static/'

    # Additional locations of static files
    STATICFILES_DIRS = (
        # Put strings here, like "/home/html/static" or "C:/www/django/static".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
        normpath(join(SITE_ROOT, 'static')),
    )

    # List of finder classes that know how to find static files in
    # various locations.
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

    BRUNCH_DIR = join(SITE_ROOT, 'frontend')

    # Amazon s3 configuration

    # os.environ.get('AWS_ACCESS_KEY_ID', CONFIG['AWS_ACCESS_KEY_ID'])
    AWS_ACCESS_KEY_ID = values.Value(environ_prefix=None)
    # os.environ.get('AWS_SECRET_ACCESS_KEY', CONFIG['AWS_SECRET_ACCESS_KEY'])
    AWS_SECRET_ACCESS_KEY = values.Value(environ_prefix=None)

    # 'com-mlstudiopr-casp-app-staging', 'com-mlstudiopr-casp-app-production'
    AWS_STATIC_BUCKET_NAME = values.Value(environ_prefix=None)
    # 'com-mlstudiopr-casp-uploads-staging', 'com-mlstudiopr-casp-uploads-production'
    AWS_STORAGE_BUCKET_NAME = values.Value(environ_prefix=None)
    AWS_MEDIA_BUCKET_NAME = values.Value(environ_prefix=None)

    # List of callables that know how to import templates from various sources.
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )

    MIDDLEWARE_CLASSES = (
        'django.middleware.cache.UpdateCacheMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.cache.FetchFromCacheMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.transaction.TransactionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'reversion.middleware.RevisionMiddleware',
    )

    ROOT_URLCONF = 'casp.urls'

    # Python dotted path to the WSGI application used by Django's runserver.
    WSGI_APPLICATION = 'casp.wsgi.application'

    TEMPLATE_DIRS = (
        # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
        # Always use forward slashes, even on Windows.
        # Don't forget to use absolute paths, not relative paths.
        normpath(join(SITE_ROOT, 'templates')),
    )

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'django.core.context_processors.tz',
        'django.core.context_processors.request',
        'django.contrib.messages.context_processors.messages',
        'apps.utils.context_processors.settings'
    )

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        'django.contrib.formtools',

        # Third-party
        'django_extensions',
        'gunicorn',
        'south',
        'bootstrapform',
        'reversion',
        'django_fsm',
        'opbeat.contrib.django',
        'bootstrap3',
        'django_tables2',
        'djrill',
        'widget_tweaks',
        # 'django_bootstrap_calendar',

        # Local apps
        'apps.django_popup_add',
        'apps.cases',
        'apps.contacts',
        'apps.profiles',
        'apps.events',
        'apps.meetings',
        'apps.notes',
        'apps.bugs',
        'apps.utils',
        'apps.reports',
        'apps.perms',
        'apps.documents',
    )

    # OPBEAT configuration
    ORGANIZATION_ID = values.Value(environ_prefix=None)
    APP_ID = values.Value(environ_prefix=None)
    SECRET_TOKEN = values.SecretValue(environ_prefix=None)

    OPBEAT = {
        'ORGANIZATION_ID': ORGANIZATION_ID,
        'APP_ID': APP_ID,
        'SECRET_TOKEN': SECRET_TOKEN,
    }

    # User mode
    AUTH_USER_MODEL = 'profiles.CaspUser'

    # Auth
    LOGIN_REDIRECT_URL = 'case_list'

    # debug toolbar
    INTERNAL_IPS = ('127.0.0.1',)
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }

    # Email setup
    # EMAIL_SUBJECT_PREFIX = '[{}] '.format(SITE_NAME.upper())
    # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # CONFIG.get('EMAIL_HOST')
    # EMAIL_HOST = values.Value(environ_prefix=None)
    # CONFIG.get('EMAIL_HOST_USER')
    # EMAIL_HOST_USER = values.Value(environ_prefix=None)
    # CONFIG.get('EMAIL_HOST_PASSWORD')
    # EMAIL_HOST_PASSWORD = values.Value(environ_prefix=None)
    # CONFIG.get('EMAIL_PORT')
    # EMAIL_PORT = values.Value(environ_prefix=None)
    # EMAIL_USE_TLS = True

    # Mandrill settings
    MANDRILL_API_KEY = values.SecretValue(environ_prefix=None)
    EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
    DEFAULT_FROM_EMAIL = values.Value(environ_prefix=None)
    SERVER_EMAIL = values.Value(environ_prefix=None)

    # Celery settings
    BROKER_URL = values.Value(environ_prefix=None, default='redis://localhost//')

    #: Only add pickle to this list if your broker is secured
    #: from unwanted access (see userguide/security.html)
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'

    # Logging configuration adapted from: http://stackoverflow.com/a/5806903
    LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(pathname)s:%(lineno)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'django.utils.log.NullHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'log_file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(SITE_ROOT, 'logs/django.log'),
                'maxBytes': '16777216',
                'formatter': 'verbose'
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler',
                'include_html': True,
            }
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': True,
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
            'apps': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
        'root': {
            'handlers': ['console'],
            'level': LOG_LEVEL
        },
    }

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
        }
    }
    CACHE_MIDDLEWARE_ALIAS = 'default'
    CACHE_MIDDLEWARE_SECONDS = 30
    CACHE_MIDDLEWARE_KEY_PREFIX = ''


class Development(Common):
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG

    PROTOCOL = 'http'

    QUALITY_ASSURANCE = [
        'geremora@gmail.com'
    ]

    MIDDLEWARE_CLASSES = Common.MIDDLEWARE_CLASSES + (
        'apps.utils.middleware.ProfileMiddleware',
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    INSTALLED_APPS = Common.INSTALLED_APPS + (
        'storages',
        'debug_toolbar'
    )

    SOUTH_TESTS_MIGRATE = False


class Staging(Common):

    MIDDLEWARE_CLASSES = Common.MIDDLEWARE_CLASSES + (
        'djangosecure.middleware.SecurityMiddleware',
    )

    INSTALLED_APPS = Common.INSTALLED_APPS + (
        'djangosecure',
        'storages',
    )

    QUALITY_ASSURANCE = [
        'geremora@gmail.com',
        'casp@ml42.com',
        'torlanco@gmail.com'
    ]

    # django-secure
    PROTOCOL = 'https'
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 15
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_FRAME_DENY = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Storage settings
    STATIC_URL = 'https://s3.amazonaws.com/com-mlstudiopr-casp-app-staging/'
    MEDIA_URL = 'https://s3.amazonaws.com/com-mlstudiopr-casp-uploads-staging/'

    DEFAULT_FILE_STORAGE = 'casp.s3utils.MediaRootS3BotoStorage'
    STATICFILES_STORAGE = 'casp.s3utils.StaticRootS3BotoStorage'


class Production(Common):

    MIDDLEWARE_CLASSES = Common.MIDDLEWARE_CLASSES + (
        'djangosecure.middleware.SecurityMiddleware',
    )

    INSTALLED_APPS = Common.INSTALLED_APPS + (
        'djangosecure',
        'storages',
    )

    # django-secure
    PROTOCOL = 'https'
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 15
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_FRAME_DENY = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Storage settings
    STATIC_URL = 'https://s3.amazonaws.com/com-mlstudiopr-casp-app-production/'
    MEDIA_URL = 'https://s3.amazonaws.com/com-mlstudiopr-casp-uploads-production/'

    DEFAULT_FILE_STORAGE = 'casp.s3utils.MediaRootS3BotoStorage'
    STATICFILES_STORAGE = 'casp.s3utils.StaticRootS3BotoStorage'


def show_toolbar(request):
    return True

SHOW_TOOLBAR_CALLBACK = show_toolbar

from django.db.backends.postgresql_psycopg2.base import DatabaseOperations, DatabaseWrapper

def lookup_cast(self, lookup_type):
    if lookup_type in('icontains', 'istartswith','iexact'):
        return "UPPER(unaccent(%s::text))"
    else:
        return super(DatabaseOperations, self).lookup_cast(lookup_type)

def patch_unaccent():
    DatabaseOperations.lookup_cast = lookup_cast
    DatabaseWrapper.operators['icontains'] = 'LIKE UPPER(unaccent(%s))'
    DatabaseWrapper.operators['istartswith'] = 'LIKE UPPER(unaccent(%s))'
    print 'Unaccent patch'

patch_unaccent()



# form error message override
from django.forms import Field
from django.utils.translation import ugettext_lazy

Field.default_error_messages = {
    'required': ugettext_lazy("Este campo es requerido"),
}