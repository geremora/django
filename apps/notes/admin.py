from django.contrib import admin

import reversion

from .models import Note


class NoteAdmin(reversion.VersionAdmin):
    list_display = ['content', 'date_updated', 'created_by', 'case']
    search_fields = ['content', 'case__number']

admin.site.register(Note, NoteAdmin)
