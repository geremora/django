# -*- coding: utf-8 -*-
from os.path import join

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from django.utils.decorators import classonlymethod
from django.views.generic import CreateView, DetailView, UpdateView
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.template.base import TemplateDoesNotExist
from django.contrib.formtools.wizard.views import (SessionWizardView,
                                                   WizardView)
import json

from braces.views import LoginRequiredMixin, GroupRequiredMixin

from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from ..cases.models import Case
from .mixins import (
    ProtectAcceptancePerfomedMixin,
    ProtectIncomingEventCreateMixin,
    ProtectIncomingEventUpdateMixin,
    ProtectOutgoingEventCreateMixin,
    ProtectOutgoingEventUpdateMixin,
    ProtectImportedEventUpdateMixin,)
from .models import IncomingEvent, OutgoingEvent, ImportedEvent, EventType
from .forms import (
    IncomingEventCreationForm, OutgoingEventCreationForm,
    UpdateOutgoingEventAcceptanceForm, IncomingEventUpdateObservingForm,
    UpdateIncomingEventAcceptanceForm, ImportedEventUpdateForm,
    OutgoingEventUpdateNotifyingForm)

import logging
logger = logging.getLogger(__name__)

from django.core import serializers


@login_required
def event_type_ajax_get(request):
    event_type_id = request.GET.get('event_type_id', None)

    event_type = EventType.objects.get(id=event_type_id)
    #data = serializers.serialize('json', [EventType.objects.get(id=event_type_id)])

    logger.debug(event_type.amount_days_terms)
    data = {'id': event_type.id, 'requires_acceptance': event_type.requires_acceptance,
    'requires_notification': event_type.requires_notification, 'requires_terms':event_type.requires_terms, 
    'description': event_type.description, 'requires_generate_by': event_type.requires_generate_by,
    'requires_parties': event_type.requires_parties, 'amount_days_terms':event_type.amount_days_terms}

    return HttpResponse(json.dumps(data), mimetype='application/json')


class IncomingEventDetailView(LoginRequiredMixin, DetailView):

    '''
    View incoming event details
    '''
    model = IncomingEvent
    template_name = 'events/event_detail.html'



class OutgoingEventDetailView(LoginRequiredMixin, DetailView):

    '''
    View outgoing event details
    '''
    model = OutgoingEvent
    template_name = 'events/event_detail.html'


class IncomingEventCreateView(LoginRequiredMixin, ProtectIncomingEventCreateMixin, CreateView):
    model = IncomingEvent
    form_class = IncomingEventCreationForm
    template_name = 'cases/caseevent_form.html'

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
        context = super(
            IncomingEventCreateView, self).get_context_data(**kwargs)

        # Add case to context, used by cancel link url tag
        context['case'] = self.case
        return context


class OutgoingEventCreateView(LoginRequiredMixin, ProtectOutgoingEventCreateMixin, CreateView):
    model = OutgoingEvent
    form_class = OutgoingEventCreationForm
    template_name = 'cases/caseevent_form.html'

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
        context = super(
            OutgoingEventCreateView, self).get_context_data(**kwargs)

        # Add case to context, used by cancel button link
        context['case'] = self.case
        return context


