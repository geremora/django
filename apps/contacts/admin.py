from django.contrib import admin

import reversion

from .models import Contact, ContactType

'''
The use of reversion.VersionAdmin as a base class for the admin
is to get version control functionality on all objects.
'''


class ContactAdmin(reversion.VersionAdmin):
    list_display = ('get_name', 'contact_type', 'email')
    search_fields = ['institutional_name', 'first_name', 'last_name',
                     'email', 'phone1', 'phone2', 'city', 'state',
                     'contact_type__name']
    list_filter = ('contact_type__name',)

    merge_list_display = (
        'institutional_name',
        'first_name',
        'last_name',
        'email',
        'phone1',
        'phone2',
        'address',
        'city',
        'state',
        'contact_type'
    )

    def get_name(self, obj):
        return obj.get_name()
    get_name.short_description = 'Name'


class ContactTypeAdmin(reversion.VersionAdmin):
    pass

admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactType, ContactTypeAdmin)
