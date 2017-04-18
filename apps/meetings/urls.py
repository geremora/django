from django.conf.urls import patterns, url

from .views import MeetingCreateView, MeetingUpdateView, MeetingAttendanceView

urlpatterns = patterns(
    '',  # Empty string as prefix

    url(r'^create/$', MeetingCreateView.as_view(), name='meeting_create'),
    url(r'^(?P<meeting_pk>\d+)/update/$',
        MeetingUpdateView.as_view(), name='meeting_update'),
    url(r'^(?P<meeting_pk>\d+)/update/attendance/$',
        MeetingAttendanceView.as_view(), name='meeting_attendance'),
)
