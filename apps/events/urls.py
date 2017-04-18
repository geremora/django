from django.conf.urls import patterns, url
from .views import (
    IncomingEventCreateView, OutgoingEventCreateView,
    IncomingEventUpdateObservingView, OutgoingEventUpdateAcceptanceView,
    IncomingEventUpdateAcceptanceView, ImportedEventUpdateView,
    OutgoingEventUpdateNotifyingView, OutgoingEventDocumentView,
    IncomingEventDetailView,OutgoingEventDetailView, event_type_ajax_get)

urlpatterns = patterns(
    '',  # Empty string as prefix

    url(r'^create/incoming/$',
        IncomingEventCreateView.as_view(), name='create_incoming_event'),

    url(r'^create/outgoing/$',
        OutgoingEventCreateView.as_view(), name='create_outgoing_event'),

    url(r'^(?P<event_pk>\d+)/document/$',
        OutgoingEventDocumentView.as_view(),
        name='preview_outgoing_event_document'),


    # url(r'^(?P<event_pk>\d+)/document/(?P<print>(print))/$',
    #     OutgoingEventDocumentView.as_view(),
    #     name='print_outgoing_event_document'),


    url(r'^(?P<pk>\d+)/in/$', IncomingEventDetailView.as_view(),
        name='incoming_event_detail'),

    url(r'^(?P<pk>\d+)/out/$', OutgoingEventDetailView.as_view(),
        name='outgoing_event_detail'),

    url(r'^(?P<event_pk>\d+)/update/out/acceptance/$',
        OutgoingEventUpdateAcceptanceView.as_view(),
        name='update_outgoing_event_acceptance'),

    url(r'^(?P<event_pk>\d+)/update/in/acceptance/$',
        IncomingEventUpdateAcceptanceView.as_view(),
        name='update_incoming_event_acceptance'),

    url(r'^(?P<event_pk>\d+)/update/observed/$',
        IncomingEventUpdateObservingView.as_view(),
        name='update_incoming_event_observed'),

    url(r'^(?P<event_pk>\d+)/update/imported/$',
        ImportedEventUpdateView.as_view(),
        name='update_imported_event'),

    url(r'^(?P<event_pk>\d+)/update/notified/$',
    OutgoingEventUpdateNotifyingView.as_view(),
    name='update_outgoing_event_notified'),

    url(r'^ajax/$', event_type_ajax_get, name='event_type_ajax_get'),
)
