# -*- coding: utf-8 -*-

from django import forms

from .models import Note

from ..events.models import IncomingEvent, OutgoingEvent


class NoteCreationForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('content','related_outgoing_event', 'related_incoming_event')

    def __init__(self, *args, **kwargs):
        super(NoteCreationForm, self).__init__(*args, **kwargs)

        self.fields['content'].label = 'Notas'
        self.fields['related_outgoing_event'].label = 'Relacionado con (evento saliente)'
        self.fields['related_incoming_event'].label = 'Relacionado con (evento entrante)'

        self.fields['related_incoming_event'].queryset = IncomingEvent.objects.filter(cases__in=[self.initial['case'].id])
        self.fields['related_outgoing_event'].queryset = OutgoingEvent.objects.filter(cases__in=[self.initial['case'].id])

        self.fields['related_incoming_event'].label_from_instance = lambda obj: "%s (%s)" % (obj.event_type, obj.date_created.strftime('%m/%d/%Y'))
        self.fields['related_outgoing_event'].label_from_instance = lambda obj: "%s (%s)" % (obj.event_type, obj.date_created.strftime('%m/%d/%Y'))

    def save(self, *args, **kwargs):
        note = super(NoteCreationForm, self).save(
            commit=False, *args, **kwargs)
        note.created_by = self.initial['created_by']
        note.case = self.initial['case']
        note.save()

        if self.initial['case'].was_consolidated():
            for c in self.initial['case'].container.get_cases().exclude(id__in=[self.initial['case'].id]):
           
                new_note = Note.objects.create(content=note.content,
                                             case=c,
                                             created_by=note.created_by)
                new_note.save()


        return note


class NoteUpdateForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super(NoteUpdateForm, self).__init__(*args, **kwargs)

        self.fields['content'].label = 'Notas'
