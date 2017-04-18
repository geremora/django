from django.conf.urls import patterns, url

from .views import NoteCreateView

urlpatterns = patterns(
    '',  # Empty string as prefix

    url(r'^create/$',
        NoteCreateView.as_view(), name='note_create'),

   



    # url(r'^(?P<note_pk>\d+)/update/$',
        # NoteUpdateView.as_view(), name='note_update'),

)
