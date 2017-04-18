# -*- coding: utf-8 -*-

import json

from django.views.generic import (
    ListView, CreateView, DetailView,
    UpdateView, DeleteView)
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse

from braces.views import LoginRequiredMixin

from .models import Contact, ContactType
from .forms import ContactForm
from .mixins import (ProtectCreateMixin,
                     ProtectUpdateMixin,
                     ProtectDeleteMixin)

from ..cases.models import CaseType


@login_required
def contacts_ajax_search(request):
    ids = request.GET.get('ids', None)
    search = request.GET.get('q', '')
    contact_type = request.GET.get('type', None)
    case_type_id = request.GET.get('case_type', None)
    limit = int(request.GET.get('page_limit', 100))

    if ids is not None:

        if ids == '':
            queryset = []
        else:
            queryset = Contact.objects.filter(
                id__in=ids.split(','))

    elif contact_type:
        contact_type = ContactType.objects.get(pk=contact_type)
        queryset = Contact.objects.filter(
            Q(institutional_name__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(phone1__icontains=search)
            | Q(email__icontains=search)
            | Q(phone2__icontains=search),
            contact_type=contact_type)
    else:
        queryset = Contact.objects.filter(
            Q(institutional_name__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(phone1__icontains=search)
            | Q(email__icontains=search)
            | Q(phone2__icontains=search))

    if case_type_id:
        case_type_code = CaseType.objects.get(id=case_type_id).code
        if case_type_code in ['SA', 'AQ', 'CA', 'PR']:
            queryset = queryset.filter(contact_type=1).exclude(institutional_name__istartswith='municipio')
        if case_type_code in ['CO', 'CD', 'PD', 'SE']:
            queryset = queryset.filter(contact_type=5) | queryset.filter(contact_type=4)
        if case_type_code in ['SM']:
            queryset = queryset.filter(contact_type=1, institutional_name__istartswith='municipio')

    if ids is None:
        queryset = queryset[:limit]

    data = [{'id': c.id, 'text': c.get_friendly_info()} for c in queryset]

    return HttpResponse(json.dumps(data), mimetype='application/json')


class ContactListView(LoginRequiredMixin, ListView):

    '''
    List all contacts
    '''
    paginate_by = 50

    def get_queryset(self):
        # Detect filter or serach and return the queryset
        c_type = self.request.GET.get('type', None)
        search = self.request.GET.get('search', None)
        sortBy = self.request.GET.get('sort', None)

        if c_type and search:
            # Do both
            contact_type = get_object_or_404(ContactType, pk=c_type)
            queryset = Contact.objects.filter(
                Q(institutional_name__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(phone1__icontains=search)
                | Q(email__icontains=search)
                | Q(phone2__icontains=search),
                contact_type=contact_type) | Contact.objects.extra(where=["UPPER(CONCAT_WS(' ', first_name,last_name)) LIKE UPPER(unaccent(%s))"], params=['%' + search + '%'])
        elif c_type:
            # Filter by ContactType
            contact_type = get_object_or_404(ContactType, pk=c_type)
            queryset = Contact.objects.filter(contact_type=contact_type)
        elif search:
            # Simple LIKE search of fields
            queryset = Contact.objects.filter(
                Q(institutional_name__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(phone1__icontains=search)
                | Q(email__icontains=search)
                | Q(phone2__icontains=search)) | Contact.objects.extra(where=["UPPER(CONCAT_WS(' ', first_name,last_name)) LIKE UPPER(unaccent(%s))"], params=['%' + search + '%'])
        else:
            # Return all
            queryset = Contact.objects.all()

        if sortBy:
            queryset = queryset.order_by(sortBy)
        return queryset

    def get_context_data(self, **kwargs):
        # Add contact type and query to template context
        context = super(ContactListView, self).get_context_data(**kwargs)
        context['contact_types'] = ContactType.objects.all()

        search = self.request.GET.get('search', None)
        if search:
            context['search_query'] = search

        c_type = self.request.GET.get('type', None)
        if c_type:
            context['c_type'] = int(c_type)

        return context


class ContactCreateView(LoginRequiredMixin, ProtectCreateMixin, CreateView):

    '''
    Create a new Contact
    '''
    model = Contact
    success_url = reverse_lazy('contact_list')
    form_class = ContactForm


class ContactDetailView(LoginRequiredMixin, DetailView):

    '''
    View Contact details
    '''
    model = Contact


class ContactUpdateView(LoginRequiredMixin, ProtectUpdateMixin, UpdateView):

    '''
    Update Contact information
    '''
    model = Contact
    form_class = ContactForm

    def get_success_url(self):
        # Send to contact_detail when saved
        return reverse_lazy('contact_detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        # Add the is_update field to change copy on template
        # we are sharing the template with the ContactCreateView
        context = super(ContactUpdateView, self).get_context_data(**kwargs)
        context['is_update'] = True

        return context


class ContactDeleteView(LoginRequiredMixin, ProtectDeleteMixin, DeleteView):

    '''
    Delete Contact
    '''
    model = Contact
    success_url = reverse_lazy('contact_list')
