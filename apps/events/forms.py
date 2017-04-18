# -*- coding: utf-8 -*-

from django import forms
from django.utils.timezone import now

from .models import IncomingEvent, OutgoingEvent, EventType
from ..utils.widgets import DateTimePickerInput

from ..django_popup_add.widgets import (SelectAjaxWithPopUp)

from datetime import datetime, date

import logging
logger = logging.getLogger(__name__)


# class OutgoingEventCreationStepOneForm(forms.ModelForm):
#     class Meta:
#         model = OutgoingEvent
#         fields = ('event_type', 'comments', 'attached_file',
#                   'requires_terms', 'date_terms_expiration',
#                   'requires_acceptance', 'accepted',
#                   'date_emitted', 'requires_notification',
#                   'date_notification')
#         widgets = {
#             'date_terms_expiration': DateTimePickerInput(),
#             'date_emitted': DateTimePickerInput(),
#             'date_notification': DateTimePickerInput()
#         }

#     def __init__(self, *args, **kwargs):
#         self.with_attachment = kwargs.pop('with_attachment', False)
#         super(OutgoingEventCreationStepOneForm, self).__init__(*args, **kwargs)
     

#         self.fields['event_type'].label = 'Tipo de evento'
#         self.fields['event_type'].queryset = EventType.objects.filter(direction='out').exclude(allowedCaseClosed=False)
#         self.fields['comments'].label = 'Comentarios'
#         self.fields['attached_file'].label = 'Archivo'
#         self.fields['requires_terms'].label = 'Tiene plazo para cumplir'
#         self.fields['date_terms_expiration'].label = u'Expiración del plazo'
#         self.fields['date_emitted'].label = u'Fecha de emisión'
#         self.fields['requires_notification'].label = u'Requiere notificación'
#         self.fields['date_notification'].label = u'Fecha de notificación'
#         self.fields['requires_acceptance'].label = u'Require decisión'
#         self.fields['accepted'].label = 'Ha lugar'

#     def clean_attached_file(self):
#         data = self.cleaned_data['attached_file']

#         if self.with_attachment and data is None:
#             raise forms.ValidationError('Este campo es requerido.')

#         return data


# class OutgoingEventCreationStepTwoForm(forms.ModelForm):
#     class Meta:
#         model = OutgoingEvent
#         fields = ('document_content',)
#         widgets = {
#             'document_content': forms.Textarea(attrs={'class': 'wysihtml5'})
#         }

#     def __init__(self, *args, **kwargs):
#         self.with_attachment = kwargs.pop('with_attachment', False)
#         super(OutgoingEventCreationStepTwoForm, self).__init__(*args, **kwargs)

#         self.fields['document_content'].label = 'Documento'


