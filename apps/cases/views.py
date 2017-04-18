# -*- coding: utf-8 -*-
import time
import json
import base64
import hmac
import urllib

from hashlib import sha1
from os.path import join
from django.core.mail.message import EmailMultiAlternatives
from django.core.cache import cache


from django.template import RequestContext

from django.views.generic import ListView, DetailView, UpdateView, RedirectView, DeleteView
from django.contrib.formtools.wizard.views import SessionWizardView, WizardView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, render_to_response
from django.db.models import Q
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.utils.decorators import classonlymethod
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.template.defaultfilters import slugify

from braces.views import LoginRequiredMixin
from django_fsm import transition, TransitionNotAllowed

#from django_fsm.db.fields import TransitionNotAllowed
from apps.cases.tasks import create_txt_email

from .models import Case, CaseCategory, CaseContainer, CaseContainerActionSequence, ContactCaseRole, CaseType
from ..events.models import EventType, OutgoingEvent
from .mixins import (ProtectCaseTypeMixin,
                     ProtectClosedCaseMixin,
                     ProtectChangeCaseMixin,
                     ProtectMergeCaseMixin,
                     ProtectUnmergeCaseMixin,
                     ProtectCaseCreateMixin,
                     ProtectChangeAssignedUserMixin,
                     ProtectCaseUpdateContactsMixin,
                     ProtectChangeDescriptionCaseMixin,
                     ProtectCaseUpdateRecordHolderMixin,
                     ProtectChangeCaseCategoryCaseMixin,
                     ProtectChangeDateClosedCaseMixin,
                     ProtectReOpenCaseMixin)

from ..contacts.models import Contact, ContactRole

from ..events.models import get_user_upload_path

from .forms import (
    CaseUpdateTypeForm,
    CaseCreationStepOneForm,
    CaseUpdateAssignedUserForm,
    CaseUpdateContactForm,
    CaseUpdateDescriptionForm,
    CaseUpdateRecordForm,
    CaseMergeForm,
    CaseUpdateCaseCategoryForm,
    CaseUpdateDateClosedForm,
    CaseContactCreateForm,
    CaseRemoveCaseMediationForm
)
from .extra_forms.ao import ExtraForm

from django_tables2 import RequestConfig
from .tables import CaseTable, CaseContactTable, CasesConsolidatedContactTable

from .tasks import unmerge_cases

import logging
logger = logging.getLogger(__name__)


@login_required
def get_s3_signature(request):
    # Load necessary information into the application:
    AWS_ACCESS_KEY = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_KEY = str(settings.AWS_SECRET_ACCESS_KEY)
    S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME

    # Collect information on the file from the GET parameters of the request:

    # s3_object_name will be broken up to be slugified correctly.
    filename, dot, ext = request.GET['s3_object_name'].rpartition('.')

    # Filename will be slugified to avoid any potential problems when trying to download the file.
    sluged_filename = '{0}{1}{2}'.format(slugify(filename), dot, ext)

    object_name = get_user_upload_path(None, urllib.quote_plus(sluged_filename))

    mime_type = request.GET['s3_object_type']

    # Set the expiry time of the signature (in seconds) and declare the permissions of the file to be uploaded
    expires = int(time.time()+10)
    amz_headers = 'x-amz-acl:private'

    # Generate the PUT request that JavaScript will use:
    put_request = str('PUT\n\n%s\n%d\n%s\n/%s/%s' % (mime_type, expires, amz_headers, S3_BUCKET, object_name))

    # Generate the signature with which the request can be signed:
    signature = base64.encodestring(hmac.new(AWS_SECRET_KEY, put_request, sha1).digest())
    # Remove surrounding whitespace and quote special characters:
    signature = urllib.quote_plus(signature.strip())

    # Build the URL of the file in anticipation of its imminent upload:
    url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, object_name)

    content = json.dumps({
        'signed_request': '%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
        'url': url,
        'object_name': object_name
    })

    # Return the signed request and the anticipated URL back to the browser in JSON format:
    return HttpResponse(content, mimetype='application/json; charset=utf-8')


@login_required
def case_ajax_search(request):
    case_type = request.GET.get('case_type', None)
    only_no_merged = request.GET.get('only_no_merged', None)
    case_id = request.GET.get('case_id', None)

    only_no_merged = only_no_merged == 'True'

    search = request.GET.get('q', '')
    limit = int(request.GET.get('page_limit', 100))

    queryset = Case.objects.filter(
            Q(number__icontains=search))
 
    if case_type is not None:
        queryset = queryset.filter(case_type__code=case_type)
    logger.debug(case_id)
    if case_id is not None:
        queryset = queryset.exclude(id__in=[case_id])

    data = []

    for case in queryset:
        c = {'id': case.id, 'text': case.number}
        if only_no_merged:
            if not case.was_consolidated():
                data.append(c)
        else:
            data.append(c)

    return HttpResponse(json.dumps(data), mimetype='application/json')


@login_required
def case_categories_ajax_by_case_type(request):
    case_type_id = request.GET.get('case_type_id', None)

    case_type = CaseType.objects.get(id=case_type_id)
    
    data = []

    for case_category in case_type.case_category.all():          
        data.append({'id':case_category.id, 'name':case_category.name})

    return HttpResponse(json.dumps(data), mimetype='application/json')


