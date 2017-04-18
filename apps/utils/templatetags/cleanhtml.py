 # -*- coding: utf-8 -*-
from lxml.html.clean import clean_html

from django import template
register = template.Library()


@register.filter(name='cleanhtml')
def cleanhtml(value):
    try:
        return clean_html(value)
    except:
        return ''
