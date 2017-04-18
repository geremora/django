# -*- coding: utf-8 -*-
from django.contrib.auth.models import AbstractUser
from django.db import models


class CaspUser(AbstractUser):
    """
    Defines our custom user model and fields
    """
    phone = models.CharField(max_length=60, blank=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __unicode__(self):
        return self.get_full_name()

    def get_short_name(self):
        return u'{}. {}'.format(self.first_name[0], self.last_name)

    def can_view_reports(self):
        return self.has_perms('can_view_reports')
