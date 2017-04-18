# coding: utf-8

from django import forms
from ..profiles.models import CaspUser


class PermsUserUpdateForm(forms.ModelForm):
    update_comment = u'Se actualizó el usuario.'

    class Meta:
        model = CaspUser
        fields = ('first_name', 'last_name', 'email',)

    def __init__(self, *args, **kwargs):
        super(PermsUserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].label = u'Nombre'
        self.fields['last_name'].label = u'Apellidos'
        self.fields['email'].label = u'Email'
