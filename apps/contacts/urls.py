from django.conf.urls import patterns, url
from .views import (
    ContactListView, ContactCreateView,
    ContactDetailView, ContactUpdateView, ContactDeleteView,
    contacts_ajax_search)

urlpatterns = patterns(
    '',  # Empty string as prefix

    url(r'^$', ContactListView.as_view(), name='contact_list'),
    url(r'^create/$', ContactCreateView.as_view(), name='contact_create'),
    url(r'^(?P<pk>\d+)/$', ContactDetailView.as_view(),
        name='contact_detail'),

    url(r'^update/(?P<pk>\d+)/$', ContactUpdateView.as_view(),
        name='contact_update'),

    url(r'^delete/(?P<pk>\d+)/$', ContactDeleteView.as_view(),
        name='contact_delete'),

    url(r'^ajax/$', contacts_ajax_search, name='contacts_ajax_search'),
)
