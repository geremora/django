from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy

from django.contrib import admin
from apps.meetings.views import CalendarView,CalendarDayView, CalendarJsonListView, meeting_json, AssignOfficialCreateView, AssignOfficialUpdateView, AssignOfficialDeleteView

from apps.profiles.forms import CaspUserPasswordChangeForm, CaspAuthForm
from apps.utils.actions import merge_selected

admin.autodiscover()

# register all Admin Actions
admin.site.add_action(merge_selected)


urlpatterns = patterns(
    '',  # Empty string as prefix

    # Root
    url(r'^$', RedirectView.as_view(url=reverse_lazy('case_list'))),

    # Login
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'authentication_form': CaspAuthForm}, name='login'),

    # Logout
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': reverse_lazy('login')}, name='logout'),

    # External password reset
    url(r'^accounts/password/reset/$',
        'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^accounts/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    url(r'^accounts/password/reset/complete/$',
        'django.contrib.auth.views.password_reset_complete', name='password_reset_complete'),
    url(r'^account/password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),

    # Change password
    url(r'^accounts/password/$', 'django.contrib.auth.views.password_change',
        {'post_change_redirect': reverse_lazy('profile_detail'),
        'password_change_form': CaspUserPasswordChangeForm},
        name='password_change'),

    # Favicon
    url(r'^favicon.ico/$',
        RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),

    # iOS icon
    url(r'^apple-touch-icon.png/$',
        RedirectView.as_view(url=settings.STATIC_URL + 'apple-touch-icon.png')),

    # robots.txt
    url(r'^robots.txt/$',
        RedirectView.as_view(url=settings.STATIC_URL + 'robots.txt')),

    # crossdomain.xml
    url(r'^crossdomain.xml/$',
        RedirectView.as_view(url=settings.STATIC_URL + 'crossdomain.xml')),

    # humans.txt
    url(r'^humans.txt/$',
        RedirectView.as_view(url=settings.STATIC_URL + 'humans.txt')),


    # Contacts
    url(r'^contacts/', include('apps.contacts.urls')),

    # Profiles
    url(r'^profiles/', include('apps.profiles.urls')),

    # Cases
    url(r'^cases/', include('apps.cases.urls')),

    # Events
    url(r'^cases/(?P<pk>\d+)/events/', include('apps.events.urls')),

     # Events
    url(r'^events/', include('apps.events.urls')),

    # Meetings
    url(r'^cases/(?P<pk>\d+)/meetings/', include('apps.meetings.urls')),

    # Meetings Calendar
    url(r'^calendar/json/$', CalendarJsonListView.as_view(), name='calendar_json'),
    # url(r'^calendar/json/$', meeting_json, name='calendar_json'),
    url(r'^calendar/', CalendarView.as_view(), name="meeting_calendar"),
    url(r'^calendarmonitor/', CalendarDayView.as_view(), name="meeting_calendar_day"),

    # url(r'^calendar/', include('apps.meetings_calendar.urls')),
    # url(r'^calendar/', include('django_bootstrap_calendar.urls')),

    # Assign Official
    url(r'^assignOfficial/$', AssignOfficialCreateView.as_view(), name='assign_official'),
    url(r'^assignOficial/(?P<pk>\d+)/update/$',
        AssignOfficialUpdateView.as_view(), name='assign_official_update'),
    url(r'^assignOficial/(?P<pk>\d+)/delete/$',
        AssignOfficialDeleteView.as_view(), name='assign_official_delete'),

    # Notes
    url(r'^cases/(?P<pk>\d+)/notes/', include('apps.notes.urls')),

    # Documents
    url(r'^cases/(?P<pk>\d+)/documents/', include('apps.documents.urls')),

    # Bugs
    url(r'^bugs/', include('apps.bugs.urls')),

    # Admin interface
    url(r'^admin/', include(admin.site.urls)),

    url(r'^reports/', include('apps.reports.urls')),
    url(r'^perms/', include('apps.perms.urls')),
)

# Serve statics during development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
