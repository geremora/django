from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse

from django.views.generic import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.cache import cache

from braces.views import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from apps.meetings.serializers import meeting_serializer
from apps.meetings.utils import timestamp_to_datetime

from .models import Meeting, AssignOfficial
from ..cases.models import Case
from .forms import (MeetingCreationForm,
                    MeetingUpdateForm, MeetingAttendanceForm, AssignOfficialForm)
from .mixins import (ProtectMeetingCreateMixin,
                     ProtectMeetingUpdateMixin,
                     ProtectMeetingAttendanceUpdateMixin,
                     ProtectAssignOfficialCreateMixin,
                     ProtectAssignOfficialUpdateMixin,
                     ProtectAssignOfficialDeleteMixin)

import logging
logger = logging.getLogger(__name__)

def meeting_json(request):
    queryset = Meeting.objects.all()
    from_date = request.GET.get('from', False)
    to_date = request.GET.get('to', False)

    if from_date and to_date:
        queryset = queryset.filter(
            date_start__range=(
                timestamp_to_datetime(from_date) + timedelta(-30),
                timestamp_to_datetime(to_date)
                )
        )
    elif from_date:
        queryset = queryset.filter(date_start__gte=timestamp_to_datetime(from_date))
    elif to_date:
        queryset = queryset.filter(date_end__lte=timestamp_to_datetime(to_date))

    queryset_json = meeting_serializer(queryset)

    return queryset_json


class MeetingCreateView(LoginRequiredMixin, ProtectMeetingCreateMixin, CreateView):

    '''
    Creates a meeting for the current case
    '''
    model = Meeting
    form_class = MeetingCreationForm

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.kwargs['pk']])

    def get_initial(self):
        # Pre-fill form with case and created_by user
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

        return {
            'case': self.case,
            'created_by': self.request.user,
            'attendees': self.case.get_all_contacts(id_only=True)
        }

    def get_context_data(self, *args, **kwargs):
        context = super(
            MeetingCreateView, self).get_context_data(**kwargs)

        # Add case to context, used by cancel button link
        context['case'] = self.case
        return context


class MeetingUpdateView(LoginRequiredMixin, ProtectMeetingUpdateMixin, UpdateView):
    model = Meeting
    form_class = MeetingUpdateForm
    pk_url_kwarg = 'meeting_pk'

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.case.pk])

    def get_initial(self):
        initial = super(MeetingUpdateView, self).get_initial()

        # Pre-fill form with case and created_by user
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

        # Gets the ids of existing attendees to pre-select them on the form
        initial['attendees'] = [
            a.contact.id for a in self.object.get_attendees()]

        return initial

    def get_context_data(self, *args, **kwargs):
        context = super(MeetingUpdateView, self).get_context_data(**kwargs)

        # Add case to context, used by cancel button link
        context['case'] = self.case
        return context


class MeetingAttendanceView(LoginRequiredMixin, ProtectMeetingAttendanceUpdateMixin, UpdateView):
    model = Meeting
    form_class = MeetingAttendanceForm
    pk_url_kwarg = 'meeting_pk'

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.case.pk])

    def get_initial(self):
        initial = super(MeetingAttendanceView, self).get_initial()

        # Pre-fill form with case and created_by user
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

        initial['attendees'] = self.object.get_attendees()

        return initial

    def get_context_data(self, *args, **kwargs):
        context = super(MeetingAttendanceView, self).get_context_data(**kwargs)

        # Add case to context, used by cancel button link
        context['case'] = self.case
        return context