class IncomingEventCreationForm(forms.ModelForm):
    attached_file = forms.CharField(required=False,
            widget=forms.TextInput(attrs={'class': 's3direct-upload'}))

    class Meta:
        model = IncomingEvent
        fields = ('event_type', 'comments', 'generate_by','party', 'date_emitted',
                  'requires_terms', 'date_terms_expiration',
                  'requires_acceptance', 'accepted', 'requires_notification',
                   'related_event')
        widgets = {
            'date_terms_expiration': DateTimePickerInput(),
            'date_emitted': DateTimePickerInput(attrs={  
            'class': 'date_emitted',
            'placeholder': 'myCustomPlaceholder'}),  
            'generate_by': SelectAjaxWithPopUp('Contact')
        }


    def __init__(self, *args, **kwargs):
        super(IncomingEventCreationForm, self).__init__(*args, **kwargs)

        self.fields['comments'].required = False

        self.fields['event_type'].label = 'Tipo de evento'
        if self.initial['case'].was_closed():
            self.fields['event_type'].queryset = EventType.objects.filter(direction='in').exclude(allowedCaseClosed=False)
        self.fields['comments'].label = 'Comentarios'
        self.fields['attached_file'].label = 'Archivo'
        self.fields['requires_terms'].label = 'Tiene plazo para cumplir'
        self.fields['date_terms_expiration'].label = u'Plazo vence el'
        self.fields['requires_notification'].label = u'Requiere notificación'
        self.fields['requires_acceptance'].label = u'Require decisión'
        self.fields['date_emitted'].label = u'Fecha de emisión'
        self.fields['date_emitted'].initial = date.today()
        self.fields['accepted'].label = 'Ha lugar'
        self.fields['party'].label = 'Parte que radica'
        self.fields['generate_by'].label = 'Radicado por'
        self.fields['related_event'].queryset = OutgoingEvent.objects.filter(cases__in=[self.initial['case'].id])
        self.fields['related_event'].label = 'Relacionado con'
        self.fields['related_event'].label_from_instance = lambda obj: "%s (%s)" % (obj.event_type, obj.date_created.strftime('%m/%d/%Y'))


    def clean_date_terms_expiration(self):
        requires_terms = self.cleaned_data.get('requires_terms')
        date_terms_expiration = self.cleaned_data.get('date_terms_expiration')

        if requires_terms and date_terms_expiration is None:
            raise forms.ValidationError('Fecha requerida')

        return date_terms_expiration

    def save(self, *args, **kwargs):
        event = super(
            IncomingEventCreationForm, self).save(commit=False,
                                                  *args, **kwargs)

        event.created_by = self.initial['created_by']
        event.attached_file = self.cleaned_data['attached_file']
        event.save()

        event.cases.add(*self.initial['case'].container.get_cases())
        #event.cases.add(self.initial['case'])

        return event


class OutgoingEventCreationForm(forms.ModelForm):
    attached_file = forms.CharField(required=False,
            widget=forms.TextInput(attrs={'class': 's3direct-upload'}))

    class Meta:
        model = OutgoingEvent
        fields = ('event_type', 'comments', 'generate_by', 'party','date_emitted',
                  'requires_terms', 'date_terms_expiration',
                  'requires_acceptance', 'accepted',
                   'requires_notification',
                  'date_notification', 'related_event')
        widgets = {
            'date_terms_expiration': DateTimePickerInput(),
            'date_emitted': DateTimePickerInput(),
            'date_notification': DateTimePickerInput(),
            'attached_file': forms.FileInput(attrs={'class': 's3direct-upload'}),
            'generate_by': SelectAjaxWithPopUp('Contact')
        }

    def __init__(self, *args, **kwargs):
        super(OutgoingEventCreationForm, self).__init__(*args, **kwargs)
    
       
        self.fields['comments'].required = False

        self.fields['event_type'].label = 'Tipo de evento'
        if self.initial['case'].was_closed():
            self.fields['event_type'].queryset = EventType.objects.filter(direction='out').exclude(allowedCaseClosed=False)
        self.fields['comments'].label = 'Comentarios'
        self.fields['attached_file'].label = 'Archivo'
        self.fields['requires_terms'].label = 'Tiene plazo para cumplir'
        self.fields['date_terms_expiration'].label = u'Plazo vence el'
        self.fields['requires_acceptance'].label = u'Require decisión'
        self.fields['requires_notification'].label = u'Requiere notificación'
        self.fields['date_emitted'].label = u'Fecha de emisión'
        self.fields['date_emitted'].initial = date.today()
        self.fields['date_notification'].label = u'Fecha de notificación'
        self.fields['accepted'].label = 'Ha lugar'
        self.fields['party'].label = 'Parte que radica'
        self.fields['generate_by'].label = 'Radicado por'
        self.fields['related_event'].queryset = IncomingEvent.objects.filter(cases__in=[self.initial['case'].id])
        self.fields['related_event'].label = 'Relacionado con'
        self.fields['related_event'].label_from_instance = lambda obj: "%s (%s)" % (obj.event_type, obj.date_created.strftime('%m/%d/%Y'))


    def clean_date_terms_expiration(self):
        requires_terms = self.cleaned_data.get('requires_terms')
        date_terms_expiration = self.cleaned_data.get('date_terms_expiration')

        if requires_terms and date_terms_expiration is None:
            raise forms.ValidationError('Fecha requerida')

        return date_terms_expiration

    def save(self, *args, **kwargs):
        event = super(
            OutgoingEventCreationForm, self).save(commit=False,
                                                  *args, **kwargs)

        event.created_by = self.initial['created_by']
        event.attached_file = self.cleaned_data['attached_file']
        event.save()

        event.cases.add(*self.initial['case'].container.get_cases_ids())

        return event


