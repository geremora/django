# -*- coding: utf-8 -*-
"""
A few Model tests to make sure it doesn't break the current implementation
"""

from django.test import TestCase
from .models import Bug


class BugTestCase(TestCase):
    fixtures = ['bugs_forms_testdata.json']

    def setUp(self):
        super(BugTestCase, self).setUp()
        self.bug_1 = Bug.objects.get(pk=1)
        self.bug_2 = Bug.objects.get(pk=2)

    def test_bug_type(self):
        self.assertEqual(self.bug_1.bug_type, 'bug')
        self.assertEqual(self.bug_2.bug_type, 'correction')

    def test_bug_type_choice(self):
        self.assertEqual(self.bug_1.get_bug_type_display(), 'Bug')
        self.assertEqual(self.bug_2.get_bug_type_display(), u'Solicitar Corrección')

    def test_bug_type_choices(self):
        choices = (('correction', u'Solicitar Corrección'), ('bug', 'Bug'), ('feature', 'Feature'))
        self.assertTupleEqual(Bug._meta.get_field_by_name('bug_type')[0].choices, choices)

    def test_readable_representation_of_model(self):
        self.assertEqual(Bug.__unicode__(self.bug_1), self.bug_1.message)
