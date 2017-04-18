from django import template

register = template.Library()

@register.simple_tag(name='itemdata')
def itemdata(item):
	data = ' '
	if hasattr(item, 'cases'):
		if item.cases.all()[0].was_consolidated():
			data+=' de '
			for c in item.cases.all():
				data+= ' ' + c.number + ','
    		data = data[1:-1]
    	else:
    		data+= ' de ' + item.case.number
    		
	data+= ' creado por ' + item.created_by.get_full_name() + ' - ' + item.date_created.strftime('%H:%M')

	if hasattr(item, 'related_outgoing_event'):
		if item.related_outgoing_event or item.related_incoming_event:
			data+= ' relacionado con'

		if item.related_outgoing_event:
			data+= ' ' + item.related_outgoing_event.get_friendly_info()

		if item.related_incoming_event:
			data+= ' ' +  item.related_incoming_event.get_friendly_info()
	return data
