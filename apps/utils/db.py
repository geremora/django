from django.db import models

from lxml.html.clean import clean_html
from lxml.etree import XMLSyntaxError

# South support
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], [r"^apps\.utils\.db\.HTMLField"])


class HTMLField(models.TextField):
    def pre_save(self, model_instance, add):
        value = super(HTMLField, self).pre_save(model_instance, add)

        try:
            return clean_html(value)
        except XMLSyntaxError:
            return ''
