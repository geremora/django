# coding=utf-8

import django_tables2 as tables
from django_tables2.utils import A
from ..cases.models import Case


class ActiveCasesByAgency(tables.Table):
    number = tables.LinkColumn(verbose_name='Numero de Caso', viewname='case_detail', args=[A('pk')])
    defendant = tables.Column(verbose_name='Agencia')
    date_created = tables.Column(verbose_name='Fecha Radicada')
    plaintiff = tables.Column(verbose_name='Apelante')
    case_category = tables.Column(verbose_name='Materia')
    num_plaintiffs = tables.Column(verbose_name='Num. Plainfiffs')

    class Meta:
        model = Case
        fields = ('number', 'defendant', 'date_created', 'plaintiff', 'case_category')
        attrs = {"class": 'paleblue table table-striped'}
        template = 'django-tables2/bootstrap-reports.html'

    def render_num_plaintiffs(self, value):
        return 1


class ActiveCasesByAgencySumary(tables.Table):
    agency = tables.Column(verbose_name='Agencia')
    total = tables.Column(verbose_name='Total')

    class Meta:
        attrs = {"class": 'paleblue table table-striped'}
        template = 'django-tables2/bootstrap-reports.html'


class ActiveCasesByCreatedDateTable(tables.Table):
    number = tables.LinkColumn(verbose_name='Numero de Caso', viewname='case_detail', args=[A('pk')])
    assigned_user = tables.Column(verbose_name='Oficial Examinador')
    case_category = tables.Column(verbose_name='Materia')
    state = tables.Column(verbose_name='Status')
    inactive = tables.Column(verbose_name='Inactivo')
    status_date = tables.Column(verbose_name='Fecha de Status')
    date_created = tables.Column(verbose_name='Fecha Radicada')

    class Meta:
        model = Case
        fields = ('number', 'assigned_user', 'case_category', 'state', 'date_created')
        attrs = {"class": "paleblue table table-striped"}
        template = 'django-tables2/bootstrap-reports.html'

    def render_inactive(self, value):
        return ''

    def render_assigned_user(self, value):
        if value:
            return value
        else:
            return 'SIN DELEGAR'

    def render_status_date(self, value):
        return ''

    def render_date_created(self, value):
        return value.strftime('%Y-%b-%d')


class ActiveCasesByCategory(tables.Table):
    case_category = tables.Column(verbose_name='Materia')
    number = tables.LinkColumn(verbose_name='Numero de Caso', viewname='case_detail', args=[A('pk')])
    date_created = tables.Column(verbose_name='Fecha Radicada')
    assigned_user = tables.Column(verbose_name='Oficial Examinador')

    class Meta:
        model = Case
        fields = ('number', 'assigned_user', 'case_category', 'state', 'date_created')
        attrs = {"class": "paleblue table table-striped"}
        template = 'django-tables2/bootstrap-reports.html'

    def render_date_created(self, value):
        return value.strftime('%Y-%b-%d')


class CasesByUsersTable(tables.Table):
    assigned_user = tables.Column(verbose_name='Usuario')
    number = tables.Column(verbose_name='Numero de Caso')
    case_category = tables.Column(verbose_name='Materia')
    state = tables.Column(verbose_name='Estado')
    date_created = tables.Column(verbose_name='Fecha Creada')
    date_updated = tables.Column(verbose_name='Ultima Actualizacion')
    # assigned_date = tables.Column(verbose_name='Fecha Asignada')
    # days = tables.Column(verbose_name='Dias')

    class Meta:
        model = Case
        fields = ('assigned_user', 'number', 'case_category', 'state', 'date_created', 'date_updated',)
        attrs = {"class": "paleblue table table-striped"}
        template = 'django-tables2/bootstrap-reports.html'
