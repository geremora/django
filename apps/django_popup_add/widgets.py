from django import forms
from django.template.loader import render_to_string
from django.contrib.admin.widgets import FilteredSelectMultiple
import logging
logger = logging.getLogger(__name__)

class PopUpBaseWidget(object):
    def __init__(self, model=None, template='addnew.html', *args, **kwargs):
        self.model = model
        self.template = template
        super(PopUpBaseWidget, self).__init__(*args, **kwargs)

    def render(self, name, *args, **kwargs):
        html = super(PopUpBaseWidget, self).render(name, *args, **kwargs)

        if not self.model:
            self.model = name

        popupplus = render_to_string(
            self.template,
            {'field': name, 'model': self.model})

        if (self.model == 'Contact') or (self.model == 'Case'):
            return html
        else:
            return html + popupplus


class FilteredMultipleSelectWithPopUp(PopUpBaseWidget, FilteredSelectMultiple):
    pass


class MultipleSelectWithPopUp(PopUpBaseWidget, forms.SelectMultiple):
    pass


class SelectWithPopUp(PopUpBaseWidget, forms.Select):
    pass


class SelectAjaxWithPopUp(PopUpBaseWidget, forms.TextInput):
    def render(self, name, *args, **kwargs):
        kwargs['attrs'].update({'class': 'select-with-ajax'})
        return super(SelectAjaxWithPopUp, self).render(name, *args, **kwargs)


class SelectAjaxMultipleWithPopUp(PopUpBaseWidget, forms.TextInput):
    def render(self, name, *args, **kwargs):
        kwargs['attrs'].update({'class': 'contact-list-ajax'})
        return super(SelectAjaxMultipleWithPopUp, self).render(name, *args, **kwargs)


class SelectAjaxCaseTypeFilterWithPopUp(PopUpBaseWidget, forms.TextInput):
    def render(self, name, *args, **kwargs):
        kwargs['attrs'].update({'class': 'contact-type-list-ajax'})

        return super(SelectAjaxCaseTypeFilterWithPopUp, self).render(name, *args, **kwargs)

class SelectAjaxCaseFilterWithPopUp(PopUpBaseWidget, forms.TextInput):
    def render(self, name, *args, **kwargs):
        kwargs['attrs'].update({'class': 'case-list-ajax'})
        return super(SelectAjaxCaseFilterWithPopUp, self).render(name, *args, **kwargs)
