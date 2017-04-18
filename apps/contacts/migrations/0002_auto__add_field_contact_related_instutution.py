# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Contact.related_instutution'
        db.add_column(u'contacts_contact', 'related_instutution',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='contact_related_institution', null=True, to=orm['contacts.Contact']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Contact.related_instutution'
        db.delete_column(u'contacts_contact', 'related_instutution_id')


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
            'related_instutution': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contact_related_institution'", 'null': 'True', 'to': u"orm['contacts.Contact']"}),
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