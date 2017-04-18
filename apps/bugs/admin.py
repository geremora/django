from django.contrib import admin

from .models import Bug


class BugAdmin(admin.ModelAdmin):
    list_display = ['message', 'created_by', 'date_created']
    search_fields = ['message', 'bug_type']

admin.site.register(Bug, BugAdmin)
