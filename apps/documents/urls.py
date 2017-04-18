from django.conf.urls import patterns, url

from .views import DocumentCreateView

urlpatterns = patterns(
    '',  # Empty string as prefix

    url(r'^create/$',
        DocumentCreateView.as_view(), name='document_create'),

    # url(r'^(?P<note_pk>\d+)/update/$',
        # NoteUpdateView.as_view(), name='note_update'),

)