class OutgoingEventCreateWizardView(LoginRequiredMixin, ProtectOutgoingEventCreateMixin, SessionWizardView):

    '''
    Handles creation of OutgoingEvent
    - Present ModelForm
    - Ask if the user wants to:
        [Create with attachment] or [Create a document from template]
    - Show document creation editor
    - Save
    '''
    template_name = 'events/event_form_wizard.html'

    # TODO: Change for what we are using on production
    file_storage = FileSystemStorage(
        location=join(settings.MEDIA_ROOT, 'tmp'))

    @classonlymethod
    def as_view(cls, *args, **kwargs):
        form_list = [
            ('event_creation_step', OutgoingEventCreationStepOneForm),
            ('document_creation_step', OutgoingEventCreationStepTwoForm),
        ]

        initkwargs = cls.get_initkwargs(form_list, *args, **kwargs)
        return super(WizardView, cls).as_view(**initkwargs)

    def _my_init(self):
        # Set the case instance variable
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        # Sub-classed to be able to initialize my case ivar
        self._my_init()
        return super(OutgoingEventCreateWizardView,
                     self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Sub-classed to be able to initialize my case ivar
        self._my_init()

        # Detect what button was pressed on first step
        self.with_attachment = bool(
            request.POST.get('with_attachment', False))

        return super(OutgoingEventCreateWizardView, self).post(*args,
                                                               **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(OutgoingEventCreateWizardView,
                        self).get_context_data(*args, **kwargs)

        context['case'] = self.case

        return context

    def process_step(self, form):
        # If the form was submited with the with_attachment button
        # we skip the document creation step
        if self.with_attachment:
            self.form_list.pop('document_creation_step', None)
        elif len(self.form_list) == 1:
            # Insert second step if the form only has one step
            insert_index = len(self.form_list) + 1
            self.form_list.insert(insert_index,
                                  'document_creation_step',
                                  OutgoingEventCreationStepTwoForm)

        # Gets the event_type instance if exists and sets ivar
        self.event_type = form.cleaned_data.get('event_type', None)

        return super(OutgoingEventCreateWizardView,
                     self).process_step(form)

    def get_form_kwargs(self, step):
        kwargs = {}

        if hasattr(self, 'with_attachment'):
            kwargs['with_attachment'] = self.with_attachment

        return kwargs

    def get_form_initial(self, step):
        initial = super(
            OutgoingEventCreateWizardView, self).get_form_initial(step)

        # Set the content of the wysihtml5 editor
        if (step == 'document_creation_step' and
           getattr(self, 'event_type', None)):

            try:
                initial['document_content'] = render_to_string(
                    self.event_type.get_template_name(),
                    {
                        'event_type': self.event_type,
                        'case': self.case
                    })
            except TemplateDoesNotExist, error:
                # Just display a blank template
                logger.error('Template not found: {}'.format(error))

        return initial

    def done(self, form_list, **kwargs):
        logger.debug('done')
        args = {
            'case': self.case,
            'comments': form_list[0].cleaned_data['comments'],
            'requires_terms': form_list[0].cleaned_data['requires_terms'],
            'terms_in_days': form_list[0].cleaned_data['terms_in_days'],
            'terms_type': form_list[0].cleaned_data['terms_type'],
            'requires_acceptance': (
                form_list[0].cleaned_data['requires_acceptance']),
            'accepted': form_list[0].cleaned_data['accepted'],
            'event_type': form_list[0].cleaned_data['event_type'],
            'created_by': self.request.user
        }

        logger.debug(len(form_list))

        if self.with_attachment:
            args.update({
                'attached_file': form_list[0].cleaned_data['attached_file']
            })
        else:
            args.update({
                'document_content': form_list[1].cleaned_data['document_content']
            })

        OutgoingEvent.objects.create(**args)

        # Redirect to case detail
        return HttpResponseRedirect(
            reverse_lazy('case_detail', args=[self.kwargs['pk']]))


class IncomingEventUpdateObservingView(LoginRequiredMixin, ProtectIncomingEventUpdateMixin, UpdateView):
    model = IncomingEvent
    form_class = IncomingEventUpdateObservingForm
    template_name = 'cases/caseevent_form.html'
    pk_url_kwarg = 'event_pk'

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.kwargs['pk']])

    def get_initial(self):
        # Pre-fill form with case and created_by user
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

        return {
            'case': self.case,
        }

    def get_context_data(self, *args, **kwargs):
        context = super(IncomingEventUpdateObservingView,
                        self).get_context_data(*args, **kwargs)

        # Add case to context, used by cancel button link
        context['case'] = self.case
        return context


