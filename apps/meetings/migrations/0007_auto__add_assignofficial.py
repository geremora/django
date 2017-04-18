# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AssignOfficial'
        db.create_table(u'meetings_assignofficial', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('assigned_official', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.CaspUser'])),
            ('assigned_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('assigned_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assigned_by', to=orm['profiles.CaspUser'])),
        ))
        db.send_create_signal(u'meetings', ['AssignOfficial'])


    def backwards(self, orm):
        # Deleting model 'AssignOfficial'
        db.delete_table(u'meetings_assignofficial')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'cases.case': {
            'Meta': {'ordering': "['date_created']", 'object_name': 'Case'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'assigned_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.CaspUser']", 'null': 'True', 'blank': 'True'}),
            'case_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cases.CaseCategory']"}),
            'case_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cases.CaseType']"}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['contacts.Contact']", 'null': 'True', 'through': u"orm['cases.ContactCaseRole']", 'blank': 'True'}),
            'container': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cases.CaseContainer']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'case_created_by'", 'to': u"orm['profiles.CaspUser']"}),
            'date_accepted': ('django.db.models.fields.DateTimeField', [], {}),
            'date_closed': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'defendant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'defendant_contact'", 'to': u"orm['contacts.Contact']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'did_confirm_case_type': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'extra': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'old_number': ('django.db.models.fields.CharField', [], {'max_length': '15', 'unique': 'True', 'null': 'True'}),
            'plaintiff': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'plaintiff_contact'", 'to': u"orm['contacts.Contact']"}),
            'record_holder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'case_record_holder'", 'db_index': 'False', 'to': u"orm['profiles.CaspUser']"}),
            'state': ('apps.cases.fields.MyFSMField', [], {'default': "'new'", 'max_length': '50'})
        },
        u'cases.casecategory': {
            'Meta': {'object_name': 'CaseCategory'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'cases.casecontainer': {
            'Meta': {'object_name': 'CaseContainer'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cases.Case']", 'null': 'True'})
        },
        u'cases.casetype': {
            'Meta': {'object_name': 'CaseType'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'cases.contactcaserole': {
            'Meta': {'object_name': 'ContactCaseRole'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cases.Case']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Contact']"}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.ContactRole']"})
        },
        u'contacts.contact': {
            'Meta': {'object_name': 'Contact'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'contact_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.ContactType']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'head_agency': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institutional_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'phone1': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'related_instutution': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contact_related_institution'", 'null': 'True', 'to': u"orm['contacts.Contact']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'contacts.contactrole': {
            'Meta': {'object_name': 'ContactRole'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'contacts.contacttype': {
            'Meta': {'object_name': 'ContactType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'meetings.assignofficial': {
            'Meta': {'ordering': "['-assigned_date']", 'object_name': 'AssignOfficial'},
            'assigned_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assigned_by'", 'to': u"orm['profiles.CaspUser']"}),
            'assigned_date': ('django.db.models.fields.DateTimeField', [], {}),
            'assigned_official': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.CaspUser']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'meetings.meeting': {
            'Meta': {'ordering': "['-date_created']", 'object_name': 'Meeting'},
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cases.Case']", 'null': 'True', 'blank': 'True'}),
            'cases': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'meeting_cases'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['cases.Case']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.CaspUser']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_end': ('django.db.models.fields.DateTimeField', [], {}),
            'date_start': ('django.db.models.fields.DateTimeField', [], {}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['meetings.Room']"}),
            'somebody_armed': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'scheduled'", 'max_length': '50'})
        },
        u'meetings.meetingattendee': {
            'Meta': {'object_name': 'MeetingAttendee'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.Contact']"}),
            'did_show_up': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['meetings.Meeting']"})
        },
        u'meetings.room': {
            'Meta': {'ordering': "['name']", 'object_name': 'Room'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'profiles.caspuser': {
            'Meta': {'object_name': 'CaspUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['meetings']