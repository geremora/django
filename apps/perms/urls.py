from django.conf.urls import patterns, url
from .views import (
    PermsUserListView, PermsUserDetailView,
    PermsUserUpdateView, PermsUserRequestView
)


urlpatterns = patterns('',
   url(r'^users/$', PermsUserListView.as_view(), name='perms-user-list'),
   url(r'^users/(?P<pk>\d+)/$', PermsUserDetailView.as_view(), name='perms-user-detail'),
   url(r'^users/(?P<pk>\d+)/update/$', PermsUserUpdateView.as_view(), name='perms-user-update'),
   url(r'^users/(?P<pk>\d+)/request/$', PermsUserRequestView.as_view(), name='perms-user-request')
)
