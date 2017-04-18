# -*- coding: utf-8 -*-
from django.forms.widgets import Input
from django.utils.safestring import mark_safe


class DateTimePickerInput(Input):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        template = """
            <div class="input-group datetimepicker" data-provide="datepicker">
                %s
                <div class="input-group-addon">
                    <i data-time-icon="icon-time" data-date-icon="icon-calendar" class="fa fa-calendar"></i>
                </div>
            </div>
        """
        return mark_safe(template % (
            super(DateTimePickerInput, self).render(name, value, attrs)))
