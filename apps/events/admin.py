'''
The use of reversion.VersionAdmin as a base class for the admin
is to get version control functionality on all objects. CaseEventFieldAdmin
is not using this funcionality since it's controlled by code and not users.
'''


from django.contrib import admin

import reversion

from .models import IncomingEvent, OutgoingEvent, EventType, ImportedEvent


class EventAdmin(reversion.VersionAdmin):
    list_display = ['event_type', 'get_case_number', 'created_by', 'date_created']
    search_fields = ['event_type__name', 'cases__number']
    raw_id_fields = ('cases',)

    # https://docs.djangoproject.com/en/1.5/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display
    def get_case_number(self, obj):
        return "\n".join([c.number for c in obj.cases.all()])

    get_case_number.short_description = 'case'


class EventTypeAdmin(reversion.VersionAdmin):
    list_display = ['name', 'direction']
    list_filter = ('direction',)
    search_fields = ['name']
    raw_id_fields = ('case_type',)


class ImportedEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'case', 'description', 'date_created']
    list_filter = ('event_type',)
    search_fields = ['event_type', 'case__number', 'description']


admin.site.register(IncomingEvent, EventAdmin)
admin.site.register(OutgoingEvent, EventAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(ImportedEvent, ImportedEventAdmin)
