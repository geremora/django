from django.db import models
from django.conf import settings
import time
from ..utils.permissions import get_custom_permissions

class Document(models.Model):
    case = models.ForeignKey('cases.Case')
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    document_type = models.ForeignKey('DocumentType', null=True, blank=True)

    class Meta:
        ordering = ['-date_updated']
        # permissions = get_custom_permissions(
        #     'note', ['add', 'change', 'delete', 'view_all'])

    def __unicode__(self):
        return u'{}...'.format(self.content[:60])

    def get_object_type(self):
        return self.__class__.__name__

    def documents(self):
        return self.content

    def can_view(self, user):
        '''
        Check if the passed user can view the current note.
        Notes can be viewed by its creator, the case's assigned user
        or users in the supervisor group.
        '''
        # if user in [self.created_by, self.case.assigned_user] or user.has_perm('notes.can_view_all_notes'):
        return True

class DocumentType(models.Model):
    name = models.CharField(max_length=60, db_index=True)
    description = models.TextField(blank=True)
    case_type = models.ManyToManyField(
        'cases.CaseType', null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_template_name(self):
        name = self.name.lower().replace(' ', '_')
        name = name + ".docx"
        #name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')

        return name
        
    def get_download_file_name(self, caseNumber):
        name = self.name.lower().replace(' ', '_')
        name = time.strftime("%Y%m%d-%H%M%S") + ' - '  + caseNumber + ' - ' + name
        name = name + ".docx"
        #name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')

        return name