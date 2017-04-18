# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Meeting.case'
        db.alter_column(u'meetings_meeting', 'case_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cases.Case'], null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Meeting.case'
        raise RuntimeError("Cannot reverse this migration. 'Meeting.case' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Meeting.case'
        db.alter_column(u'meetings_meeting', 'case_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cases.Case']))

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
            'assigned_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['profiles.CaspUser']", 'null': 'True', 'blank': 'True'}),
            'case_category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cases.CaseCategory']"}),
            'case_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cases.CaseType']"}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['contacts.Contact']", 'null': 'True', 'blank': 'True'}),
            'container': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cases.CaseContainer']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'case_created_by'", 'to': u"orm['profiles.CaspUser']"}),
            'date_accepted': ('django.db.models.fields.DateTimeField', [], {}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'defendant': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'defendant_contact'", 'to': u"orm['contacts.Contact']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'did_confirm_case_type': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'extra': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'plaintiff': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'plaintiff_contact'", 'to': u"orm['contacts.Contact']"}),
            'record_holder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'case_record_holder'", 'to': u"orm['profiles.CaspUser']"}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'cases.casetype': {
            'Meta': {'object_name': 'CaseType'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contacts.contact': {
            'Meta': {'object_name': 'Contact'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'contact_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contacts.ContactType']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
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
            'Meta': {'object_name': 'Room'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'profiles.caspuser': {
            'Meta': {'object_name': 'CaspUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['meetings']