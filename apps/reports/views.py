# -*- coding: utf-8 -*-
from datetime import datetime, date
from calendar import monthrange
from datetime import timedelta
import json
import csv
from django.core.paginator import Paginator

from django.db import connection
from django.db.models.query_utils import Q
from django.views import generic
from django.http import HttpResponse, StreamingHttpResponse
from braces.views import LoginRequiredMixin
from django_tables2.config import RequestConfig
from apps.events.models import OutgoingEvent
from apps.profiles.models import CaspUser
from apps.reports.tables import ActiveCasesByCategory, ActiveCasesByCreatedDateTable, ActiveCasesByAgency, \
    ActiveCasesByAgencySumary, CasesByUsersTable

from ..contacts.models import Contact
from ..cases.models import Case, CaseCategory
import cStringIO as StringIO

class GlobalStat(object):

    def __init__(self, materia, year, semester, count):
        self.materia = materia
        self.year = year
        self.semester = semester
        self.count = count

    def __str__(self):
        return json.dump(self)


class CaspGlobalStats(LoginRequiredMixin, generic.TemplateView):
    semester_1 = 'ene-jun'
    semester_2 = 'jul-dic'
    template_name = 'reports/global-stats.html'

    def get_context_data(self, **kwargs):
        context = super(CaspGlobalStats, self).get_context_data(**kwargs)

        current_year = datetime.utcnow().year
        start_year = self.request.GET.get('start_year')

        start_year = current_year - 10 if start_year is None else start_year

        context['recs'] = None

        context['recs'] = self.get_global_stats()

        #
        # The Global stats report is to have two columns for every year. Eg.
        # ene-jun | jul-dic
        # 2000    | 2000
        # Additionally it will have the columns Ley and Materia
        #
        context['report_headers'] = ['Ley', 'Materia', ]
        context['years'] = []

        # The report will be for the past 10 years at first
        for year in range(start_year, current_year + 1):
            context['years'].append(year)
            context['report_headers'].append(self.semester_1)
            context['report_headers'].append(self.semester_2)

        return context

    def get_global_stats(self):
        cursor = connection.cursor()

        query = """
                select ccc.name
                     , extract(year from cc.date_created) as year
                     , case when extract(month from cc.date_created) <= 6 then 'ene-jun' else 'jul-dic' end as month
                     , count(cc.id) as count
                from cases_case cc
                join cases_casecategory ccc on ccc.id = cc.case_category_id
                group by ccc.name, year, month order by year, month;
        """

        cursor.execute(query)

        recs = []

        for rec in cursor:
            global_stat = GlobalStat(rec[0], rec[1], rec[2], rec[3])
            recs.append(global_stat)

        return recs


