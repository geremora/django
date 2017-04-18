# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError



class Contact(models.Model):
    '''
    Contact model, contact_type is the only required field
    '''
    institutional_name = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    related_instutution = models.ForeignKey('self', blank=True, null=True,
                                            limit_choices_to={'contact_type__id': 1},
                                            related_name='contact_related_institution')
    email = models.EmailField(blank=True)
    phone1 = models.CharField(max_length=60)
    phone2 = models.CharField(max_length=60, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=60)
    state = models.CharField(max_length=60)
    zip_code = models.CharField(max_length=60)
    contact_type = models.ForeignKey('ContactType')
    head_agency = models.CharField(max_length=60, blank=True) #Only for contact_ty Agencia
    notes = models.TextField(blank=True)

    

    def __unicode__(self):
        return self.get_name()

    def clean(self):
        # Check if we have (institutional_name) or (first_name and last_name)
        if not self.institutional_name and (not self.first_name
                                            or not self.last_name):
            raise ValidationError('Institutional name or \
                                  first and last name required')
    def get_friendly_info(self):
        return self.get_name() + ' ' + '(' + self.contact_type.name + ')'

    def get_name(self):
        # Get's the name of the Contact it prefers the institutional_name
        if self.institutional_name == '':
            return u'{} {}'.format(self.first_name, self.last_name)
        else:
            return u'{}'.format(self.institutional_name)

    def has_email(self):
        # Whether or not the Contact has an email address assigned
        if self.email == '':
            return False
        return True

    def get_url(self):
        return reverse('contact_detail', kwargs={'pk': self.id})


class ContactRole(models.Model):
    '''
    Types of contact role in case
    '''
    name = models.CharField(max_length=60)

    def __unicode__(self):
        return self.name

class ContactType(models.Model):
    '''
    Types of contacts
    '''
    name = models.CharField(max_length=60)

    def __unicode__(self):
        return self.name
