# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import (PasswordChangeForm,
                                       AuthenticationForm)

from .models import CaspUser


class UserCreationForm(forms.ModelForm):
    '''
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    '''
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput)

    class Meta:
        model = CaspUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        elif len(password2) < 6:
            raise forms.ValidationError("Password must be at least 6 chararacters")

        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CaspUserPasswordChangeForm(PasswordChangeForm):
    '''
    Sub-class of default password change form to change text of labels
    '''
    def __init__(self, *args, **kwargs):
        super(CaspUserPasswordChangeForm, self).__init__(*args, **kwargs)

        self.fields['old_password'].label = 'Password actual'
        self.fields['new_password1'].label = 'Password nuevo'
        self.fields['new_password2'].label = u'Confirmación nuevo password'


class CaspUserUpdateForm(forms.ModelForm):
    '''
    Sub-class of model form for CaspUser to edit default field labels
    '''
    def __init__(self, *args, **kwargs):
        super(CaspUserUpdateForm, self).__init__(*args, **kwargs)

        self.fields['username'].help_text = u'Requerido. 30 caracteres máximo. Letras, números y @/./+/-/_ solamente'
        self.fields['email'].label = 'Email'
        self.fields['phone'].label = u'Teléfono'

    class Meta:
        model = CaspUser
        fields = ('username', 'email', 'phone')


class CaspAuthForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254, widget=forms.TextInput(
            attrs={'class': 'form-control', 'autofocus': 'autofocus'}))

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