@login_required
def case_feed_json(request):
    id = request.GET.get('id', None)
    search = request.GET.get('q', '')

    user = request.user

    with_events = request.GET.get('with_events', None)
    with_notes = request.GET.get('with_notes', None)
    with_meetings = request.GET.get('with_meetings', None)
    with_imported = request.GET.get('with_imported', None)
    
    totalResult = request.GET.get('totalResult', 10)


    with_events = with_events == 'true'
    with_notes = with_notes == 'true'
    with_meetings = with_meetings == 'true'

    case = Case.objects.filter(
            Q(pk__in=[id]))[0]

    context = RequestContext(request, {
        'object': case.get_feed(user=user, with_events=with_events, with_notes=with_notes, with_meetings=with_meetings, with_imported_events=with_imported, limit=totalResult),
      })

    return render_to_response("cases/detail/event/event_list_partial.html", context_instance = context)

def eliminate_close_transition(transitions):
        for trans in transitions:
            if trans['target_name'] == 'closed':
                transitions = transitions.remove(trans)
        return transitions


class CaseReOpenView(LoginRequiredMixin,ProtectReOpenCaseMixin, RedirectView):

    '''
    This will execute a transition method for a case. The method is
    choosen dynamically based on the last segment of the url.
    '''
    permanent = False

    def get(self, request, *args, **kwargs):
        # Get the case
        self.object = get_object_or_404(Case, pk=kwargs.get('pk'))

        func = getattr(self.object, 'go_' + self.object.case_type.code.lower() + '_' + 'case_type_confirmed')
  
        try:
            func()


            # Add transition event
            # Get transition event type
            transition_type = EventType.objects.get(pk=27)
            comments='Se reabre el caso'
            event = OutgoingEvent.objects.create(event_type=transition_type,
                                                 comments=comments,
                                                 created_by=request.user)

            event.cases.add(*self.object.container.get_cases_ids())

            self.object.save()

        except TransitionNotAllowed:
                messages.add_message(request, messages.ERROR,
                                     'No se puede "{}". No se están cumpliendo \
                                     todos los requsitos para \
                                     continuar.'.format(func.__doc__.strip()))

        return super(CaseReOpenView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        cache.clear()
        
        return reverse_lazy('case_detail', args=[self.object.id])



class CaseListView(LoginRequiredMixin, ListView):
    model = Case
    # paginate_by = 20

    def get_queryset(self):
        # Detect filter or search and return the queryset
        category_pk = self.request.GET.get('category', None)
        search = self.request.GET.get('search', None)
        year = self.request.GET.get('year', None)
        defendant_pk = self.request.GET.get('defendant', None)

        if category_pk:
            # Filter by ContactType
            case_category = get_object_or_404(CaseCategory, pk=category_pk)
            queryset = Case.objects.select_related(
                'case_type', 'defendant', 'plaintiff', 'assigned_user', 'case_category').filter(
                case_category=case_category)
        elif search:
            # Simple LIKE search of fields
            queryset = Case.objects.select_related(
                'defendant', 'plaintiff', 'assigned_user', 'case_category').filter(
                Q(number__icontains=search) |
                Q(old_number__icontains=search) |
                Q(description__icontains=search) |
                Q(state__icontains=search) |
                Q(case_type__name__icontains=search) |
                Q(case_category__name__icontains=search) |
                Q(defendant__first_name__icontains=search) |
                Q(defendant__last_name__icontains=search) |
                Q(defendant__institutional_name__icontains=search) |
                Q(plaintiff__first_name__icontains=search) |
                Q(plaintiff__last_name__icontains=search) |
                Q(plaintiff__institutional_name__icontains=search)) | Case.objects.extra(where=["UPPER(CONCAT_WS(' ', contacts_contact.first_name,contacts_contact.last_name)) LIKE UPPER(unaccent(%s)) OR UPPER(CONCAT_WS(' ', T5.first_name,T5.last_name)) LIKE UPPER(unaccent(%s))"], params=['%' + search + '%', '%' + search + '%'])
        elif year:
            # Filter by date created
            queryset = Case.objects.select_related(
                'defendant', 'plaintiff', 'assigned_user', 'case_category').filter(
                date_created__year=int(year))
        elif defendant_pk:
            queryset = Case.objects.filter(
                defendant__in=Contact.objects.select_related(
                    'defendant', 'plaintiff', 'assigned_user', 'case_category').filter(
                    pk=defendant_pk))
        else:
            # Return all
            queryset = Case.objects.select_related(
                'defendant', 'plaintiff', 'assigned_user', 'case_category').all()

        return queryset

    def get_context_data(self, **kwargs):
        context = super(CaseListView, self).get_context_data(**kwargs)

        context['user_case_table'] = None
        context['case_list_table'] = None

        user = self.request.user

        # Search query
        search = self.request.GET.get('search', None)
        if search:
            context['search_query'] = search

        context['has_add_case_perm'] = user.get_group_permissions().issuperset(['cases.add_case']) or user.has_perm('cases.add_case')

        if context['object_list'].count() > 0:
            user_object_list = context['object_list'].filter(assigned_user=self.request.user)
            if not search:
                user_object_list = user_object_list.exclude(state='closed')

            case_list = context['object_list'].exclude(id__in=user_object_list)

            if not search and not self.request.user.is_superuser:
                case_list = case_list.filter(assigned_user=self.request.user)

            if user_object_list.count() > 0:
                user_case_table = CaseTable(user_object_list)
                RequestConfig(request=self.request, paginate={"per_page": 20}).configure(user_case_table)
                context['user_case_table'] = user_case_table

            if case_list.count() > 0:
                case_table = CaseTable(case_list)
                RequestConfig(request=self.request, paginate={"per_page": 20}).configure(case_table)
                context['case_list_table'] = case_table

        context['object_list'] = None

        return context
        

class CaseCreateWizardView(LoginRequiredMixin, ProtectCaseCreateMixin, SessionWizardView):
    template_name = 'cases/case_form_wizard.html'
    #template_name = 'cases/case_form.html'
    # TODO: Change for what we are using on production
    file_storage = FileSystemStorage(
        location=join(settings.MEDIA_ROOT, 'tmp'))

    @classonlymethod
    def as_view(cls, *args, **kwargs):
        form_list = [
            ('basic_info_step', CaseCreationStepOneForm),
   #         ('extra_info_step', ExtraForm)
        ]

        initkwargs = cls.get_initkwargs(form_list, *args, **kwargs)
        return super(WizardView, cls).as_view(**initkwargs)

    def _my_init(self):
        # Init instance vars
        pass

    def get(self, request, *args, **kwargs):
        # Sub-classed to be able to initialize my case ivar
        self._my_init()
        return super(CaseCreateWizardView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Sub-classed to be able to initialize my ivars
        self._my_init()

        return super(CaseCreateWizardView, self).post(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(CaseCreateWizardView,
                        self).get_context_data(*args, **kwargs)
        return context

    def get_form_kwargs(self, step):
        kwargs = {}
        return kwargs

    def get_form_initial(self, step):
        initial = super(CaseCreateWizardView, self).get_form_initial(step)
        return initial

    def done(self, form_list, **kwargs):
        # Save results
        basic_info = self.get_cleaned_data_for_step('basic_info_step')
        extra_info = self.get_cleaned_data_for_step('extra_info_step') or {}

        case = Case.create_new_case(basic=basic_info,
                                    extra=extra_info,
                                    created_by=self.request.user)

        # Creates contact case rol for defendant and plaintiff
        role_plaintiff = ContactRole.objects.get(pk=1)
        contact_case_plaintiff = ContactCaseRole.objects.create(name=role_plaintiff, case=case, contact=case.plaintiff)
        contact_case_plaintiff.save()

        role_defendant = ContactRole.objects.get(pk=2)
        contact_case_defendant = ContactCaseRole.objects.create(name=role_defendant, case=case, contact=case.defendant)
        contact_case_defendant.save()


        # Remove extra form
        self.form_list.pop('extra_info_step', None)

        # Redirect to case detail
        return HttpResponseRedirect(
            reverse_lazy('case_detail', args=[case.pk]))


class CaseMergedListView(LoginRequiredMixin, ListView):
    model = Case
    template_name = 'cases/detail/case_merged.html'
    paginate_by = 20

    def get_queryset(self, queryset=None):
        case = Case.objects.select_related(
            'container').get(pk=self.kwargs.get('pk'))

        user = self.request.user
        user_group_permissions = user.get_group_permissions()

        tmp_case_list = []
        case_list = Case.objects.filter(container=case.container)

        for merged_case in case_list:
            case_type = merged_case.case_type.code

            merged_case.can_unmerge = (
                (user_group_permissions.issuperset(['cases.can_unmerge_case_{}'.format(case_type)]) or
                    user.has_perm('cases.can_unmerge_case_{}'.format(case_type))) or
                (user == merged_case.assigned_user and
                    (user_group_permissions.issuperset(['cases.can_unmerge_case_own_{}'.format(case_type)]) or
                        user.has_perm('cases.can_unmerge_case_own_{}'.format(case_type)))))

            tmp_case_list.append(merged_case)
        return tmp_case_list  # Case.objects.filter(container=case.container)

    def get_context_data(self, **kwargs):
        context = super(CaseMergedListView, self).get_context_data(**kwargs)

        user = self.request.user
        user_group_permissions = user.get_group_permissions()

        # TODO: check and see hwo to get the case here and add the missing permissions
        can_unmerge_case = user_group_permissions.issuperset(['cases.can_unmerge_case']) or user.has_perm('cases.can_unmerge_case')

        context['can_unmerge_case'] = can_unmerge_case
        context['object'] = {}
        context['object']['id'] = self.kwargs.get('pk')
        return context


class CaseDetailView(LoginRequiredMixin, DetailView):
    model = Case

    def get_object(self, queryset=None):
        return Case.objects.select_related().get(pk=self.kwargs.get('pk'))

    def get_context_data(self, object=None, **kwargs):
        context = super(CaseDetailView, self).get_context_data(**kwargs)

        case = object

        user = self.request.user
        user_group_permissions = user.get_group_permissions()

        user_groups = user.groups.all()
        context['user_groups'] = [slugify(ug.name) for ug in user_groups]

        feed = case.get_feed(user=user)

        contactsRoleCase = case.get_contacts_role()

        # Template permissions
        # TODO: Look for a way to clean all this up. Maybe look for an app to handle it?
        can_change_case = user_group_permissions.issuperset(['cases.change_case']) or user.has_perm('cases.change_case')
        # TODO: validate if this should be change_meetingattendee
        can_change_meetings = user_group_permissions.issuperset(['meetings.change_meeting']) or user.has_perm('meetings.change_meeting')
        can_merge_cases = user_group_permissions.issuperset(['cases.can_merge_case']) or user.has_perm('cases.can_merge_case')
        can_change_assigned_user = user_group_permissions.issuperset(['cases.change_assigned_user_case']) or user.has_perm('cases.change_assigned_user_case')
        can_change_record_holder_case = user_group_permissions.issuperset(['cases.can_change_record_holder_case']) or user.has_perm('cases.can_change_record_holder_case')
        change_outgoing_event = user_group_permissions.issuperset(['cases.change_outgoingevent']) or user.has_perm('cases.change_outgoingevent')
        change_incoming_event = user_group_permissions.issuperset(['cases.change_incomingevent']) or user.has_perm('cases.change_incomingevent')
        change_meeting_attendee = user_group_permissions.issuperset(['meetings.change_meetingattendee']) or user.has_perm('meetings.change_meetingattendee')
        change_case_contact = user_group_permissions.issuperset(['cases.can_change_contacts_case']) or user.has_perm('cases.can_change_contacts_case')
        can_change_case_description = user_group_permissions.issuperset('cases.can_change_description') or user.has_perm('cases.can_change_description')
        can_add_incoming_event = user_group_permissions.issuperset('events.add_incomingevent') or user.has_perm('events.add_incomingevent')
        can_add_outgoing_event = user_group_permissions.issuperset('events.add_outgoingevent') or user.has_perm('events.add_outgoingevent')
        can_add_notes = user_group_permissions.issuperset('notess.add_note') or user.has_perm('notes.add_note')
        can_change_casecategory = user_group_permissions.issuperset('cases.change_casecategory') or user.has_perm('cases.change_casecategory')
        can_change_date_closed = user_group_permissions.issuperset('cases.change_dateclosed') or user.has_perm('cases.change_dateclosed')

        can_re_open_case = user_group_permissions.issuperset(['cases.re_open']) or user.has_perm('cases.re_open')

        context['meetings'] = feed['meetings']
        context['documents'] = case.get_documents() 
        context['case_id'] = case.id
        context['notes'] = feed['notes']
        context['feed'] = feed['feed']
        #context['c'] = case.container

        # Gets a list of valid transitions
        context['transitions'] = (
            #case.get_all_possible_state_transitions())
            case.get_available_state_transitions())

        case_type = case.case_type.code

        if not user_group_permissions.issuperset(['cases.can_close_case_{}'.format(case_type)]) and not user.has_perm('cases.can_close_case_{}'.format(case_type)):
            if (user == case.assigned_user and (not user_group_permissions.issuperset(['cases.can_close_case_own_{}'.format(case_type)]) and
                    not user.has_perm('cases.can_close_case_own_{}'.format(case_type)))):
                context['transitions'] = eliminate_close_transition(context['transitions'])

        if not can_change_case:
            can_change_case = ((user_group_permissions.issuperset(['cases.can_change_case_{}'.format(case_type)]) or user.has_perm('cases.can_change_case_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_change_case_own_{}'.format(case_type)]) or user.has_perm('cases.can_change_case_own_{}'.format(case_type)))))

        if not can_re_open_case:
            can_re_open_case = ((user_group_permissions.issuperset(['cases.can_re_open_case_{}'.format(case_type)]) or user.has_perm('cases.can_re_open_case_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_re_open_case_own_{}'.format(case_type)]) or user.has_perm('cases.can_re_open_case_own_{}'.format(case_type)))))

        if not can_merge_cases:
            can_merge_cases = ((user_group_permissions.issuperset(['cases.can_merge_case_{}'.format(case_type)]) or user.has_perm('cases.can_merge_case_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_merge_case_own_{}'.format(case_type)]) or user.has_perm('cases.can_merge_case_own_{}'.format(case_type)))))

        if not can_change_meetings:
            can_change_meetings = ((user_group_permissions.issuperset(['meetings.can_change_meeting_{}'.format(case_type)]) or user.has_perm('meetings.can_change_meeting_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['meetings.can_change_meeting_own_{}'.format(case_type)]) or user.has_perm('meetings.can_change_meeting_own_{}'.format(case_type)))))

        if not change_meeting_attendee:
            change_meeting_attendee = ((user_group_permissions.issuperset(['meetings.can_change_meeting_attendee_{}'.format(case_type)]) or user.has_perm('meetings.can_change_meeting_attendee_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['meetings.can_change_meeting_attendee_own_{}'.format(case_type)]) or user.has_perm('meetings.can_change_meeting_attendee_own_{}'.format(case_type)))))

        if not can_change_assigned_user:
            can_change_assigned_user = ((user_group_permissions.issuperset(['cases.can_change_assigned_user_case_{}'.format(case_type)]) or user.has_perm('cases.can_change_assigned_user_case_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_change_assigned_user_case_own_{}'.format(case_type)]) or user.has_perm('cases.can_change_assigned_user_case_own_{}'.format(case_type)))))

        if not can_change_record_holder_case:
            can_change_record_holder_case = ((user_group_permissions.issuperset(['cases.can_change_record_holder_case_{}'.format(case_type)]) or user.has_perm('cases.can_change_record_holder_case_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_change_record_holder_case_own_{}'.format(case_type)]) or user.has_perm('cases.can_change_record_holder_case_{}'.format(case_type)))))

        if not change_outgoing_event:
            change_outgoing_event = ((user_group_permissions.issuperset(['cases.can_change_outgoing_event_{}'.format(case_type)]) or user.has_perm('cases.can_change_outgoing_event_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_change_outgoing_event_own_{}'.format(case_type)]) or user.has_perm('cases.can_change_outgoing_event_case_{}'.format(case_type)))))

        if not change_incoming_event:
            change_incoming_event = ((user_group_permissions.issuperset(['cases.can_change_incoming_event_{}'.format(case_type)]) or user.has_perm('cases.can_change_incoming_event_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_change_incoming_event_own_{}'.format(case_type)]) or user.has_perm('cases.can_change_incoming_event_case_{}'.format(case_type)))))
        if not change_case_contact:
            change_case_contact = ((user_group_permissions.issuperset(['cases.can_change_contacts_case_{}'.format(case_type)]) or user.has_perm('cases.can_change_contacts_case_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_change_contacts_case_own_{}'.format(case_type)]) or user.has_perm('cases.can_change_contacts_case_own_{}'.format(case_type)))))

        if not can_change_case_description:
            can_change_case_description = ((user_group_permissions.issuperset(['cases.can_change_description_case_{}'.format(case_type)]) or user.has_perm('cases.can_change_description_case_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_change_description_case_own_{}'.format(case_type)]) or user.has_perm('cases.can_change_description_case_own_{}'.format(case_type)))))

        if not can_add_outgoing_event:
            can_add_incoming_event = ((user_group_permissions.issuperset(['events.can_add_outgoing_event_{}'.format(case_type)]) or user.has_perm('events.can_add_outgoing_event_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['events.can_add_outgoing_event_own_{}'.format(case_type)]) or user.has_perm('events.can_add_outgoing_event_own_{}'.format(case_type)))))

        if not can_add_incoming_event:
            can_add_incoming_event = ((user_group_permissions.issuperset(['events.can_add_incoming_event_{}'.format(case_type)]) or user.has_perm('events.can_add_incoming_event_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['events.can_add_incoming_event_own_{}'.format(case_type)]) or user.has_perm('events.can_add_incoming_event_own_{}'.format(case_type)))))

        if not can_add_notes:
            can_add_notes = ((user_group_permissions.issuperset(['notes.can_add_note_{}'.format(case_type)]) or user.has_perm('notes.can_add_note_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['notes.can_add_note_own_{}'.format(case_type)]) or user.has_perm('notes.can_add_note_own_{}'.format(case_type)))))

        if not can_change_casecategory:
            can_change_casecategory = ((user_group_permissions.issuperset(['cases.change_casecategory_{}'.format(case_type)]) or user.has_perm('cases.change_casecategory_{}'.format(case_type))) or
                (user == case.assigned_user and (user_group_permissions.issuperset(['cases.change_casecategory_own_{}'.format(case_type)]) or user.has_perm('cases.change_casecategory_own_{}'.format(case_type)))))

        context['can_change_case'] = can_change_case
        context['can_change_meetings'] = can_change_meetings
        context['can_merge_cases'] = can_merge_cases
        context['can_change_assigned_user'] = can_change_assigned_user
        context['can_change_record_holder_case'] = can_change_record_holder_case
        context['change_outgoing_event'] = change_outgoing_event
        context['change_incoming_event'] = change_incoming_event
        context['change_meetingattendee'] = change_meeting_attendee
        context['change_case_contact'] = change_case_contact
        context['can_change_case_description'] = can_change_case_description
        context['can_add_outgoing_event'] = can_add_outgoing_event
        context['can_add_incoming_event'] = can_add_incoming_event
        context['can_add_notes'] = can_add_notes
        context['can_change_casecategory'] = can_change_casecategory
        context['can_change_date_closed'] = can_change_date_closed
        context['can_re_open_case'] = can_re_open_case



        return context


class CasePrintView(LoginRequiredMixin, DetailView):
    model = Case
    template_name = 'cases/case_print.html'

    def get_context_data(self, **kwargs):
        context = super(CasePrintView, self).get_context_data(**kwargs)

        user_groups = self.request.user.groups.all()
        context['user_groups'] = [slugify(ug.name) for ug in user_groups]

        feed = self.object.get_feed(user=self.request.user)

        context['meetings'] = feed['meetings']
        context['documents'] = self.object.get_documents()
        context['notes'] = feed['notes']
        context['feed'] = feed['feed']

        return context


class CaseUpdateTypeView(LoginRequiredMixin, ProtectClosedCaseMixin, ProtectCaseTypeMixin, UpdateView):
    model = Case
    form_class = CaseUpdateTypeForm

    def get_success_url(self):
        # Send to case_detail when saved
        cache.clear()
        return reverse_lazy('case_detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        # Add the is_update field to change copy on template
        # we are sharing the template with the ContactCreateView
        context = super(CaseUpdateTypeView, self).get_context_data(**kwargs)
        context['is_update'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(CaseUpdateTypeView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


def filter_by_search_field(term, queryset):
    # Filter case contacts by search term.

    result = queryset.filter(
        Q(contact__first_name__icontains=term) | Q(contact__email__icontains=term) |
        Q(name__name__icontains=term) | Q(contact__last_name__icontains=term)
    )

    return result

class CaseContactsListView(LoginRequiredMixin, ProtectClosedCaseMixin, ListView):
    template_name = 'cases/detail/contacts/contacts_list.html'

    def get_success_url(self):
        # Send to case_detail when saved
        cache.clear()
        return reverse_lazy('case_detail', args=[self.object.id])

    def get_queryset(self):
        case = Case.objects.select_related().get(pk=self.kwargs.get('pk'))

        search_field = self.request.GET.get('search')

        queryset = case.container.get_contacts_role()

        if search_field and queryset:
            queryset = filter_by_search_field(search_field, queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(CaseContactsListView, self).get_context_data(**kwargs)

        user = self.request.user
        case = Case.objects.select_related().get(pk=self.kwargs.get('pk'))

        if case.was_consolidated():
            contact_table = CasesConsolidatedContactTable(context['object_list'])
        else:
            contact_table = CaseContactTable(context['object_list'])

        RequestConfig(request=self.request, paginate={"per_page": 20}).configure(contact_table)
        context['contact_table'] = contact_table
        
        context['case'] = case

        context['object_list'] = None

        return context

@login_required
def delete_case_contact(request, pk, pk2):
    c = get_object_or_404(ContactCaseRole, pk=pk2)
    contact_name = c.contact.get_name()
    c.delete()
    case = get_object_or_404(Case, pk=pk)

    update_comment = u'Se eliminó un contacto: {0}'.format(
            contact_name)

    update_event_type = EventType.objects.get(name=u'Actualización')
    event = OutgoingEvent.objects.create(comments=update_comment,
                                             event_type=update_event_type,
                                             created_by=request.user,
                                             requires_notification=False)

    event.cases.add(*case.container.get_cases_ids())
    
    cache.clear()

    return HttpResponseRedirect(reverse_lazy('case_contacts_list', args=[pk]))    

class CaseUpdateContactView(LoginRequiredMixin, ProtectClosedCaseMixin, ProtectCaseUpdateContactsMixin, UpdateView):
    model = Case
    form_class = CaseUpdateContactForm

    def get_success_url(self):
        # Send to case_detail when saved
        cache.clear()
        return reverse_lazy('case_contacts_list', args=[self.kwargs['pk']])

    def get_context_data(self, **kwargs):
        # Add the is_update field to change copy on template
        # we are sharing the template with the ContactCreateView
        context = super(CaseUpdateContactView, self).get_context_data(**kwargs)
        
        context['is_update'] = True
        return context

    def get_initial(self):
        initial = super(CaseUpdateContactView, self).get_initial()

        initial['contactCaseRole'] = get_object_or_404(ContactCaseRole, pk=self.kwargs['pk2'])
        initial['case'] = get_object_or_404(Case, pk=self.kwargs['pk'])
        return initial

    def get_form_kwargs(self):
        kwargs = super(CaseUpdateContactView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

  

class CaseCreateContactsView(LoginRequiredMixin, ProtectClosedCaseMixin, ProtectCaseUpdateContactsMixin, UpdateView):
    model = Case
    form_class = CaseContactCreateForm

    def get_success_url(self):
        # Send to case_detail when saved
        cache.clear()
        return reverse_lazy('case_contacts_list', args=[self.kwargs['pk']])

    def get_context_data(self, **kwargs):
        # Add the is_update field to change copy on template
        # we are sharing the template with the ContactCreateView
        context = super(CaseCreateContactsView, self).get_context_data(**kwargs)

        context['is_update'] = True
        return context

    def get_initial(self):
        initial = super(CaseCreateContactsView, self).get_initial()

        initial['case'] = get_object_or_404(Case, pk=self.kwargs['pk'])
        return initial

    def get_form_kwargs(self):
        kwargs = super(CaseCreateContactsView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class CaseUpdateAssignedUserView(LoginRequiredMixin, ProtectClosedCaseMixin, ProtectChangeAssignedUserMixin, UpdateView):
    model = Case
    form_class = CaseUpdateAssignedUserForm

    def get_success_url(self):
        # Send to case_detail when saved
        cache.clear()
        return reverse_lazy('case_detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        # Add the is_update field to change copy on template
        # we are sharing the template with the ContactCreateView
        context = super(
            CaseUpdateAssignedUserView, self).get_context_data(**kwargs)
        context['is_update'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(CaseUpdateAssignedUserView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class CaseUpdateDateClosedView(LoginRequiredMixin, ProtectChangeDateClosedCaseMixin, UpdateView):
    model = Case
    form_class = CaseUpdateDateClosedForm

    def get_success_url(self):
        # Send to case_detail when saved
        cache.clear()
        return reverse_lazy('case_detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        # Add the is_update field to change copy on template
        # we are sharing the template with the ContactCreateView
        context = super(
            CaseUpdateDateClosedView, self).get_context_data(**kwargs)
        context['is_update'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(CaseUpdateDateClosedView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class CaseUpdateDescriptionView(LoginRequiredMixin, ProtectClosedCaseMixin, ProtectChangeDescriptionCaseMixin, UpdateView):
    model = Case
    form_class = CaseUpdateDescriptionForm

    def get_success_url(self):
        # Send to case_detail when saved
        cache.clear()
        return reverse_lazy('case_detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        # Add the is_update field to change copy on template
        # we are sharing the template with the ContactCreateView
        context = super(
            CaseUpdateDescriptionView, self).get_context_data(**kwargs)
        context['is_update'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(CaseUpdateDescriptionView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs



  

class CaseUpdateCaseCategoryView(LoginRequiredMixin, ProtectClosedCaseMixin, ProtectChangeCaseCategoryCaseMixin, UpdateView):
    model = Case
    form_class = CaseUpdateCaseCategoryForm

    def get_success_url(self):
        # Send to case_detail when saved
        cache.clear()
        return reverse_lazy('case_detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        # Add the is_update field to change copy on template
        # we are sharing the template with the ContactCreateView
        context = super(
            CaseUpdateCaseCategoryView, self).get_context_data(**kwargs)
        context['is_update'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(CaseUpdateCaseCategoryView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class CaseUpdateRecordView(LoginRequiredMixin, ProtectClosedCaseMixin, ProtectCaseUpdateRecordHolderMixin, UpdateView):
    model = Case
    form_class = CaseUpdateRecordForm

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super(CaseUpdateRecordView, self).get_context_data(**kwargs)
        context['is_update'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(CaseUpdateRecordView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class CaseSendCaseMediationView(LoginRequiredMixin, ProtectClosedCaseMixin, RedirectView):
    http_method_names = ['get']

    def get_redirect_url(self, **kwargs):
        cache.clear()
        return reverse_lazy('case_detail',args=[self.request.GET.get('case_pk')])

    def get(self, request, *args, **kwargs):

        date_submitted = time.strftime('%Y-%m-%d %I:%M:%S')

        user = request.user

        case = Case.objects.select_related().get(pk=kwargs.get('pk', None))

        case.mediation = True

        case.save()

        update_comment = u'El caso {} se mando a mediación'.format(case.number)

        update_event_type = EventType.objects.get(name=u'Actualización')

        event = OutgoingEvent.objects.create(comments=update_comment,
                                             event_type=update_event_type,
                                             created_by=self.request.user,
                                             requires_notification=False)

       
        event.cases.add(*case.container.get_cases_ids())

        event.cases.add(case.id)

        return HttpResponseRedirect(reverse_lazy('case_detail', args=[case.id]))    

class CaseRemoveCaseMediationView(LoginRequiredMixin, ProtectClosedCaseMixin, UpdateView):
    model = Case
    form_class = CaseRemoveCaseMediationForm

    def get_success_url(self):
        # Send to case_detail when saved
        cache.clear()
        return reverse_lazy('case_detail', args=[self.kwargs['pk']])

    def get_context_data(self, **kwargs):
        # Add the is_update field to change copy on template
        # we are sharing the template with the ContactCreateView
        context = super(
            CaseRemoveCaseMediationView, self).get_context_data(**kwargs)
        context['is_update'] = True
        return context

    def get_initial(self):
        initial = super(CaseRemoveCaseMediationView, self).get_initial()

        initial['case'] = get_object_or_404(Case, pk=self.kwargs['pk'])
        return initial

    def get_form_kwargs(self):
        kwargs = super(CaseRemoveCaseMediationView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs



class CaseTransitionView(LoginRequiredMixin, ProtectClosedCaseMixin, RedirectView):

    '''
    This will execute a transition method for a case. The method is
    choosen dynamically based on the last segment of the url.
    '''
    permanent = False

    def post(self, request, *args, **kwargs):
        # Get the case
        self.object = get_object_or_404(Case, pk=kwargs.get('pk'))


        # Replace dashes with underscores and prepend go_ as the name of the
        # method that will be run. Example: ao-created -> go_ao_created
        
        try:
            update_comment = u'De {0}'.format(self.object.pretty_state_name)

            if self.object.was_consolidated():
                for case in self.object.container.get_cases():
                    func = getattr(
                            case, 'go_{}'.format(
                                kwargs.get('state').replace('-', '_')))
                    func()
                    case.save()
                    update_comment += u' a {0}'.format(self.object.pretty_state_name)

            else:
                    func = getattr(self.object, 'go_{}'.format(kwargs.get('state').replace('-', '_')))
                    func()
                    self.object.save()
                    update_comment += u' a {0}'.format(self.object.pretty_state_name)
           
            # Add transition event
            # Get transition event type
            transition_type = EventType.objects.get(pk=27)

            event = OutgoingEvent.objects.create(event_type=transition_type,
                                                 comments=update_comment,
                                                 created_by=self.request.user,
                                                 requires_notification=False)

            #event.cases.add(self.object)

            event.cases.add(*self.object.container.get_cases_ids())

        except TransitionNotAllowed:
            messages.add_message(request, messages.ERROR,
                                 'No se puede "{}". No se están cumpliendo \
                                 todos los requsitos para \
                                 continuar.'.format(func.__doc__.strip()))

        return super(CaseTransitionView, self).post(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.object.id])


class CaseMergeView(LoginRequiredMixin, ProtectMergeCaseMixin, UpdateView):
    model = Case
    form_class = CaseMergeForm

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super(CaseMergeView, self).get_context_data(**kwargs)
        user = self.request.user

        user_group_permissions = user.get_group_permissions()

        can_unmerge_case = user_group_permissions.issuperset(['cases.can_unmerge_case']) or user.has_perm('cases.can_unmerge_case')

        if context['case'].case_type.code == 'AO':
            can_unmerge_case = ((user_group_permissions.issuperset(['cases.can_unmerge_case_AO']) or user.has_perm('cases.can_unmerge_case_AO')) or
                                (user == context['case'].assigned_user and (user_group_permissions.issuperset(['cases.can_unmerge_case_own_AO']) or user.has_perm('cases.can_unmerge_case_own_AO'))))
        elif context['case'].case_type.code == 'XX':
            can_unmerge_case = ((user_group_permissions.issuperset(['cases.can_unmerge_case_XX']) or user.has_perm('cases.can_unmerge_case_XX')) or
                                (user == context['case'].assigned_user and (user_group_permissions.issuperset(['cases.can_unmerge_case_own_XX']) or user.has_perm('cases.can_unmerge_case_own_XX'))))

        context['can_unmerge_case'] = can_unmerge_case
        context['is_update'] = True
        return context

    def get_initial(self):
        initial = super(CaseMergeView, self).get_initial()

        initial['case'] = get_object_or_404(Case, pk=self.kwargs['pk'])
        return initial

    def get_form_kwargs(self):
        kwargs = super(CaseMergeView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class CaseActiveView(LoginRequiredMixin, RedirectView):
    http_method_names = ['get']

    def get_redirect_url(self, **kwargs):
        cache.clear()
        return reverse_lazy('case_detail',
                            args=[self.request.GET.get('case_pk')])

    def get(self, request, *args, **kwargs):

        date_submitted = time.strftime('%Y-%m-%d %I:%M:%S')

        user = request.user

        case_main = Case.objects.select_related().get(pk=kwargs.get('pk', None))

        case_active = Case.objects.select_related().get(pk=kwargs.get('pk2', None))

        case_active.active = True

        case_active.save()

        update_comment = u'Se activó el caso {}'.format(case_active.number)

        update_event_type = EventType.objects.get(name=u'Actualización')

        event = OutgoingEvent.objects.create(comments=update_comment,
                                             event_type=update_event_type,
                                             created_by=self.request.user,
                                             requires_notification=False)

       
        event.cases.add(*case_main.container.get_cases_ids())

        event.cases.add(case_active.id)

        return HttpResponseRedirect(reverse_lazy('case_detail', args=[case_main.id]))    

class CaseDesactiveView(LoginRequiredMixin, RedirectView):
    http_method_names = ['get']

    def get_redirect_url(self, **kwargs):
        cache.clear()
        return reverse_lazy('case_detail',
                            args=[self.request.GET.get('case_pk')])

    def get(self, request, *args, **kwargs):

        date_submitted = time.strftime('%Y-%m-%d %I:%M:%S')

        user = request.user

        case_main = Case.objects.select_related().get(pk=kwargs.get('pk', None))

        case_desactive = Case.objects.select_related().get(pk=kwargs.get('pk2', None))

        case_desactive.active = False

        case_desactive.save()

        update_comment = u'Se desactivó el caso {}'.format(case_desactive.number)

        update_event_type = EventType.objects.get(name=u'Actualización')

        event = OutgoingEvent.objects.create(comments=update_comment,
                                             event_type=update_event_type,
                                             created_by=self.request.user,
                                             requires_notification=False)

       
        event.cases.add(*case_main.container.get_cases_ids())

        event.cases.add(case_desactive.id)

        return HttpResponseRedirect(reverse_lazy('case_detail', args=[case_main.id]))    

class CaseUnmergeView(LoginRequiredMixin, ProtectUnmergeCaseMixin, RedirectView):
    http_method_names = ['get']
    update_comment = u'Se realizó una desconsolidación del siguiente caso: '
    def get_redirect_url(self, **kwargs):
        cache.clear()
        return reverse_lazy('case_detail',
                            args=[self.request.GET.get('case_pk')])

    def get(self, request, *args, **kwargs):

        date_submitted = time.strftime('%Y-%m-%d %I:%M:%S')

        user = request.user

        case_main = Case.objects.select_related().get(pk=kwargs.get('pk', None))
        case_unmerge = Case.objects.select_related().get(pk=kwargs.get('pk2', None))

        CaseContainer.unmerge_case(case_unmerge)

        self.update_comment += case_unmerge.number

        update_event_type = EventType.objects.get(name=u'Desconsolidación')

        event = OutgoingEvent.objects.create(comments=self.update_comment,
                                             event_type=update_event_type,
                                             created_by=self.request.user,
                                             requires_notification=False)

       
        event.cases.add(*case_main.container.get_cases_ids())

        event.cases.add(case_unmerge.id)




        # case_id_list = request.POST.getlist('selected_case')
        # action_seq = CaseContainerActionSequence.next('unmerge')

        # # setup task apply_sync kwargs
        # unmerge_cases_kwargs = {'case_id_list': case_id_list,
        #                         'username': user.username,
        #                         'action_seq': action_seq}

        # # send to celery unmerge task
        # unmerge_cases.apply_async(kwargs=unmerge_cases_kwargs, countdown=60)

        # msg_body = self.create_txt_email(action_seq, len(case_id_list), date_submitted)

        # msg_html_body = self.create_html_email(action_seq, len(case_id_list), date_submitted)

        # msg = EmailMultiAlternatives(subject='Pedido descosolidación: {}'.format(action_seq), body=msg_body,
        #                              from_email=settings.DEFAULT_EMAIL_FROM, to=[user.email])

        # msg.attach_alternative(content=msg_html_body, mimetype='text/html')
        # msg.send()

        #return super(CaseUnmergeView, self).post(request, *args, **kwargs)
        return HttpResponseRedirect(reverse_lazy('case_detail', args=[case_main.id]))    

    @staticmethod
    def create_html_email(action_seq, num_cases, date_submitted):
        """
        Formats the email body for a HTML email.
        :param action_seq:
        :param num_cases:
        :param date_submitted:
        :return:
        """
        return u"""
            <div style="max-width: 500px; min-width: 300px; font-family: helvetica, arial, sans-serif;margin: auto;">
                <p>Su desconsolidación es la: {}</p>
                <hr />
                <p>Esta tarea contiene <b>{} casos a ser deconsolidados</b></p>
                <p><b>Fecha Pedido:</b> {}</p>
            </div>
        """.format(action_seq, num_cases, date_submitted)

    @staticmethod
    def create_txt_email(action_seq, num_cases, date_submitted):
        """
        Formats the email body for a text email.
        :param action_seq:
        :param num_cases:
        :param date_submitted:
        :return:
        """
        return """
        Su desconsolidación es la: {}

        Esta tarea contiene {} casos a ser desconsolidados.

        Fecha Pedido: {}
        """.format(action_seq, num_cases, date_submitted)
