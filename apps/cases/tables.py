import django_tables2 as tables
from django_tables2.utils import A
from .models import Case, ContactCaseRole
from ..contacts.models import Contact
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.safestring import mark_safe

import logging
logger = logging.getLogger(__name__)

class CaseTable(tables.Table):
    number = tables.LinkColumn(verbose_name='Numero de Caso', viewname='case_detail', args=[A('pk')])
    old_number = tables.Column(verbose_name='Num Caso Anterior')
    expired_events = tables.Column(verbose_name='Termino Expirado', accessor=A('has_expired_events'), orderable=False)
    date_created = tables.Column(verbose_name='Fecha Sometida')
    case_category = tables.Column(verbose_name='Materia')
    plaintiff = tables.Column(verbose_name='Promovente', accessor=A('plaintiff.get_name'), order_by=('plaintiff.first_name'))
    defendant = tables.Column(verbose_name='Promovido', accessor=A('defendant.get_name'), order_by=('defendant.first_name'))
    state = tables.Column(verbose_name='Estado', accessor=A('pretty_state_name'), order_by=('state'))
    last_outgoing_event = tables.Column(verbose_name='Ultimo evento', orderable=False)

    class Meta:
        model = Case
        fields = ('number', 'old_number', 'expired_events', 'date_created', 'case_category', 'plaintiff', 'defendant', 'state', 'last_outgoing_event',)
        attrs = {"class": "paleblue table table-striped"}
        template = 'django-tables2/bootstrap-base.html'

    # def render_last_outgoing_event(self, value):
    #     return "ola"


    def render_expired_events(self, value):
        if value:
            return 'Si'
        else:
            return 'No'


class CasesConsolidatedContactTable(tables.Table):
    name = tables.LinkColumn(verbose_name='Nombre', accessor=A('contact.get_name'), order_by=('contact.first_name'), viewname='case_contact_update', args=[A('case.pk'), A('pk')])
    rol = tables.Column(verbose_name='Rol', accessor=A('get_name'), order_by=('name.name'))
    active = tables.Column(verbose_name='Estado', accessor=A('get_status'), orderable=False)
    case = tables.Column(verbose_name='Caso', accessor=A('case.number'), order_by=('case.number'))
    link = tables.LinkColumn("delete_case_contact", verbose_name=' ', empty_values=(), orderable=False)

    class Meta:
        model = ContactCaseRole
        fields = ('name', 'rol', 'active', 'case','link')
        attrs = {"class": "paleblue table table-striped"}
        template = 'django-tables2/bootstrap-base.html'

    def render_link(self, record):
        if record.name.pk == 1 or record.name.pk == 2:
            return '-'
        else:
            delete_url = reverse_lazy('delete_case_contact', args=[record.case.pk, record.pk])
            return mark_safe('''<a href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>''' % (delete_url))  


class CaseContactTable(tables.Table):
    name = tables.LinkColumn(verbose_name='Nombre', accessor=A('contact.get_name'), order_by=('contact.first_name'), viewname='case_contact_update', args=[A('case.pk'), A('pk')])
    rol = tables.Column(verbose_name='Rol', accessor=A('get_name'), order_by=('name.name'))
    active = tables.Column(verbose_name='Estado', accessor=A('get_status'), orderable=False)
    link = tables.LinkColumn("delete_case_contact", verbose_name=' ', empty_values=(), orderable=False)

    class Meta:
        model = ContactCaseRole
        fields = ('name', 'rol', 'active', 'link')
        attrs = {"class": "paleblue table table-striped"}
        template = 'django-tables2/bootstrap-base.html'

    def render_link(self, record):
        if record.name.pk == 1 or record.name.pk == 2:
            return '-'
        else:
            delete_url = reverse_lazy('delete_case_contact', args=[record.case.pk, record.pk])
            return mark_safe('''<a href="%s"><i class="fa fa-trash" aria-hidden="true"></i></a>''' % (delete_url))    