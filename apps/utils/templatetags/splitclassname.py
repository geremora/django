 # -*- coding: utf-8 -*-
from django import template
register = template.Library()


@register.filter(name='splitclassname')
def splitclassname(value):
    output = str()
    for char in value:
        if char.isupper():
            output += ' {}'.format(char)
        else:
            output += char
    return output
