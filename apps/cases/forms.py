# -*- coding: utf-8 -*-
import re

from django import forms

from ..django_popup_add.widgets import (SelectAjaxWithPopUp, SelectAjaxMultipleWithPopUp,
                                        SelectAjaxCaseTypeFilterWithPopUp, SelectAjaxCaseFilterWithPopUp)
from ..utils.widgets import DateTimePickerInput
from ..utils.forms import CommaSeparatedListField

from .models import Case, CaseContainer, ContactCaseRole, CaseCategory
from ..events.models import OutgoingEvent, EventType
from ..contacts.models import Contact, ContactRole
from django.shortcuts import get_object_or_404


import logging
logger = logging.getLogger(__name__)


class CaseCreationStepOneForm(forms.ModelForm):
    #contacts = CommaSeparatedListField(
     #   label='Otros contactos',
     #   widget=SelectAjaxMultipleWithPopUp('Contact'),
    #    required=False)
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = Case
        fields = (
            'case_type', 'plaintiff', 'defendant',
            'case_category', 'date_accepted', 'description', 'assigned_user')

        widgets = {
            'date_accepted': DateTimePickerInput(attrs={'class': 'form-control'}),
            'plaintiff': SelectAjaxWithPopUp(
                'Contact'),  # attrs={'data-contact-type': 3}),
            'defendant': SelectAjaxCaseTypeFilterWithPopUp(
                'Contact')  # attrs={'data-contact-type': 1})
        }

    def __init__(self, *args, **kwargs):
        super(CaseCreationStepOneForm, self).__init__(*args, **kwargs)

        self.fields['case_type'].label = 'Tipo de caso'
        self.fields['description'].label = 'Descripción'
        self.fields['defendant'].label = 'Promovido'
        self.fields['plaintiff'].label = 'Promovente'
        self.fields['case_category'].label = 'Materia'
        self.fields['date_accepted'].label = u'Fecha de radicación'
        self.fields['assigned_user'].queryset = \
        self.fields['assigned_user'].queryset.exclude(is_active=False).order_by('first_name')
        self.fields['description'].required = False



class BaseUpdateCaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BaseUpdateCaseForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        case = super(BaseUpdateCaseForm, self).save(*args, **kwargs)

        update_event_type = EventType.objects.get(name=u'Actualización')
        event = OutgoingEvent.objects.create(comments=self.update_comment,
                                             event_type=update_event_type,
                                             created_by=self.request.user,
                                             requires_notification=False)

        event.cases.add(*case.container.get_cases_ids())

        return case


class CaseUpdateTypeForm(BaseUpdateCaseForm):
    update_comment = u'Se actualizó el tipo de caso'

    class Meta:
        model = Case
        fields = ('case_type',)

    def __init__(self, *args, **kwargs):
        super(CaseUpdateTypeForm, self).__init__(*args, **kwargs)
        self.fields['case_type'].label = 'Tipo de caso'

    def save(self, *args, **kwargs):

        case_type = self.instance.case_type
        state = self.instance.state
        self.update_comment += u' a {}'.format(case_type.code.lower())

        if 'new' in state and case_type.code.lower() not in state:
            self.instance.state = '{}-new'.format(case_type.code.lower())

        case = super(CaseUpdateTypeForm, self).save(*args, **kwargs)

        return case

class CaseUpdateCaseCategoryForm(BaseUpdateCaseForm):
    update_comment = u'Se actualizó la materia del caso'

    class Meta:
        model = Case
        fields = ('case_category',)

    def __init__(self, *args, **kwargs):
        super(CaseUpdateCaseCategoryForm, self).__init__(*args, **kwargs)
        self.instance = kwargs.pop('instance')
        self.fields['case_category'].label = u'Materia'
        self.fields['case_category'].queryset = self.instance.case_type.case_category.all()

    def save(self, *args, **kwargs):

        previous_case_category = get_object_or_404(Case, pk=self.instance.pk).case_category

        self.update_comment += u' de {0} a {1}'.format(
            previous_case_category,
            self.instance.case_category
       )
        return super(CaseUpdateCaseCategoryForm, self).save(*args, **kwargs)

final_decision_choices = [('1',u'Se llegó a acuerdo total'), ('2', u'Se llegó a acuerdo parcial'),('3',u'No se llegó a acuerdo'), ]

