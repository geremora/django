# -*- coding: utf-8 -*-

import unicodedata
import uuid
import os

from boto.s3.bucket import Bucket
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from django.db import models
from django.utils.timezone import now
from django.conf import settings

from ..utils.db import HTMLField
from ..utils.permissions import get_custom_permissions

CHOICES = (
    (None, "Se desconoce"),
    (True, "Si"),
    (False, "No")
)


def get_user_upload_path(instance, filename):
    identifier = str(uuid.uuid4())
    return os.path.join('uploads', identifier, filename)


class BaseEvent(models.Model):
    '''
    Defines the common fields for all event models
    '''
    class Meta:
        abstract = True
        ordering = ['-date_created']

    cases = models.ManyToManyField('cases.Case', null=True, blank=True)
    comments = models.TextField(blank=True)
    attached_file = models.CharField(max_length=256, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    requires_terms = models.BooleanField(default=False)
    date_terms_expiration = models.DateTimeField(null=True, blank=True)
    date_emitted = models.DateTimeField(null=True, blank=True)
    date_notification = models.DateTimeField(null=True, blank=True)
    requires_acceptance = models.BooleanField(default=False)
    accepted = models.NullBooleanField(choices=CHOICES)
    requires_notification = models.BooleanField(default=True)
    generate_by = models.ForeignKey('contacts.Contact', null=True, blank=True)
    party = models.ForeignKey('EventCaseParty', null=True, blank=True)

    def __unicode__(self):
        return u'{}'.format(self.event_type.name)

    def get_attached_file_url(self):
        if self.attached_file:
            conn = S3Connection(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                is_secure=True)
            bucket = Bucket(conn, settings.AWS_MEDIA_BUCKET_NAME)
            fileKey = Key(bucket, self.attached_file)
            return fileKey.generate_url(600)
        return None

    def terms_expiration_date(self):
        return self.date_terms_expiration or None

    def notification_date(self):
        return self.date_notification or None

    def get_object_type(self):
        return self.__class__.__name__

    def get_template_name(self):
        return self.event_type.get_template_name()



class IncomingEvent(BaseEvent):
    event_type = models.ForeignKey('EventType',
                                   limit_choices_to={'direction': 'in'})
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='incoming_created_by')

    # Used to indicate if the event has been taken care of (atendido)
    date_observed = models.DateTimeField(null=True, blank=True)
    observed_notes = models.TextField(blank=True)

    related_event = models.ForeignKey('OutgoingEvent', null=True, blank=True)

    class Meta:
        permissions = get_custom_permissions('incoming_event')

    def was_observed(self):
        '''
        Indicates if the event has taken care of (atendido)
        '''
        if self.date_observed:
            return True
        return False

    def terms_expired(self):
        if self.was_observed():
            return False
        elif self.requires_terms and self.terms_expiration_date() < now():
            return True

    def get_friendly_info(self):
        return self.event_type.name + ' ' + '(' + self.date_created.strftime("%d/%m/%y") + ')'


class OutgoingEvent(BaseEvent):
    document_content = HTMLField(blank=True)
    event_type = models.ForeignKey('EventType',
                                   limit_choices_to={'direction': 'out'})
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='outgoing_created_by')

    related_event = models.ForeignKey('IncomingEvent', null=True, blank=True)

    class Meta:
        permissions = get_custom_permissions('outgoing_event')

    def terms_expired(self):
        '''
        Returns True if the date_created + terms_in_days is equal or greater
        than the current datetime.
        '''
        return self.requires_terms and self.terms_expiration_date() < now()

    def notification_expired(self):
        if self.date_notification():
            return False
        elif self.date_notification() < now():
            return True
    def get_friendly_info(self):
        return self.event_type.name + ' ' + '(' + self.date_created.strftime("%d/%m/%y") + ')'


class EventCaseParty(models.Model):
    '''
    Types of party in a event case
    '''
    name = models.CharField(max_length=60)

    def __unicode__(self):
        return self.name

class EventType(models.Model):
    name = models.CharField(max_length=60, db_index=True)
    description = models.TextField(blank=True)
    case_type = models.ManyToManyField(
        'cases.CaseType', null=True, blank=True)
    direction = models.CharField(
        max_length=10,
        choices=(('in', 'Incoming'), ('out', 'Outgoing')))
    allowedCaseClosed = models.BooleanField(default=False)
    requires_terms = models.BooleanField(default=False)
    requires_acceptance = models.BooleanField(default=False)
    requires_notification = models.BooleanField(default=False)
    isPublic = models.BooleanField(default=True)
    requires_parties = models.BooleanField(default=False)
    requires_generate_by = models.BooleanField(default=False)
    amount_days_terms = models.IntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_template_name(self):
        name = self.name.lower().replace(' ', '_')
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')

        return 'docs/{}.html'.format(name)


class ImportedEvent(models.Model):
    case = models.ForeignKey('cases.Case')
    event_type = models.CharField(max_length=50)
    description = models.TextField()
    is_published = models.BooleanField(default=False)
    date_created = models.DateTimeField()

    class Meta:
        ordering = ['-date_created']
        permissions = get_custom_permissions('imported_event')

    def __unicode__(self):
        return u'{}: {}'.format(self.event_type, self.description)

    def get_object_type(self):
        return self.__class__.__name__

