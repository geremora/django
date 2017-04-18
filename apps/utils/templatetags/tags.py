import re
from django import template

register = template.Library()


@register.simple_tag
def active(request, pattern):
    '''
    Simple template tag that will return the string active if the passed
    pattern is found in the current url. We user this to highlight the
    current menu item.
    '''
    path = '/{}/'.format(request.path.split('/')[1])

    if re.search(pattern, path):
        return 'active'
    return ''

@register.simple_tag(name='debug_object_dump')
def debug_object_dump(var):
    return vars(var)


# @register.simple_tag(name='conditions_met')
# def conditions_met(transition):

# 	result=True

# 	for cond in transition.conditions:
# 		result = result and cond()

# 	return result