class CaseRemoveCaseMediationForm(forms.Form):
    update_comment = u'Se termino la mediación del caso.'
   
    final_decision = forms.ChoiceField(choices = (final_decision_choices), required=True)
    final_notes_mediation = forms.CharField(widget=forms.Textarea, max_length=200, required=False)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        self.request = kwargs.pop('request', None)
        super(CaseRemoveCaseMediationForm, self).__init__(*args, **kwargs)
       
        self.fields['final_decision'].label = u'Decisión final'
        self.fields['final_notes_mediation'].label = 'Notas finales'

    def save(self, *args, **kwargs):
        final_notes_mediation = self.cleaned_data['final_notes_mediation']
        index_selected = int(self.cleaned_data['final_decision'])

        final_decision = final_decision_choices[index_selected][1]


        case = self.initial['case']
        case.mediation = False
        case.was_mediation = True
        case.save()


        self.update_comment += u' El resultado fue: {}.'.format(final_decision)

        if final_notes_mediation:
            self.update_comment += u' Comentarios: {}'.format(final_notes_mediation)
       
        update_event_type = EventType.objects.get(name=u'Actualización')

        event = OutgoingEvent.objects.create(comments=self.update_comment,
                                             event_type=update_event_type,
                                             created_by=self.request.user,
                                             requires_notification=False)

        event.cases.add(*self.initial['case'].container.get_cases_ids())


class CaseUpdateAssignedUserForm(BaseUpdateCaseForm):
    update_comment = u'Se actualizó empleado asignado al caso'

    class Meta:
        model = Case
        fields = ('assigned_user',)

    def __init__(self, *args, **kwargs):
        super(CaseUpdateAssignedUserForm, self).__init__(*args, **kwargs)
        self.fields['assigned_user'].label = 'Asignado a'
        self.fields['assigned_user'].queryset = \
        self.fields['assigned_user'].queryset.exclude(is_active=False).order_by('first_name')

    def save(self, *args, **kwargs):
        previous_assigned_user = get_object_or_404(Case, pk=self.instance.pk).assigned_user

        if previous_assigned_user:

            self.update_comment += u' de {0} {1} a {2} {3}'.format(
                previous_assigned_user.first_name, 
                previous_assigned_user.last_name,
                self.instance.assigned_user.first_name,
                self.instance.assigned_user.last_name
            )
        else:
            self.update_comment += u' a {0} {1}'.format(
                self.instance.assigned_user.first_name,
                self.instance.assigned_user.last_name)


        return super(CaseUpdateAssignedUserForm, self).save(*args, **kwargs)


class CaseContactCreateForm(forms.Form):
    update_comment = u'Se crea un nuevo contacto en el caso'
    contact = forms.ModelChoiceField(queryset = '', widget=SelectAjaxWithPopUp('Contact'))
    rol = forms.ModelChoiceField(queryset=ContactRole.objects.filter().exclude(id__in=[1,2]))

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        self.request = kwargs.pop('request', None)
        super(CaseContactCreateForm, self).__init__(*args, **kwargs)
        self.fields['contact'].label = 'Contacto'
        self.fields['rol'].label = 'Rol'

        self.fields['contact'].queryset = Contact.objects.filter().exclude(id__in=self.initial['case'].get_all_contacts(id_only=True))
       

    def save(self, *args, **kwargs):
         contact = self.cleaned_data['contact']
         rol = self.cleaned_data['rol']
         role = ContactCaseRole.objects.create(name=rol, case=self.initial['case'], contact=contact)
    
         role.save()

         self.update_comment += u' {0} - {1}'.format(
            contact.get_name(),
            rol.name)

         update_event_type = EventType.objects.get(name=u'Actualización')

         event = OutgoingEvent.objects.create(comments=self.update_comment,
                                             event_type=update_event_type,
                                             created_by=self.request.user,
                                             requires_notification=False)
         event.cases.add(*self.initial['case'].container.get_cases_ids())



class CaseUpdateContactForm(forms.Form):
    update_comment = u'Se actualizó un contacto del caso'
    contact = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))
    rol = forms.ModelChoiceField(queryset=ContactRole.objects.filter().exclude(id__in=[1,2]), required=False)
    active = forms.BooleanField(required=False)


    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        self.request = kwargs.pop('request', None)
        super(CaseUpdateContactForm, self).__init__(*args, **kwargs)

        self.fields['contact'].label = 'Contacto'
        self.fields['rol'].label = 'Rol'
        self.fields['active'].label = 'Activo'

        if self.initial['contactCaseRole']:
            contactCaseRole = self.initial['contactCaseRole']
            self.fields['contact'].initial = contactCaseRole.contact.get_name
            self.fields['active'].initial = contactCaseRole.active
            
            #If promovente/promovido principal can't change
            if contactCaseRole.name.pk == 1 or contactCaseRole.name.pk == 2:

               self.fields['rol'].queryset=ContactRole.objects.all()
               self.fields['rol'].widget.attrs['disabled'] = True

            self.fields['rol'].initial = contactCaseRole.name

    def clean_rol(self):

        if self.initial['contactCaseRole'].name.pk == 1 or self.initial['contactCaseRole'].name.pk == 2:
            return self.initial['contactCaseRole'].name
        else:
            return self.cleaned_data.get('rol')

    def save(self, *args, **kwargs):
        contactCaseRole = self.initial['contactCaseRole']
     
        rol = self.cleaned_data['rol']
        active = self.cleaned_data['active']
   
        ContactCaseRole.objects.filter(pk=contactCaseRole.pk).update(name=rol, active=active)

        self.update_comment += u' {0}'.format(
            contactCaseRole.contact.get_name())

        update_event_type = EventType.objects.get(name=u'Actualización')
        event = OutgoingEvent.objects.create(comments=self.update_comment,
                                             event_type=update_event_type,
                                             created_by=self.request.user,
                                             requires_notification=False)

        event.cases.add(*self.initial['case'].container.get_cases_ids())


