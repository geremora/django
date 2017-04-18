from django import forms


class CommaSeparatedListField(forms.CharField):
    def to_python(self, value):
        if not value:
            return []
        return value.split(',')