class CaspOrdRadResByMonth(LoginRequiredMixin, generic.ListView):
    template_name = 'reports/ordenes-radicaciones-resoluciones.html'
    model = Case
    queryset = Case.objects.all()
    LAST_SEARCH_YEAR = 2000

    def get_queryset(self):
        queryset = self.queryset
        current_year = datetime.utcnow().year
        search_year = int(self.request.GET.get('search_year', current_year))

        queryset = queryset.filter(date_created__year=search_year)

        return queryset

    def post(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Ordenes_Radicaciones_Resoluciones_Por_Mes.csv"'

        writer = csv.writer(response)

        writer.writerow(['Estado Libre Asociado de Puerto Rico',
                         'Comision Apelativa del Sistema de Administracion de Recursos Humanos',
                         'Ordenes, Radicaciones y Resoluciones por Mes', ])
        writer.writerow(['Mes/Año', 'ORD', 'RAD', 'RES'])

        search_year = int(self.request.GET.get('search_year', datetime.utcnow().year))

        ord_total = 0
        rad_total = 0
        res_total = 0

        for month_index in range(1, 13):
            queryset = self.queryset.filter(date_created__year=search_year, date_created__month=month_index)

            month = '{}/{}'.format(month_index, search_year)

            ord = 0
            rad = queryset.count()
            res = queryset.filter(state='closed').count()

            ord_total += ord
            rad_total += rad
            res_total += res

            writer.writerow([month, ord, rad, res])

        writer.writerow(['Totales', ord_total, rad_total, res_total])

        return response

    def get_context_data(self, *args, **kwargs):
        context_data = super(CaspOrdRadResByMonth, self).get_context_data(*args, **kwargs)

        context_data['recs'] = []
        context_data['page_header'] = 'Ordenes, Radicaciones y Resoluciones por Mes'
        context_data['years'] = []

        context_data['recs_totals'] = {
            'ord_total': 0,
            'rad_total': 0,
            'res_total': 0
        }

        current_year = datetime.utcnow().year
        search_year = int(self.request.GET.get('search_year', current_year))
        context_data['search_year'] = search_year

        for year in range(current_year, self.LAST_SEARCH_YEAR, -1):
            context_data['years'].append(year)

        for month_index in range(1, 13):
            rec = {}

            queryset = self.queryset.filter(date_created__year=search_year, date_created__month=month_index)

            rec['month'] = '{}/{}'.format(month_index, search_year)
            rec['ord'] = 0
            rec['rad'] = queryset.count()
            rec['res'] = queryset.filter(state='closed').count()

            context_data['recs_totals']['ord_total'] += rec['ord']
            context_data['recs_totals']['rad_total'] += rec['rad']
            context_data['recs_totals']['res_total'] += rec['res']

            context_data['recs'].append(rec)

        return context_data


class CaspActiveCasesByAgency(LoginRequiredMixin, generic.ListView):
    template_name = 'reports/active-cases-by-agency.html'
    model = Case

    def get_queryset(self):
        queryset = Case.objects.select_related(
                'case_type', 'defendant', 'plaintiff', 'assigned_user', 'case_category').exclude(
                    state='closed').exclude(defendant__institutional_name='').order_by('defendant', 'date_created')

        date_from = self.request.GET.get('date_from', None)
        date_to = self.request.GET.get('date_to', None)
        agency = self.request.GET.get('agency', None)

        if date_from:
            queryset = queryset.filter(date_created__gte=date_from)

        if date_to:
            queryset = queryset.filter(date_created__lte=date_to)

        if agency is not None and agency != 'all':
            queryset = queryset.filter(defendant__institutional_name=agency)

        return queryset

    def post(self, request):

        def stream():
            buffer_ = StringIO.StringIO()

            writer = csv.writer(buffer_)
            writer.writerow(['Estado Libre Asociado de Puerto Rico',
                              'Comision Apelativa del Sistema de Administracion de Recursos Humanos',
                              'Casos Activos Por Agencia', ])
            writer.writerow(['Numero de Caso', 'Oficial Examinador', 'Materia', 'Estado', 'Fecha Radicada', 'Inactivo',
                              'Fecha de Estatus'])
            for case in self.get_queryset():
                case_category = case.case_category.name
                writer.writerow([case.number,
                                  case.assigned_user,
                                  case_category.encode('utf-8'),
                                  case.state,
                                  case.date_created,
                                  '',
                                  ''])
                buffer_.seek(0)
                data = buffer_.read()
                buffer_.seek(0)
                buffer_.truncate()
                yield data

        response = StreamingHttpResponse(
        stream(), content_type='text/csv'
        )
        disposition = "attachment; filename=Casos_Activos_Por_Agencia.csv"
        response['Content-Disposition'] = disposition
        return response

    def get_context_data(self, **kwargs):
        context_data = super(CaspActiveCasesByAgency, self).get_context_data(**kwargs)

        report_type = self.request.GET.get('report_type')
        data_table = None

        if report_type == 'sum':
            context_data['sumary_data'] = []

            raw_queryset = Case.objects.raw("select c.institutional_name, count(cc.id) from cases_case cc join contacts_contact c on c.id=cc.defendant_id where c.institutional_name != '' and cc.state !='closed' group by c.institutional_name")
            cursor = raw_queryset.query.cursor
            recs = []
            for rec in cursor:
                recs.append({'agency': rec[0], 'total': rec[1]})

            data_table = ActiveCasesByAgencySumary(recs)
            RequestConfig(request=self.request, paginate={"per_page": 20}).configure(data_table)
        else:
            data_table = ActiveCasesByAgency(context_data['object_list'])
            RequestConfig(request=self.request, paginate={"per_page": 20}).configure(data_table)

        context_data['page_header'] = 'Informe de Casos Activos por Agencia'
        context_data['search_action'] = 'active_cases_by_agency'
        context_data['data_table'] = data_table
        context_data['agencies'] = Contact.objects.exclude(institutional_name='')
        context_data['search_agency'] = self.request.GET.get('agency', None)
        context_data['date_from'] = self.request.GET.get('date_from', None)
        context_data['date_to'] = self.request.GET.get('date_to', None)
        # context_data['object_list'] = None

        return context_data


class CaspActiveCasesByCreatedDate(LoginRequiredMixin, generic.ListView):
    template_name = "reports/active-cases-by-created-date.html"
    model = Case

    def get_queryset(self):
        # queryset = self.queryset
        queryset = Case.objects.all()
        date_from = self.request.GET.get('date_from', None)
        date_to = self.request.GET.get('date_to', None)
        case_state = self.request.GET.get('case_state_filters', None)

        current_month = datetime.now().month
        current_year = datetime.now().year
        first_last_day_month = monthrange(current_year, current_month)

        if date_from is None or date_from == '':
            date_from = date(current_year, current_month, (first_last_day_month[0] + 1))

        if date_to is None or date_to == '':
            date_to = date(current_year, current_month, (first_last_day_month[1] - 1))

        # TODO: Why would a active case report have an option to get inactive cases?
        if case_state == 'inactive':
            queryset = queryset.filter(state='closed')
        elif case_state == 'active':
            queryset = queryset.exclude(state='closed')

        return queryset.filter(date_created__gte=date_from).filter(date_created__lte=date_to)

    def post(self, request):

        def stream():
            buffer_ = StringIO.StringIO()

            writer = csv.writer(buffer_)
            writer.writerow(['Estado Libre Asociado de Puerto Rico',
                              'Comision Apelativa del Sistema de Administracion de Recursos Humanos',
                              'Casos Activos Por Fecha Radicada', ])
            writer.writerow(['Numero de Caso', 'Oficail Examinador', 'Materia', 'Estado', 'Fecha Radicada', 'Inactivo',
                              'Fecha de Estatus'])
            for case in self.get_queryset():
                case_category = case.case_category.name
                writer.writerow([case.number,
                                  case.assigned_user,
                                  case_category.encode('utf-8'),
                                  case.state,
                                  case.date_created,
                                  '',
                                  ''])
                buffer_.seek(0)
                data = buffer_.read()
                buffer_.seek(0)
                buffer_.truncate()
                yield data

        response = StreamingHttpResponse(
        stream(), content_type='text/csv'
        )
        disposition = "attachment; filename=Casos_Activos_Por_Fecha_Radicada.csv"
        response['Content-Disposition'] = disposition
        return response

    def get_context_data(self, **kwargs):
        context_data = super(CaspActiveCasesByCreatedDate, self).get_context_data(**kwargs)

        data_table = ActiveCasesByCreatedDateTable(context_data['object_list'])
        RequestConfig(request=self.request, paginate={"per_page": 20}).configure(data_table)

        context_data['page_header'] = 'Casos Activos por Fecha de Radicacion'
        context_data['search_action'] = 'active_cases_by_created_date'
        context_data['data_table'] = data_table
        context_data['date_from'] = self.request.GET.get('date_from', None)
        context_data['date_to'] = self.request.GET.get('date_to', None)
        # context_data['object_list'] = None

        return context_data


class CaspActiveCasesByCategory(LoginRequiredMixin, generic.ListView):
    template_name = "reports/active-cases-by-case-category.html"
    queryset = Case.objects.select_related(
            'case_type', 'defendant', 'plaintiff', 'assigned_user', 'case_category').exclude(state='closed')

    def get_queryset(self):
        queryset = self.queryset.order_by('date_created', 'case_category')
        category = self.request.GET.get('category')

        date_from = self.request.GET.get('date_from', None)
        date_to = self.request.GET.get('date_to', None)

        if date_from:
            queryset = queryset.filter(date_created__gte=date_from)

        if date_to:
            queryset = queryset.filter(date_created__lte=date_to)

        if category and category != 'none':
            queryset = queryset.filter(case_category__name=category)

        return queryset

    def post(self, request):
        
        def stream():
            buffer_ = StringIO.StringIO()

            writer = csv.writer(buffer_)
            writer.writerow(['Estado Libre Asociado de Puerto Rico',
                         'Comision Apelativa del Sistema de Administracion de Recursos Humanos',
                         'Casos Activos Por Categoria', ])
            writer.writerow(['Numero de Caso', 'Oficial Examinador', 'Materia', 'State', 'Fecha Radicada'])

            for case in self.get_queryset():
                assigned_user = case.assigned_user
                state = 'Abierto'
                case_category = case.case_category

                if case.assigned_user == 'NULL' or case.assigned_user == 'null' or case.assigned_user == 'Undefined':
                    assigned_user = ''

                if case.state == 'closed':
                    state = 'Cerrado'

                if case.case_category.name == 'Undefined':
                    case_category = ''

                writer.writerow([case.number,
                             assigned_user,
                             case_category,
                             state,
                             case.date_accepted])
                buffer_.seek(0)
                data = buffer_.read()
                buffer_.seek(0)
                buffer_.truncate()
                yield data

        response = StreamingHttpResponse(
        stream(), content_type='text/csv'
        )
        disposition = "attachment; filename=Casos_Activos_Por_Categoria.csv"
        response['Content-Disposition'] = disposition
        return response

    def get_context_data(self, **kwargs):
        context_data = super(CaspActiveCasesByCategory, self).get_context_data(**kwargs)

        data_table = ActiveCasesByCategory(context_data['object_list'])
        RequestConfig(request=self.request, paginate={"per_page": 20}).configure(data_table)

        context_data['page_header'] = 'Casos Activos por Materia'
        context_data['search_action'] = 'active_cases_by_case_category'
        context_data['date_from'] = self.request.GET.get('date_from', None)
        context_data['date_to'] = self.request.GET.get('date_to', None)
        context_data['data_table'] = data_table
        context_data['case_categories'] = CaseCategory.objects.all()
        context_data['search_case_category'] = self.request.GET.get('category')
        # context_data['object_list'] = None

        return context_data


class CaspCasesByUsers(LoginRequiredMixin, generic.ListView):
    template_name = "reports/cases-by-users.html"

    def get_queryset(self):
        queryset = Case.objects.select_related(
                'case_type', 'defendant', 'plaintiff', 'assigned_user', 'case_category').all().order_by('assigned_user')

        case_state = self.request.GET.get('case_state', None)
        date_from = self.request.GET.get('date_from', None)
        date_to = self.request.GET.get('date_to', None)
        search_user = self.request.GET.get('search_user', None)
        search_case_number = self.request.GET.get('search_case_number', None)

        if date_from:
            queryset = queryset.filter(date_created__gte=date_from)

        if date_to:
            queryset = queryset.filter(date_created__lte=date_to)

        if case_state and case_state == 'inactive':
            queryset = queryset.filter(state='closed')
        elif case_state and case_state == 'active':
            queryset = queryset.exclude(state='closed')

        if search_user and search_user != 'all':
            queryset = queryset.filter(assigned_user__username=search_user)

        if search_case_number:
            queryset = queryset.filter(Q(number__icontains=search_case_number))

        return queryset

    def post(self, request):

        def stream():
            buffer_ = StringIO.StringIO()

            writer = csv.writer(buffer_)
            writer.writerow(['Estado Libre Asociado de Puerto Rico',
                              'Comision Apelativa del Sistema de Administracion de Recursos Humanos',
                              'Casos Activos Por Usuario', ])
            writer.writerow(['Usuario', 'Numero de Caso', 'Estado', 'Fecha Creada', 'Ultima Actualizacion'])
            for case in self.get_queryset():
                writer.writerow([case.assigned_user,
                             case.number,
                             case.state,
                             case.date_created,
                             case.date_updated])
                buffer_.seek(0)
                data = buffer_.read()
                buffer_.seek(0)
                buffer_.truncate()
                yield data

        response = StreamingHttpResponse(
        stream(), content_type='text/csv'
        )
        disposition = "attachment; filename=Casos_Activos_Por_Usuario.csv"
        response['Content-Disposition'] = disposition
        return response

    def get_context_data(self, **kwargs):
        context_data = super(CaspCasesByUsers, self).get_context_data(**kwargs)
        # cases = []

        # for case in self.queryset:
        #     event = OutgoingEvent.objects.select_related('event', 'cases').filter(cases__pk=case.pk).filter(
        #         Q(comments__icontains=u'actualizó empleado asignado')).order_by('date_created')

        #     cases.append({
        #         'assigned_user': case.assigned_user.get_full_name() if case.assigned_user else '-',
        #         'number': case.number if case.number else '-',
        #         'case_category': case.case_category.name if case.case_category else '-',
        #         'assigned_date': event[0].date_created if event else '-',
        #         'days': '-',
        #     })

        data_table = CasesByUsersTable(context_data['object_list'])
        RequestConfig(request=self.request, paginate={'per_page': 20}).configure(data_table)

        context_data['users'] = CaspUser.objects.all()
        context_data['page_header'] = 'Casos por Usuario'
        context_data['data_table'] = data_table
        context_data['date_from'] = self.request.GET.get('date_from', None)
        context_data['date_to'] = self.request.GET.get('date_to', None)
        context_data['search_user'] = self.request.GET.get('search_user', None)
        context_data['search_case_number'] = self.request.GET.get('search_case_number', '')
        context_data['case_state'] = self.request.GET.get('case_state', 'all')
        # context_data['object_list'] = None

        return context_data


class CaseReportsView(LoginRequiredMixin, generic.ListView):
    model = Case
    queryset = Case.objects.select_related('case_type', 'defendant', 'plaintiff', 'assigned_user',
                                           'case_category').order_by('-date_created', 'case_category')
    context_object_name = 'cases'
    template_name = 'reports/reports.html'

    def get_queryset(self):
        queryset = self.queryset
        report_type = self.request.GET.get('report_type')
        current_date = datetime.utcnow()

        if report_type is not None:
            if report_type == 'active':
                queryset = queryset.exclude(state='close')
            elif report_type == 'resolved':
                queryset = queryset.filter(state='close')

        return queryset.filter(date_created__year=current_date.year)

    def get_total_year_cases_count(self):
        current_date = datetime.utcnow()
        return Case.objects.filter(date_created__year=current_date.year).count()

    def get_total_month_cases_count(self):
        current_date = datetime.utcnow()
        return Case.objects.filter(date_created__month=current_date.month).count()

    def get_report_total_cases(self):
        current_date = datetime.utcnow()
        report_type = self.request.GET.get('report_type')
        queryset = self.queryset

        if report_type == 'active':
            queryset = self.queryset.exclude(state='close')
        elif report_type == 'resolved':
            queryset = self.queryset.filter(state='close')

        return queryset.filter(date_created__year=current_date.year).count()

    def get_context_data2(self, **kwargs):
        context = super(CaseReportsView, self).get_context_data(**kwargs)

        report_type = self.request.GET.get('report_type')

        if report_type == 'active':
            context['page_header'] = 'Casos Activos'
        elif report_type == 'resolved':
            context['page_header'] = 'Casos Cerrados'
        else:
            context['page_header'] = 'Radicados'

        cases = context['cases']

        grouped_cases = {}
        months = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                  9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

        for case in cases:
            case_category = {}
            category = case.case_category.name
            month = months[case.date_created.month]

            if month in grouped_cases:
                if category in grouped_cases[month]:
                    grouped_cases[month][category].append(case)
                else:
                    grouped_cases[month][category] = [case]
            else:
                case_category[category] = [case]
                grouped_cases[month] = case_category

        context['grouped_cases'] = grouped_cases

        return context