class CaseUpdateDateClosedForm(BaseUpdateCaseForm):
    update_comment = u'Se actualizó la fecha de cierre del caso'

    class Meta:
        model = Case
        fields = ('date_closed',)
        widgets = {
            'date_closed': DateTimePickerInput(),
        }

    def __init__(self, *args, **kwargs):
        super(CaseUpdateDateClosedForm, self).__init__(*args, **kwargs)
        self.fields['date_closed'].label = u'Fecha Cierre'

    def save(self, *args, **kwargs):

        previous_date_closed = get_object_or_404(Case, pk=self.instance.pk).date_closed


        self.update_comment += u' de {0} a {1}'.format(
            previous_date_closed,
            self.instance.date_closed
       )
        return super(CaseUpdateDateClosedForm, self).save(*args, **kwargs)


class CaseUpdateDescriptionForm(BaseUpdateCaseForm):
    update_comment = u'Se actualizó la descripción del caso'

    class Meta:
        model = Case
        fields = ('description',)

    def __init__(self, *args, **kwargs):
        super(CaseUpdateDescriptionForm, self).__init__(*args, **kwargs)
        self.fields['description'].label = u'Descripción'


class CaseUpdateRecordForm(BaseUpdateCaseForm):
    update_comment = u'Se actualizó quien tiene el expediente del caso'

    class Meta:
        model = Case
        fields = ('record_holder',)

    def __init__(self, *args, **kwargs):
        super(CaseUpdateRecordForm, self).__init__(*args, **kwargs)
        self.fields['record_holder'].label = u'Tiene expediente'
        self.fields['record_holder'].queryset = \
            self.fields['record_holder'].queryset.exclude(is_active=False).order_by('first_name')

    def save(self, *args, **kwargs):
        previous_record_holder = get_object_or_404(Case, pk=self.instance.pk).record_holder

        self.update_comment += u' de {0} {1} a {2} {3}'.format(
            previous_record_holder.first_name, 
            previous_record_holder.last_name,
            self.instance.record_holder.first_name,
            self.instance.record_holder.last_name
        )
        return super(CaseUpdateRecordForm, self).save(*args, **kwargs)


class CaseMergeForm(BaseUpdateCaseForm):
    update_comment = u'Se realizó una consolidación con el caso: '

    merge_cases = forms.CharField(
        widget=SelectAjaxCaseFilterWithPopUp('Case'),
        label='Casos para consolidar')

    class Meta:
        model = Case
        fields = ()

    def __init__(self, *args, **kwargs):
        super(CaseMergeForm, self).__init__(*args, **kwargs)
        self.instance = kwargs.pop('instance')
        case_type = self.instance.case_type
        self.fields['merge_cases'].widget.attrs['data-case-type'] = case_type.code
        self.fields['merge_cases'].widget.attrs['data-only-no-merged-case'] = True
        self.fields['merge_cases'].widget.attrs['data-case-id'] = self.instance.id
        

       
    def clean_merge_cases(self):
        return [int(x) for x in self.cleaned_data['merge_cases'].split(',')]

    # def clean_merge_cases(self):

    #     logger.debug(self.cleaned_data['merge_cases'])
    #     case_num_regex = re.compile(r'(([\w]{2})\W?([0-9]{2,4})\W?([0-9]{3,6}))')
    #     found = case_num_regex.findall(self.cleaned_data['merge_cases'])

    #     return ['-'.join(number[1:]) for number in found]


    def save(self, *args, **kwargs):
        '''
        Merges the cases from the current case's container with the
        ones that where submited by the user
        '''

        merge_cases = list(Case.objects.filter(
             id__in=self.cleaned_data['merge_cases']))


        merge_cases.extend(self.instance.container.get_cases())

        case_container = CaseContainer.merge_cases(self.instance, merge_cases)

        for case in merge_cases:
             self.update_comment += case.number + ','

        self.update_comment = self.update_comment[:-1]

        update_event_type = EventType.objects.get(name=u'Consolidación')

        event = OutgoingEvent.objects.create(comments=self.update_comment,
                                              event_type=update_event_type,
                                              created_by=self.request.user,
                                              requires_notification=False)
       
        event.cases.add(*case_container.get_cases_ids())


        return self.instance
