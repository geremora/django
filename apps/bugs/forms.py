# -*- coding: utf-8 -*-

from django import forms

from .models import Bug


class BugCreationForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ('bug_type', 'message')

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super(BugCreationForm, self).__init__(*args, **kwargs)

        self.fields['bug_type'].label = 'Tipo de reporte'
        self.fields['message'].label = u'Descripción'

    def save(self, *args, **kwargs):
        bug = super(BugCreationForm, self).save(commit=False, *args, **kwargs)

        bug.created_by = self.created_by
        bug.save()

        return bug
