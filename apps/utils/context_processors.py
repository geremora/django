from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured


def settings(request):
    """
    Adds the settings specified in settings.TEMPLATE_VISIBLE_SETTINGS to
    the request context.
    """
    new_settings = {}
    for attr in django_settings.TEMPLATE_VISIBLE_SETTINGS:
        try:
            new_settings[attr] = getattr(django_settings, attr)
        except AttributeError:
            m = "TEMPLATE_VISIBLE_SETTINGS: '{0}' does not exist".format(attr)
            raise ImproperlyConfigured(m)

    return new_settings
