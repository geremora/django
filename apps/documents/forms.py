# -*- coding: utf-8 -*-

from django import forms

from .models import Document, DocumentType


class DocumentCreationForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document_type', )

    def __init__(self, *args, **kwargs):
        super(DocumentCreationForm, self).__init__(*args, **kwargs)

        self.fields['document_type'].label = 'Tipo de documento'
   #     self.fields['content'].label = 'Comentarios'

    def save(self, *args, **kwargs):
        document = super(DocumentCreationForm, self).save(
            commit=False, *args, **kwargs)
        document.created_by = self.initial['created_by']
        document.case = self.initial['case']
        document.save()

        return document


