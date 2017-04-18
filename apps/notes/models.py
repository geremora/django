# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings

from ..events.models import IncomingEvent, OutgoingEvent

from ..utils.permissions import get_custom_permissions


class Note(models.Model):
    case = models.ForeignKey('cases.Case')
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    related_outgoing_event = models.ForeignKey('events.OutgoingEvent', null=True, blank=True)

    related_incoming_event = models.ForeignKey('events.IncomingEvent', null=True, blank=True)

    class Meta:
        ordering = ['-date_updated']
        permissions = get_custom_permissions(
            'note', ['add', 'change', 'delete', 'view_all'])

    def __unicode__(self):
        return u'{}...'.format(self.content[:60])

    def get_object_type(self):
        return self.__class__.__name__

    def notes(self):
        return self.content

    def can_view(self, user):
        '''
        Check if the passed user can view the current note.
        Notes can be viewed by its creator, the case's assigned user
        or users in the supervisor group.
        '''
        if user in [self.created_by, self.case.assigned_user] or user.has_perm('notes.can_view_all_notes'):
            return True
