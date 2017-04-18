# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Contact'
        db.create_table(u'contacts_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('institutional_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('phone1', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('phone2', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('address', self.gf('django.db.models.fields.TextField')()),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('contact_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.ContactType'])),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'contacts', ['Contact'])

        # Adding model 'ContactType'
        db.create_table(u'contacts_contacttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
        ))
        db.send_create_signal(u'contacts', ['ContactType'])


    def backwards(self, orm):
        # Deleting model 'Contact'
        db.delete_table(u'contacts_contact')

        # Deleting model 'ContactType'
        db.delete_table(u'contacts_contacttype')


    models = {
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
        }
    }

    complete_apps = ['contacts']