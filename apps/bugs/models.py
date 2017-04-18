# -*- coding: utf-8 -*-
from django.db import models


class Bug(models.Model):
    message = models.TextField()
    created_by = models.ForeignKey('profiles.CaspUser')
    date_created = models.DateTimeField(auto_now_add=True)
    bug_type = models.CharField(max_length=50,
                                choices=(('correction', u'Solicitar Corrección'),
                                         ('bug', 'Bug'),
                                         ('feature', 'Feature')))

    def __unicode__(self):
        return self.message
