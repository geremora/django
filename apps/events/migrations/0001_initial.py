# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IncomingEvent'
        db.create_table(u'events_incomingevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cases.Case'])),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('attached_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('requires_terms', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('terms_in_days', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('terms_type', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('requires_acceptance', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('accepted', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('group_uuid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('event_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.EventType'])),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='incoming_created_by', to=orm['profiles.CaspUser'])),
            ('date_observed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'events', ['IncomingEvent'])

        # Adding model 'OutgoingEvent'
        db.create_table(u'events_outgoingevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cases.Case'])),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('attached_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('requires_terms', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('terms_in_days', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('terms_type', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('requires_acceptance', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('accepted', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('group_uuid', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('document_content', self.gf('apps.utils.db.HTMLField')(blank=True)),
            ('event_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.EventType'])),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='outgoing_created_by', to=orm['profiles.CaspUser'])),
        ))
        db.send_create_signal(u'events', ['OutgoingEvent'])

        # Adding model 'EventType'
        db.create_table(u'events_eventtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('direction', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'events', ['EventType'])

        # Adding M2M table for field case_type on 'EventType'
        db.create_table(u'events_eventtype_case_type', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('eventtype', models.ForeignKey(orm[u'events.eventtype'], null=False)),
            ('casetype', models.ForeignKey(orm[u'cases.casetype'], null=False))
        ))
        db.create_unique(u'events_eventtype_case_type', ['eventtype_id', 'casetype_id'])


    def backwards(self, orm):
        # Deleting model 'IncomingEvent'
        db.delete_table(u'events_incomingevent')

        # Deleting model 'OutgoingEvent'
        db.delete_table(u'events_outgoingevent')

        # Deleting model 'EventType'
        db.delete_table(u'events_eventtype')

        # Removing M2M table for field case_type on 'EventType'
        db.delete_table('events_eventtype_case_type')


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
            'extra': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'plaintiff': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'plaintiff_contact'", 'to': u"orm['contacts.Contact']"}),
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
        u'events.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'case_type': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['cases.CaseType']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'events.incomingevent': {
            'Meta': {'ordering': "['-date_created']", 'object_name': 'IncomingEvent'},
            'accepted': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'attached_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cases.Case']"}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incoming_created_by'", 'to': u"orm['profiles.CaspUser']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_observed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.EventType']"}),
            'group_uuid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requires_acceptance': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requires_terms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'terms_in_days': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'terms_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        u'events.outgoingevent': {
            'Meta': {'ordering': "['-date_created']", 'object_name': 'OutgoingEvent'},
            'accepted': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'attached_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'case': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cases.Case']"}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'outgoing_created_by'", 'to': u"orm['profiles.CaspUser']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'document_content': ('apps.utils.db.HTMLField', [], {'blank': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.EventType']"}),
            'group_uuid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requires_acceptance': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requires_terms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'terms_in_days': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'terms_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
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

    complete_apps = ['events']