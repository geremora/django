# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from ..utils.permissions import get_custom_permissions
from ..profiles.models import CaspUser


class Room(models.Model):
    name = models.CharField(max_length=50)
    location = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

CHOICES = (
    (None, "Se desconoce"),
    (True, "Si"),
    (False, "No")
)

class Meeting(models.Model):
    case = models.ForeignKey('cases.Case', blank=True, null=True)
    cases = models.ManyToManyField('cases.Case', null=True, blank=True,
                                   related_name='meeting_cases')
    room = models.ForeignKey('Room')
    notes = models.TextField(blank=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    meeting_type = models.CharField(max_length=50, choices=(
                                    ('status', 'Vista de Estatus'),
                                    ('arbitraje', 'Vista de Arbitraje'),
                                    ('continuacion', u'Continuación de Vista'),
                                    ('mediacion', u'Sesión de Medición')))
    status = models.CharField(max_length=50, default='scheduled', choices=(
                              ('did_happen', u'Se celebró'),
                              ('cancelled', u'Se canceló'),
                              ('scheduled', 'Pautada')))
    somebody_armed = models.NullBooleanField(blank=True, null=True, choices=CHOICES)

    class Meta:
        ordering = ['-date_created']
        permissions = get_custom_permissions('meeting')

    def __unicode__(self):
        return u'{} en {}'.format(self.date_start, self.room.name)

    def get_object_type(self):
        return self.__class__.__name__

    def clean(self):
        # Check for overlapping meetings
        # Reference: http://c2.com/cgi/wiki?TestIfDateRangesOverlap

        if self.date_start and self.date_end:
            overlapping_meetings = Meeting.objects.filter(
                date_end__gte=self.date_start,
                date_start__lte=self.date_end,
                room=self.room).exclude(pk=self.pk).exclude(status='cancelled').exclude(status='did_happen').count()

            if overlapping_meetings > 0:
                raise ValidationError('Overlapping meetings')

    def get_attendees(self):
        return MeetingAttendee.objects.select_related('meeting', 'contact').filter(meeting=self)


class MeetingAttendee(models.Model):
    meeting = models.ForeignKey('Meeting')
    contact = models.ForeignKey('contacts.Contact')
    did_show_up = models.NullBooleanField()

    class Meta:
        permissions = get_custom_permissions('meeting_attendee')

    def __unicode__(self):
        return self.contact.get_name()

    def get_name(self):
        return self.contact.get_name()

class AssignOfficial(models.Model):
    assigned_official = models.ForeignKey(settings.AUTH_USER_MODEL)
    assigned_date = models.DateTimeField()
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_by')

    class Meta():
        ordering = ['-assigned_date']

    def clean(self):

        if self.assigned_date:
            already_assigned = AssignOfficial.objects.filter(
                assigned_date=self.assigned_date.strftime('%Y-%m-%d')).exclude(pk=self.pk)

            if already_assigned.exists():
                raise ValidationError('Date already assigned')