class CalendarJsonListView(LoginRequiredMixin, ListView):
    template_name = 'calendar/calendar_events.html'

    def get_queryset(self):
        queryset = Meeting.objects.all().exclude(status='cancelled')
        from_date = self.request.GET.get('from', False)
        to_date = self.request.GET.get('to', False)
        show_all = self.request.GET.get('view', None)
        user = self.request.user
        
        if from_date and to_date:
            assigned_officials_queryset = AssignOfficial.objects.all()
            queryset = queryset.filter(
                date_start__range=(
                    timestamp_to_datetime(from_date) + timedelta(-30),
                    timestamp_to_datetime(to_date))
            )
            assigned_officials_queryset = assigned_officials_queryset.filter(
                assigned_date__range=(timestamp_to_datetime(from_date) + timedelta(-30),
                    timestamp_to_datetime(to_date))
            )
        elif from_date:
            queryset = queryset.filter(
                date_start__gte=timestamp_to_datetime(from_date)
            )
            assigned_officials_queryset = assigned_officials_queryset.filter(
                assigned_date__gte=timestamp_to_datetime(from_date)
            )
        elif to_date:
            queryset = queryset.filter(
                date_end__lte=timestamp_to_datetime(to_date)
            )
            assigned_officials_queryset = assigned_officials_queryset.filter(
                assigned_date__lte=timestamp_to_datetime(from_date)
            )

        if show_all is None:
            queryset = queryset.filter(cases__assigned_user=user)

        return meeting_serializer(queryset, assigned_officials_queryset, self.request.user)


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'calendar/calendar.html'

    def get_context_data(self):
        show_all = self.request.GET.get('view', None)
        context = super(CalendarView, self).get_context_data()

        context['events_url'] = reverse('calendar_json')
        
        if show_all:
            context['events_url'] = context['events_url'] + '?view=all'

        return context

class CalendarDayView(TemplateView):
    template_name = 'calendar/calendarday.html'

    def get_context_data(self):
        context = super(CalendarDayView, self).get_context_data()

        context['events_url'] = reverse('meeting_calendar_day') + '?view=all'

        print context['events_url'] 

        return context

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('view', None):
            queryset = Meeting.objects.all().exclude(status='cancelled')
            from_date = self.request.GET.get('from', False)
            to_date = self.request.GET.get('to', False)
            show_all = self.request.GET.get('view', None)
            user = self.request.user
            
            if from_date and to_date:
                assigned_officials_queryset = AssignOfficial.objects.all()
                queryset = queryset.filter(
                    date_start__range=(
                        timestamp_to_datetime(from_date) + timedelta(-30),
                        timestamp_to_datetime(to_date))
                )
                assigned_officials_queryset = assigned_officials_queryset.filter(
                    assigned_date__range=(timestamp_to_datetime(from_date) + timedelta(-30),
                        timestamp_to_datetime(to_date))
                )

            return HttpResponse(meeting_serializer(queryset, assigned_officials_queryset, self.request.user))

        return super(CalendarDayView, self).get(request, *args, **kwargs)

class AssignOfficialCreateView(LoginRequiredMixin,ProtectAssignOfficialCreateMixin, CreateView):
    '''
    Assigns Official to specific dates in calendar
    '''
    model = AssignOfficial
    form_class = AssignOfficialForm

    def get_success_url(self):
        cache.clear()
        return reverse('meeting_calendar')

    def get_initial(self):
        # Pre-fill form with assigned_by user

        return {
            'assigned_by': self.request.user,
        }

class AssignOfficialUpdateView(LoginRequiredMixin, ProtectAssignOfficialUpdateMixin, UpdateView):

    '''
    Update Assign Official information
    '''
    model = AssignOfficial
    form_class = AssignOfficialForm

    def get_success_url(self):
        # Send to contact_detail when saved
        return reverse_lazy('meeting_calendar')
        
    def get_initial(self):
        # Pre-fill form with assigned_by user

        return {
            'assigned_by': self.request.user,
        }


class AssignOfficialDeleteView(LoginRequiredMixin, ProtectAssignOfficialDeleteMixin, DeleteView):

    '''
    Delete AssignOfficial
    '''
    model = AssignOfficial
    success_url = reverse_lazy('meeting_calendar')

    def get(self, *args, **kwargs):
        """
        This has been overriden because by default
        DeleteView doesn't work with GET requests
        """
        return self.delete(*args, **kwargs)
