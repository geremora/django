# -*- coding: utf-8 -*-

from django import forms

from .models import Meeting, AssignOfficial
from .models import MeetingAttendee
from ..contacts.models import Contact
from ..utils.widgets import DateTimePickerInput
from ..utils.forms import CommaSeparatedListField


class MeetingCreationForm(forms.ModelForm):
    attendees = CommaSeparatedListField(
        label='Invitados',
        widget=forms.TextInput(attrs={'class': 'contact-list-ajax'}))

    class Meta:
        model = Meeting
        fields = (
            'room', 'notes', 'date_start', 'date_end', 'meeting_type', 'somebody_armed')

        widgets = {
            'date_start': DateTimePickerInput(attrs={'class': 'form-control'}),
            'date_end': DateTimePickerInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(MeetingCreationForm, self).__init__(*args, **kwargs)

        self.fields['room'].label = u'Salón'
        self.fields['notes'].label = 'Notas'
        self.fields['date_start'].label = 'Fecha / Hora comienzo'
        self.fields['date_end'].label = u'Fecha / Hora terminación'
        self.fields['meeting_type'].label = 'Tipo de vista'
        self.fields['somebody_armed'].label = u'Invitado armado'

    def save(self, *args, **kwargs):
        meeting = super(MeetingCreationForm, self).save(
            commit=False, *args, **kwargs)
        meeting.created_by = self.initial['created_by']
        meeting.save()
        meeting.cases.add(*self.initial['case'].container.get_cases())

        # TODO: Notify attendees
        meeting_attendees = []
        for attendee in self.cleaned_data['attendees']:
            ma = MeetingAttendee(meeting=meeting,
                                 contact=Contact.objects.get(pk=attendee))
            meeting_attendees.append(ma)

        MeetingAttendee.objects.bulk_create(meeting_attendees)

        return meeting


class MeetingUpdateForm(forms.ModelForm):
    attendees = CommaSeparatedListField(
        label='Invitados',
        widget=forms.TextInput(attrs={'class': 'contact-list-ajax'}))

    class Meta:
        model = Meeting
        fields = (
            'status', 'room', 'notes', 'date_start', 'date_end', 'somebody_armed')

        widgets = {
            'date_start': DateTimePickerInput(),
            'date_end': DateTimePickerInput()
        }

    def __init__(self, *args, **kwargs):
        super(MeetingUpdateForm, self).__init__(*args, **kwargs)

        self.fields['status'].label = 'Estatus'
        self.fields['room'].label = u'Salón'
        self.fields['notes'].label = 'Notas'
        self.fields['date_start'].label = 'Fecha / Hora comienzo'
        self.fields['date_end'].label = u'Fecha / Hora terminación'
        self.fields['somebody_armed'].label = u'Invitado armado'

    def save(self, *args, **kwargs):
        meeting = super(MeetingUpdateForm, self).save(*args, **kwargs)

        submited_contacts = self.cleaned_data['attendees']

        # TODO: Notify attendees

        # Delete MeetingAttendee that where not selected
        MeetingAttendee.objects.filter(
            meeting=meeting).exclude(contact__in=submited_contacts).delete()

        for attendee in self.cleaned_data['attendees']:
            contact = Contact.objects.get(pk=attendee)
            MeetingAttendee.objects.get_or_create(meeting=meeting, contact=contact)

        return meeting


class MeetingAttendanceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super(MeetingAttendanceForm, self).__init__(*args, **kwargs)

        attendance_choices = (
            ('', '-------'),
            (1, 'Se presentó'),
            (0, 'No se presentó')
        )

        for attendee in self.initial['attendees']:
            if attendee.did_show_up is None:
                did_show_up = None
            elif attendee.did_show_up:
                did_show_up = 1
            else:
                did_show_up = 0

            self.fields['{}'.format(attendee.pk)] = forms.ChoiceField(
                label=attendee.contact.get_name(), choices=attendance_choices,
                initial=did_show_up)

    def save(self, *args, **kwargs):
        for pk, value in self.cleaned_data.items():
            if value == '1':
                did_show_up = True
            elif value == '0':
                did_show_up = False

            MeetingAttendee.objects.filter(pk=pk).update(did_show_up=did_show_up)

class AssignOfficialForm(forms.ModelForm):
    class Meta:
        model = AssignOfficial
        fields = (
            'assigned_official', 'assigned_date')

        widgets = {
            'assigned_date': DateTimePickerInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AssignOfficialForm, self).__init__(*args, **kwargs)

        self.fields['assigned_official'].label = u'Oficial a asignar'
        self.fields['assigned_date'].label = 'Fecha a asignar'

    def save(self, *args, **kwargs):
        assigned_official = super(AssignOfficialForm, self).save(
            commit=False, *args, **kwargs)
        assigned_official.assigned_by = self.initial['assigned_by']
        assigned_official.save()

        return assigned_official
