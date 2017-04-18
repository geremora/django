from django.contrib import admin

import reversion

from .models import Room, Meeting, MeetingAttendee, AssignOfficial

'''
The use of reversion.VersionAdmin as a base class for the admin
is to get version control functionality on all objects.
'''


class RoomAdmin(reversion.VersionAdmin):
    pass


class MeetingAdmin(reversion.VersionAdmin):
    list_display = ['room', 'status', 'date_start', 'date_end']
    search_fields = ['room__name', 'case__number']
    raw_id_fields = ('case', 'cases')


class MeetingAttendeeAdmin(reversion.VersionAdmin):
    list_display = ['contact', 'meeting', 'did_show_up']
    search_fields = ['contact__first_name', 'contact__last_name']


admin.site.register(Room, RoomAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(MeetingAttendee, MeetingAttendeeAdmin)
admin.site.register(AssignOfficial)
