from django.conf.urls import patterns, url
from .views import BugsCreateView

urlpatterns = patterns(
    '',  # Empty string as prefix

    url(r'^create/$', BugsCreateView.as_view(), name='bug_create'),
)