class OutgoingEventDocumentView(LoginRequiredMixin, DetailView):
    model = OutgoingEvent
    template_name = 'events/document_detail.html'
    pk_url_kwarg = 'event_pk'

    def get_context_data(self, **kwargs):
        context = super(OutgoingEventDocumentView,
                        self).get_context_data(**kwargs)
        print_doc = self.kwargs.get('print', False)
        context['print'] = True if print_doc else False
        return context


class OutgoingEventUpdateAcceptanceView(LoginRequiredMixin, ProtectOutgoingEventUpdateMixin, UpdateView):
    model = OutgoingEvent
    form_class = UpdateOutgoingEventAcceptanceForm
    template_name = 'cases/caseevent_form.html'
    pk_url_kwarg = 'event_pk'

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.case.pk])

    def get_initial(self):
        initial = super(OutgoingEventUpdateAcceptanceView, self).get_initial()
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

        return initial

    def get_context_data(self, **kwargs):
        context = super(OutgoingEventUpdateAcceptanceView,
                        self).get_context_data(**kwargs)
        context['case'] = self.case
        context['is_update'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(OutgoingEventUpdateAcceptanceView,
                       self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class IncomingEventUpdateAcceptanceView(LoginRequiredMixin, ProtectAcceptancePerfomedMixin, UpdateView):
    model = IncomingEvent
    form_class = UpdateIncomingEventAcceptanceForm
    template_name = 'cases/caseevent_form.html'
    pk_url_kwarg = 'event_pk'

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.case.pk])

    def get_initial(self):
        initial = super(IncomingEventUpdateAcceptanceView, self).get_initial()
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

        return initial

    def get_context_data(self, **kwargs):
        context = super(IncomingEventUpdateAcceptanceView,
                        self).get_context_data(**kwargs)
        context['case'] = self.case
        context['is_update'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(IncomingEventUpdateAcceptanceView,
                       self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class ImportedEventUpdateView(LoginRequiredMixin, ProtectImportedEventUpdateMixin, GroupRequiredMixin, UpdateView):
    model = ImportedEvent
    form_class = ImportedEventUpdateForm
    template_name = 'cases/caseevent_form.html'
    pk_url_kwarg = 'event_pk'
    group_required = (u'Total', u'Supervisor', u'Normal User', u'Data Entry')
    raise_exception = True

    def check_membership(self, group):
        if self.request.user.is_superuser:
            return True
            
        for g in self.group_required:
            for ug in self.request.user.groups.values_list('name', flat=True):
                if g == ug:
                    return True
        return False

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.case.pk])

    def get_object(self, *args, **kwargs):
        object = super(ImportedEventUpdateView, self).get_object(
            *args, **kwargs)

        if object.event_type == 'Vista':
            raise PermissionDenied

        return object

    def get_initial(self):
        initial = super(ImportedEventUpdateView, self).get_initial()
        initial['event_type_choices'] = EventType.objects.all()
        initial['created_by'] = self.request.user
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

        return initial

    def get_context_data(self, **kwargs):
        context = super(
            ImportedEventUpdateView, self).get_context_data(**kwargs)
        context['case'] = self.case
        context['is_update'] = True
        return context


class OutgoingEventUpdateNotifyingView(LoginRequiredMixin, ProtectOutgoingEventUpdateMixin, UpdateView):
    model = OutgoingEvent
    form_class = OutgoingEventUpdateNotifyingForm
    template_name = 'cases/caseevent_form.html'
    pk_url_kwarg = 'event_pk'

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.kwargs['pk']])

    def get_initial(self):
        # Pre-fill form with case and created_by user
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

        return {
            'case': self.case,
        }

    def get_context_data(self, *args, **kwargs):
        context = super(OutgoingEventUpdateNotifyingView,
                        self).get_context_data(*args, **kwargs)

        # Add case to context, used by cancel button link
        context['case'] = self.case
        return context
