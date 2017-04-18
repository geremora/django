'''
The use of reversion.VersionAdmin as a base class for the admin
is to get version control functionality on all objects. CaseEventFieldAdmin
is not using this funcionality since it's controlled by code and not users.
'''


from django.contrib import admin

import reversion

from .models import CaseContainer, Case, CaseType, CaseCategory, CaseSequence


class CaseContainerAdmin(reversion.VersionAdmin):
    pass


class CaseAdmin(reversion.VersionAdmin):
    list_display = ['number', 'description', 'defendant', 'case_category']
    search_fields = ['number', 'description',
                     'defendant__first_name', 'defendant__last_name',
                     'case_category__name']
    raw_id_fields = ('contacts', 'case_category', 'case_type')


class CaseCategoryAdmin(admin.ModelAdmin):
    pass


class CaseSequenceAdmin(admin.ModelAdmin):
    list_display = ('case_type', 'year', 'last_id')


admin.site.register(CaseContainer, CaseContainerAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(CaseType)
admin.site.register(CaseCategory, CaseCategoryAdmin)
admin.site.register(CaseSequence, CaseSequenceAdmin)