class UpdateOutgoingEventAcceptanceForm(forms.ModelForm):
    class Meta:
        model = OutgoingEvent
        fields = ('requires_acceptance', 'accepted')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UpdateOutgoingEventAcceptanceForm,
              self).__init__(*args, **kwargs)

        self.fields['requires_acceptance'].label = u'Require decisión'
        self.fields['accepted'].label = 'Ha lugar'


class UpdateIncomingEventAcceptanceForm(forms.ModelForm):
    class Meta:
        model = IncomingEvent
        fields = ('requires_acceptance', 'accepted')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UpdateIncomingEventAcceptanceForm,
              self).__init__(*args, **kwargs)

        self.fields['requires_acceptance'].label = u'Require decisión'
        self.fields['accepted'].label = 'Ha lugar'


class IncomingEventUpdateObservingForm(forms.ModelForm):
    class Meta:
        model = IncomingEvent
        fields = ('observed_notes',)

    def __init__(self, *args, **kwargs):
        super(IncomingEventUpdateObservingForm, self).__init__(*args, **kwargs)

        self.fields['observed_notes'].required = True
        self.fields['observed_notes'].label = 'Notas'

    def save(self, *args, **kwargs):
        event = super(IncomingEventUpdateObservingForm,
                      self).save(commit=False, *args, **kwargs)

        event.date_observed = now()
        event.save()

        return event


class ImportedEventUpdateForm(forms.Form):
    event_type = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        self.initial_data = kwargs.pop('initial')

        event_type_choices = self.initial_data['event_type_choices']

        super(ImportedEventUpdateForm, self).__init__(*args, **kwargs)

        self.fields['event_type'].label = 'Tipo de evento'

        self.fields['event_type'].choices = [(e.id, e.name) for e in event_type_choices]
        self.fields['event_type'].choices.insert(0, ('', '-----'))

    def save(self, *args, **kwargs):
        new_event_type_id = self.cleaned_data['event_type']
        new_event_type = self.initial_data['event_type_choices'].get(pk=new_event_type_id)

        if new_event_type.direction == 'out':
            event = OutgoingEvent()
        elif new_event_type.direction == 'in':
            event = IncomingEvent()

        event.comments = self.instance.description
        event.event_type = new_event_type
        event.created_by = self.initial_data['created_by']
        event.save()
        event.cases.add(self.instance.case)

        event.date_created = self.instance.date_created
        event.save()

        self.instance.delete()

        return event


class OutgoingEventUpdateNotifyingForm(forms.ModelForm):
    class Meta:
        model = IncomingEvent
        fields = ('date_notification',)
        widgets = {
            'date_notification': DateTimePickerInput()
        }

    def __init__(self, *args, **kwargs):
        super(OutgoingEventUpdateNotifyingForm, self).__init__(*args, **kwargs)

        self.fields['date_notification'].required = True
        self.fields['date_notification'].label = u'Fecha de notificación'

    def save(self, *args, **kwargs):
        event = super(OutgoingEventUpdateNotifyingForm,
                      self).save(commit=False, *args, **kwargs)

        event.date_notification = self.instance.date_notification
        event.save()

        return event
