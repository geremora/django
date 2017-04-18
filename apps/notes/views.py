# -*- coding: utf-8 -*-

from django.views.generic import CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from braces.views import LoginRequiredMixin

from .models import Note
from .forms import NoteCreationForm, NoteUpdateForm
from .mixins import (ProtectNoteCreateMixin,
                     ProtectNoteUpdateMixin,)
from ..cases.models import Case


class NoteCreateView(LoginRequiredMixin, ProtectNoteCreateMixin, CreateView):

    '''
    Creates a note for the current case
    '''
    model = Note
    form_class = NoteCreationForm

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.kwargs['pk']])

    def get_initial(self):
        # Pre-fill form with case and created_by user
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

        return {
            'case': self.case,
            'created_by': self.request.user
        }

    def get_context_data(self, *args, **kwargs):
        context = super(NoteCreateView, self).get_context_data(**kwargs)

        # Add case to context, used by cancel button link
        context['case'] = self.case
        return context


class NoteUpdateView(LoginRequiredMixin, ProtectNoteUpdateMixin, UpdateView):
    model = Note
    form_class = NoteUpdateForm
    pk_url_kwarg = 'note_pk'

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.case.pk])

    def get_initial(self):
        initial = super(NoteUpdateView, self).get_initial()

        # Pre-fill form with case and created_by user
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

        return initial

    def get_context_data(self, *args, **kwargs):
        context = super(NoteUpdateView, self).get_context_data(**kwargs)

        # Add case to context, used by cancel button link
        context['case'] = self.case
        return context
