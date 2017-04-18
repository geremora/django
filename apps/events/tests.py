# -*- coding: utf-8 -*-
"""
A few Model tests to make sure it doesn't break the current implementation
"""

from django.test import TestCase
from .models import BaseEvent


class BaseEventTestCase(TestCase):
    def test_base_event_ordering(self):
        field = ['-date_created']
        self.assertListEqual(BaseEvent.Meta.ordering, field)
