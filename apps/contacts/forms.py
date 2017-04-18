# -*- coding: utf-8 -*-

from django import forms
from django.forms.util import ErrorList
from .models import Contact
import logging
logger = logging.getLogger(__name__)

class ContactForm(forms.ModelForm):
    '''
    Sub-class ModelForm to change default labels
    '''

    class Meta:
        model = Contact
        fields = ['contact_type', 'head_agency' ,'institutional_name', 'first_name', 'last_name', 'related_instutution', 'phone1', 'phone2', 'address', 'city', 'state', 'zip_code', 'notes']
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)

        self.fields['institutional_name'].label = 'Nombre insitucional'
        self.fields['first_name'].label = 'Nombre'
        self.fields['last_name'].label = 'Apellidos'
        self.fields['related_instutution'].label = u'Relacionado a institución'
        self.fields['phone1'].label = u'Teléfono 1'
        self.fields['phone2'].label = u'Teléfono 2'
        self.fields['address'].label = u'Dirección postal'
        self.fields['city'].label = 'Ciudad'
        self.fields['state'].label = 'Estado'
        self.fields['zip_code'].label = u'Código postal'
        self.fields['contact_type'].label = 'Tipo de contacto'
        self.fields['head_agency'].label = 'Jefe de Agencia'
        self.fields['notes'].label = 'Notas'

        

    def clean(self, *args, **kwargs):
        cleaned_data = super(ContactForm, self).clean(*args, **kwargs)

        institutional_name = cleaned_data['institutional_name']
        first_name = cleaned_data['first_name']
        last_name = cleaned_data['last_name']

        if institutional_name == '' and (first_name == '' or last_name == ''):
            required_error = u'Este campo es requerido.'

            if institutional_name == '':
                self._errors['institutional_name'] = ErrorList([required_error])

            if first_name == '':
                self._errors['first_name'] = ErrorList([required_error])

            if last_name == '':
                self._errors['last_name'] = ErrorList([required_error])

        return cleaned_data


