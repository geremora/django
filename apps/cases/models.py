# -*- coding: utf-8 -*-
from collections import defaultdict
from itertools import chain
from operator import attrgetter
from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.timezone import now, utc

#rom django_fsm.db.fields import transition, TransitionNotAllowed

from django_fsm import transition, TransitionNotAllowed
from jsonfield import JSONField
from django.contrib import messages

from .fields import MyFSMField
from .conditions import has_materia, has_closing_document, has_date_accepted
from ..meetings.models import Meeting
from ..notes.models import Note
from ..events.models import IncomingEvent, OutgoingEvent, ImportedEvent
from ..utils.models import ModelDiffMixin
from ..utils.permissions import get_custom_permissions
from ..profiles.models import CaspUser
import re

from datetime import datetime

from django.db.models import Q

import logging
logger = logging.getLogger(__name__)

STATES_DICT = [
('closed','cerrado'),
('new','nuevo'),
('.*-case-type-confirmed','confirmado'),
('.*-send-to-mediacion',u'enviado a mediación'),
('.*-enviado-a-legal',u'enviado a legal'),
('.*-informe-investigador',u'informe investigador emitido'),
('.*-enviado_a_investigador',u'enviado a investigador'),
('.*-send-to-arbitraje',u'enviado a arbitraje'),
('.*-send-to-arbitraje',u'enviado a arbitraje'),
('.*-devolver-a-legal',u'devuelto a legal'),
('.*-submit-laudo_close',u'se emitió laudo'),
('.*-partial-agreement',u'arreglo parcial'),
('.*-total-agreement-close',u'acuerdo total'),
('.*-no-agreement',u'sin acuerdo'),
('.*-new-assigned-to',u'se asignó I.N.'),
('.*-reinvestigar-caso',u'reinvestigando caso'),
('.*-enviado-a-ma',u'enviado a M.A'),
('.*-devolver-a-comision',u'devuelto a comisión'),
('.*-ca-notifico-partes-desestimacion',u'se notifico a partes desestimación'),
('.*-notifica-querella-aviso-de-audiencia',u'se notifico a querella'),
('.*-no-reconsideracion-closed',u'no reconsideración'),
('.*-determinacion-final',u'determinación final'),
('.*-enviar-a-investigador',u'enviado a investigador'),
('.*-informe-interes-sustancial',u'informe intereses sustancial'),
('.*-cumple-con-interes-sustancial',u'cumple intereses sustancial'),
('.*-no-cumple-con-interes-sustancial',u'no cumple intereses sustancial'),
('.*-solicitud-archivada',u'solicitud archivada'),
('.*-eleccion-ordenada',u'elección ordenada'),
('.*-resultados',u'resultados'),
('.*-devolver-oficial-examinador',u'Devuelto a oficial examinador'),
('.*-notifica-informe-oficial-examinador',u'Informe oficial examinador emitido'),
]
        

class CaseContainerActionSequence(models.Model):
    action_type = models.CharField(choices=[('unmerge', 'unmerge'), ('merge', 'merge')], max_length=7)
    last_id = models.IntegerField()

    def __unicode__(self):
        return self.action_type

    @classmethod
    def next(self, action_type):
        try:
            seq = CaseContainerActionSequence.objects.get(action_type=action_type)
            seq.last_id += 1
            seq.save()
            return seq.last_id

        except CaseContainerActionSequence.DoesNotExist:

            new_seq = CaseContainerActionSequence.objects.create(action_type=action_type, last_id=1)
            return new_seq.last_id


class CaseContainerAction(models.Model):
    action_seq = models.IntegerField()
    container = models.IntegerField()
    action_type = models.CharField(choices=[('unmerge', 'unmerge'), ('merge', 'merge')], max_length=7)
    case = models.ForeignKey('Case')
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=50)

    @classmethod
    def create_case_container_action(self, action_seq, container, action_type, case, user):

        return CaseContainerAction.objects.create(action_seq=action_seq, container=container, action_type=action_type,
                                                  case=case, user=user)


class CaseContainer(models.Model):
    '''
    Holds cases and acts as a proxy to all the contained cases
    '''
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    main_case = models.ForeignKey('Case', null=True)

    def __unicode__(self):
        case_list = []  # [c.number for c in Case.objects.filter(container=self)]

        if len(case_list) > 0:
            return '{}:{}'.format(self.pk, ', '.join(case_list))

        return '{}'.format(self.pk)

    def get_cases(self):
        # Get's all the cases on the container
        return Case.objects.select_related(
            'plaintiff', 'plaintiff__profile',
            'defendant', 'defendant__profile').filter(container=self)



    def get_cases_not_main(self):
        # Get's all the cases on the container 
        return Case.objects.select_related(
            'plaintiff', 'plaintiff__profile',
            'defendant', 'defendant__profile').filter(container=self).exclude(id__in=[self.main_case.id])

    def get_events(self, current_case, limit=1):
        events = []

        events.extend(OutgoingEvent.objects.select_related(
            'event_type', 'created_by', 'created_by__profile',
            'related_event').filter(cases__in=self.get_cases_ids())
                .filter(Q(date_created__lte=self.date_created)).order_by('-date_created')[:limit])

        events.extend(IncomingEvent.objects.select_related(
            'event_type', 'created_by', 'created_by__profile',
            'related_event').filter(cases__in=self.get_cases_ids())
                .filter(Q(date_created__lte=self.date_created)).order_by('-date_created')[:limit])

        events.extend(IncomingEvent.objects.select_related(
            'event_type', 'created_by', 'created_by__profile',
            'related_event').filter(cases__in=[current_case.id]).filter(Q(date_created__gte=self.date_created)).order_by('-date_created')[:limit])

        events.extend(OutgoingEvent.objects.select_related(
            'event_type', 'created_by', 'created_by__profile',
            'related_event').filter(cases__in=[current_case.id]).filter(Q(date_created__gte=self.date_created)).order_by('-date_created')[:limit])

        return events

    def get_meetings(self, current_case, limit=1):
        meetings = []

        meetings.extend(Meeting.objects.select_related('room', 'created_by').filter(cases__in=self.get_cases_ids())
            .filter(Q(date_created__lte=self.date_created)))

        meetings.extend(Meeting.objects.select_related('room', 'created_by').filter(cases__in=[current_case.id]).filter(Q(date_created__gte=self.date_created)))


        return meetings

    def get_notes(self, user, current_case, limit=1):
        notes = []

        notes.extend(Note.objects.select_related('created_by').filter(case__in=self.get_cases_ids()).filter(Q(date_created__lte=self.date_created)))
        
        notes.extend(Note.objects.select_related('created_by').filter(case__in=[current_case.id]).filter(Q(date_created__gte=self.date_created)))

        return [n for n in notes if n.can_view(user)]

    def get_imported_events(self):
        return ImportedEvent.objects.filter(case__in=[self.get_cases_ids()])

    def get_contacts_role(self):
        return ContactCaseRole.objects.select_related('date_created').filter(case__in=self.get_cases_ids())

    def get_contacts_role_not_main_cases(self):
        return ContactCaseRole.objects.select_related('date_created').filter(case__in=self.get_cases_not_main_ids())

    def get_cases_ids(self):
        # Get's all the cases ids on the container
        return Case.objects.filter(container=self).values_list('id', flat=True)

    def get_cases_not_main_ids(self):
        return Case.objects.filter(container=self).exclude(id__in=[self.main_case.id]).values_list('id', flat=True)

    def get_count_extra_plaintiffs(self):
        if self.get_case_count() > 1:
            return len(self.get_contacts_role_not_main_cases().filter(name_id__in=[1,3]).filter(active=True).distinct())
        else:
            return len(self.get_contacts_role().filter(name_id__in=[3]).filter(active=True))

    def get_count_extra_defendants(self):
        if self.get_case_count() > 1:
            return len(self.get_contacts_role_not_main_cases().filter(name_id__in=[2,4]).filter(active=True).distinct())
        else:
            return len(self.get_contacts_role().filter(name_id__in=[4]).filter(active=True))

    def get_case_count(self):
        return self.get_cases().count()

    def has_merged_cases(self):
        if self.get_cases().count() > 1:
            return True
        return False

 

    @classmethod
    def merge_cases(self, main_case, case_list):
        '''
        Takes a list of Case and merges them into the same CaseContainer
        the old CaseContainers are discarted
        '''
        cc = CaseContainer.objects.create(main_case=main_case)
        discated_containers = []
        for case in case_list:
            discated_containers.append(case.container_id)
            case.container = cc
            if case.id != main_case.id:
                case.go_merged()
                logger.info('go_{}'.format(
                                main_case.state.replace('-', '_')))
                func = getattr(
                            case, 'go_{}'.format(
                                main_case.state.replace('-', '_')))
                try:
                    func()

                except TransitionNotAllowed:
                    logger.error("error")

            case.save()

        CaseContainer.objects.filter(case__isnull=True,
                                     pk__in=discated_containers).delete()

        return cc

    @classmethod
    def unmerge_case(self, case_unmerge):
        cc = CaseContainer.objects.create()
        case_unmerge.container = cc
        case_unmerge.save()

        return case_unmerge

        # '''
        # Takes a list of Cases and unmerges them into separate CaseContainer
        # '''
        # new_containers = []
        # unmerge_container = case_list[0].container

        # for case in case_list:
        #     # Check if current Case's CaseContainer has other Cases
        #     if case.container.get_cases().count() > 1:
        #         # Create new CaseContainer
        #         cc = CaseContainer.objects.create()
        #         # Cache old CaseContainer
        #         discarted_container = case.container
        #         case.container = cc
        #         case.save()

        #         # If old CaseContainer is empty we delete it
        #         if discarted_container.get_cases().count() == 0:
        #             discarted_container.delete()

        #         new_containers.append(cc)
        #     else:
        #         new_containers.append(case.container)

        # return unmerge_container




class CaseType(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    mediation_allowed = models.BooleanField(default=True) #Se el tipo de caso permite la mediacion como metodo de resolucion

    case_category = models.ManyToManyField(
        'cases.CaseCategory', null=True, blank=True)

    def __unicode__(self):
        return u'{}:{}'.format(self.code, self.name)

class ContactCaseRole(models.Model):
    #class Meta:
    #    auto_created = True
    contact = models.ForeignKey('contacts.Contact')
    case = models.ForeignKey('Case')
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True, null=True)
    name = models.ForeignKey('contacts.ContactRole')
    active = models.BooleanField(default=True)

    def get_name(self):
        return self.name

    def get_status(self):
        return 'activo' if self.active else 'desactivado'
  

class Case(ModelDiffMixin, models.Model):
    '''
    Represents a case beign handled on CASP. Agency choices are limited to
    Contact with the type of 'Agencia de Gobierno'.
    '''
    state = MyFSMField(default='new')
    container = models.ForeignKey('CaseContainer')
    case_type = models.ForeignKey('CaseType')
    did_confirm_case_type = models.BooleanField(default=False)
    number = models.CharField(max_length=255, unique=True, db_index=True)
    old_number = models.CharField(max_length=15, unique=True, null=True)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_accepted = models.DateTimeField()
    date_closed = models.DateTimeField(null=True)
    extra = JSONField(blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='case_created_by')

    defendant = models.ForeignKey('contacts.Contact',
                                  # limit_choices_to={'contact_type__id': 1},
                                  related_name='defendant_contact')

    plaintiff = models.ForeignKey('contacts.Contact',
                                  # limit_choices_to={'contact_type__id': 3},
                                  related_name='plaintiff_contact')

    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    contacts = models.ManyToManyField('contacts.Contact', null=True, blank=True, through='ContactCaseRole')

    case_category = models.ForeignKey('CaseCategory')

    record_holder = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='case_record_holder', db_index=False)

    active = models.BooleanField(default=True) #Es usado para casos consolidados (merged)

    mediation = models.BooleanField(default=False)

    was_mediation = models.BooleanField(default=False)

    class Meta():
        ordering = ['date_created']
        permissions = get_custom_permissions(
            'case', ['add', 'change', 'delete', 'merge', 'unmerge',
                     'change_case_type', 'change_description',
                     'change_assigned_user', 'change_contacts',
                     'change_case_category', 'change_record_holder',
                     'change_date_closed','re_open',
                     'close'])

    def __unicode__(self):
        return self.number

    @property
    def pretty_state_name(self):
        for pattern, value in STATES_DICT:
            if re.search(pattern, self.state):
                return value
        return self.state


    def is_main_case(self):
        if self.was_consolidated():
            return self.container.main_case == self
        else:
            return True

    def was_consolidated(self):
        return self.container.get_case_count() > 1

    def get_all_contacts(self, id_only=False):
        if id_only:
            contacts = list(chain([c.id for c in self.contacts.all()], [self.defendant.id, self.plaintiff.id]))
        else:
            contacts = list(chain(self.contacts.all(), [self.defendant, self.plaintiff]))

        return contacts

    def get_main_contacts(self, id_only=False):
        if id_only:
            contacts = list([self.defendant.id, self.plaintiff.id])
        else:
            contacts = list([self.defendant, self.plaintiff])

        return contacts

    # def status_legal(self):
    #     #Un caso segun su tipo o state puede considerar en Legal, Investigacion o metodos alternos

    #     if self.case_type.code in ['PR']:
    #         return 'INVESTIGACION'
    #     else if self.case_type.code in ['SA', 'SM']:
    #         return 'LEGAL'
    #     else if self.case_type.code in ['AQ', 'AO']:
    #         return 'METODOS ALTERNOS'
    

    def get_events(self):
        events = []

        events.extend(OutgoingEvent.objects.select_related(
            'event_type', 'created_by', 'created_by__profile',
            'related_event', 'cases').filter(cases__in=[self]).order_by('date_notification'))

        events.extend(IncomingEvent.objects.select_related(
            'event_type', 'created_by', 'created_by__profile',
            'related_event', 'cases').filter(cases__in=[self]).order_by('date_created'))

        return events

    @property
    def last_outgoing_event(self):
        return OutgoingEvent.objects.filter(cases__in=[self]).order_by('date_created').last()

    def get_imported_events(self):
        return ImportedEvent.objects.filter(case__in=[self])

    def get_documents(self):
        outgoing = OutgoingEvent.objects.select_related(
            'event_type', 'created_by', 'related_event').prefetch_related('cases').filter(
            cases__in=[self]).exclude(attached_file__isnull=True).exclude(document_content__isnull=True).exclude(
            attached_file__exact='').exclude(document_content__exact='')

        incoming = IncomingEvent.objects.select_related(
            'event_type', 'created_by', 'related_event').prefetch_related('cases').filter(
            cases__in=[self]).exclude(attached_file__isnull=True).exclude(attached_file__exact='')

        return sorted(chain(outgoing, incoming), key=attrgetter('date_created'), reverse=True)

    def get_meetings(self):
        return Meeting.objects.select_related('room', 'created_by').filter(cases__in=[self])

    def get_plaintiff_contact_role(self):
        return self.get_contacts_role().filter(contact_id__in=[self.plaintiff.id]).first()

    def get_defendant_contact_role(self):
        return self.get_contacts_role().filter(contact_id__in=[self.defendant.id]).first()

    def get_contacts_role(self):
        return ContactCaseRole.objects.select_related('date_created').filter(case=self)

    def get_count_extra_plaintiffs(self):
        return len(self.get_contacts_role().filter(name_id__in=[3]).filter(active=True))

    def get_count_extra_defendants(self):
        return len(self.get_contacts_role().filter(name_id__in=[4]).filter(active=True))

    def get_contacts_role_without_main_contacts(self):
        return ContactCaseRole.objects.select_related('date_created').filter(case=self).exclude(contact_id__in=self.get_main_contacts(id_only=True))

    def get_notes(self, user):
        notes = Note.objects.select_related('created_by').filter(case=self)
        return [n for n in notes if n.can_view(user)]

    def get_feed(self, user=None, with_events=True, with_meetings=True, with_notes=True, with_imported_events=True, limit=10):
        '''
        Returns a dict of CaseEvent, Document, Meeting
        that we use to build the case timeline
        '''
        result = {}
        grouped = defaultdict(list)
        limit = int(limit)
        objects = []
        if with_events:
            result['events'] = self.container.get_events(self, limit)

            objects.append(result['events'])
           
        if with_meetings:
            result['meetings'] = self.container.get_meetings(self, limit)

            objects.append(result['meetings'])

        if with_notes:
            result['notes'] = self.container.get_notes(user, self, limit)

            objects.append(result['notes'])

        if with_imported_events:
            result['imported_events'] = self.get_imported_events()

            objects.append(result['imported_events'])

        sorted_objects = sorted(chain(*objects), key=attrgetter('date_created'), reverse=True)

        sorted_objects = sorted_objects[:limit]

        # Produces {'date': [object1, object2, ...]}
        for item in sorted_objects:
            grouped[item.date_created.date()].append(item)

        # Finally produces a list of dicts
        result['feed'] = sorted([{'grouper': d, 'list': o} for d, o in grouped.iteritems()], reverse=True)

        return result

    def get_expired_events(self):
        events = self.get_events()
        return [e for e in events if e.terms_expired()]

    def has_expired_events(self):
        expired_events = self.get_expired_events()

        if len(expired_events) > 0:
            return True
        else:
            return False

    def refresh(obj):
        """ Reload an object from the database """
        return obj.__class__._default_manager.get(pk=obj.pk)

    def was_closed(self):
        return self.state == 'closed'

    def was_imported(self):
        """
        Detect if case was imported by type based
        on the date_created by case_type.

        Cases created before the date the data of that case_type
        was imported are considered "imported".
        """
        if self.case_type.code == u'AQ' and self.date_created < datetime(2013, 8, 27, 0, 0, 0, 0, utc):
            return True

        if (self.case_type.code == u'SA' or self.case_type.code == u'SM') and \
                self.date_created < datetime(2016, 7, 1, 0, 0, 0, 0, utc):
            return True

        return False

    def get_form_class_for_state(self):
        if self.state == 'new':
            mod = import_module('apps.cases.forms.common')
        else:
            mod = import_module('apps.cases.forms.{}'.format(self.case_type.code.lower()))

        class_prefix = ''.join(self.state.title().split('-'))

        return getattr(mod, '{}StateForm'.format(class_prefix))

    def show_friendly_state_name(self):
        """
        Returns the state in a more friendly way. (yeah...)
        """
        if self.state == 'new':
            return 'Open'
        return self.state

    @classmethod
    def generate_case_number(self, case_type):
        """
        Generates a case number based on the case type
        Numbers are XX-2013-0001
        we use CaseSequence to make sure we don't
        accidentally reuse a number
        """
        
        next_seq = CaseSequence.next(case_type)
        new_number = ('{}-{}-{:06d}'.format(case_type.code, str(now().year)[-2:], next_seq))

        # Make sure we don't have a duplicate number
        if Case.objects.filter(number=new_number).count() > 0:
            new_number = self.generate_case_number(case_type)

        return new_number

    @classmethod
    def create_new_case(self, basic, extra, created_by):
        # Create a new empty container for the Case
        container = CaseContainer.objects.create()

        # Get tmp case number
        number = self.generate_case_number(CaseType.objects.get(pk=1))

        contacts = basic.pop('contacts', None)

        state = '{}-new'.format(basic['case_type'].code.lower())

        # Get number and create case
        case = Case.objects.create(container=container, number=number, created_by=created_by,
                                   extra=extra, record_holder=created_by, state=state, **basic)

        #case.contacts = contacts

        func = getattr(case, 'go_{}_case_type_confirmed'.format(basic['case_type'].code.lower()).replace('-', '_'))
        
        func()

        case.save()

        return case




    class CaseStateLabelEnum(object):
        CASE_TYPE_CONFIRMED = u'Confirmar tipo de caso'
        SEND_TO_MEDIATION = u'Enviar a mediación'
        SEND_TO_ARBITRAJE = u'Enviar a arbitraje'
        ENVIADO_A_INVESTIGADOR = u'Enviado a investigador'
        INFORME_INVESTIGADOR = u'Informe investigador'
        REINVESTIGAR_CASO = u'Reinvestigar caso'
        ENVIAR_A_MA = u'Enviar a MA'
        DEVOLVER_A_COMISION = u'Devolver a comisión'
        CASO_DESESTIMADO = u'Caso desestimado'
        NOTIFICAR_QUERELLA = u'Notificar querella'
        NO_RECONSIDERACION = u'No reconsideración / Cerrar'
        ENVIAR_A_LEGAL = u'Enviar a legal'
        EMISION_INFORME_LEGAL = u'Emisión de informe legal'
        DEVOLVER_A_LEGAL = u'Devolver a legal'
        DETERMINACION_FINAL = u'Determinación Final'
        SOMETIDO_A_LAS_PARTES = u'Sometido por las partes'
        SE_EMITIO_LAUDO = u'Se emitió laudo / cerrar'
        SE_LLEGO_A_ACUERDO_TOTAL = u'Se llegó a acuerdo total / cerrar'
        SE_LLEGO_A_ACUERDO_PARCIAL = u'Se llegó a acuerdo parcial'
        NO_SE_LLEGO_ACUERDO = u'No se llegó a acuerdo'
        SE_ASIGNO_UN_NUEVO_I_N = u'Se asignó nuevo I.N.'
        REMITE_INFORME_INTERES_SUSTANCIAL = u'Remite informe de interés sustancial'
        CUMPLE_INTERES_SUSTANCIAL = u'Cumple con interés sustencial'
        NO_CUMPLE_INTERES_SUSTANCIAL = u'No cumple con interés sustencial'
        SOLICITUD_ARCHIVADA = u'Solicitud archivada'
        ELECCION_ORDENADA = u'Elección ordenada'
        RESULTADOS = u'Resultados'
        CERRAR_CASO = u'Cerrar caso'
  
  

    # TODO: analyze all the transition methods and find a better way to implement them. It's just too cluttered!!!!
    # TODO: update django-fsm to newest version (maybe)

    # Case transitions
    # AQ

      # AQ
    @transition(source=['aq-new', 'closed'], target='aq-case-type-confirmed', conditions=[has_materia, has_date_accepted],
                field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_aq_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    @transition(source=['aq-case-type-confirmed','merged'], target='aq-send-to-mediacion', field=state,
        custom=dict(label=CaseStateLabelEnum.SEND_TO_MEDIATION))
    def go_aq_send_to_mediacion(self):
        """
        Enviar a mediación
        """
        pass

    @transition(source=['aq-case-type-confirmed', 'merged'], target='aq-send-to-arbitraje', field=state,
        custom=dict(label=CaseStateLabelEnum.SEND_TO_ARBITRAJE))
    def go_aq_send_to_arbitraje(self):
        """
        Enviar a arbitraje
        """
        pass

    @transition(source=['aq-send-to-arbitraje','merged'], target='aq-submitted', field=state,
        custom=dict(label=CaseStateLabelEnum.SOMETIDO_A_LAS_PARTES))
    def go_aq_submitted(self):
        """
        Sometido por las partes
        """
        pass

    @transition(source=('aq-submitted', 'aq-new-assigned-to', 'merged'), target='closed', field=state,
        custom=dict(label=CaseStateLabelEnum.SE_EMITIO_LAUDO))
    def go_aq_submit_laudo_close(self):
        """
        Se emitió laudo / cerrar
        """
        pass

    @transition(source=['aq-send-to-mediacion','merged'], target='closed', field=state,
        custom=dict(label=CaseStateLabelEnum.SE_LLEGO_A_ACUERDO_TOTAL))
    def go_aq_total_agreement_close(self):
        """
        Se llegó a acuerdo total / cerrar
        """
        pass

    @transition(source=['aq-send-to-mediacion','merged'], target='aq-partial-agreement', field=state, 
        custom=dict(label=CaseStateLabelEnum.SE_LLEGO_A_ACUERDO_PARCIAL))
    def go_aq_partial_agreement(self):
        """
        Se llegó a acuerdo parcial
        """
        pass

    @transition(source=['aq-send-to-mediacion','merged'], target='aq-no-agreement', field=state,
        custom=dict(label=CaseStateLabelEnum.NO_SE_LLEGO_ACUERDO))
    def go_aq_no_agreement(self):
        """
        No se llegó a acuerdo
        """
        pass


    @transition(source=('aq-partial-agreement', 'aq-no-agreement', 'merged'), target='aq-new-assigned-to', field=state,
        custom=dict(label=CaseStateLabelEnum.SE_ASIGNO_UN_NUEVO_I_N))
    def go_aq_new_assigned_to(self):
        """
        Se asignó nuevo I.N.
        """
        pass

    # AQ
    @transition(source=['ao-new', 'closed'], target='ao-case-type-confirmed', conditions=[has_materia, has_date_accepted],
                field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_ao_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    @transition(source=['ao-case-type-confirmed', 'merged'], target='ao-send-to-mediacion', field=state,
        custom=dict(label=CaseStateLabelEnum.SEND_TO_MEDIATION))
    def go_ao_send_to_mediacion(self):
        """
        Enviar a mediación
        """
        pass

    @transition(source=['ao-case-type-confirmed','merged'], target='ao-send-to-arbitraje', field=state,
        custom=dict(label=CaseStateLabelEnum.SEND_TO_ARBITRAJE))
    def go_ao_send_to_arbitraje(self):
        """
        Enviar a arbitraje
        """
        pass

    @transition(source=('ao-send-to-arbitraje', 'ao-new-assigned-to', 'merged'), target='closed', field=state,
        custom=dict(label=CaseStateLabelEnum.SE_EMITIO_LAUDO))
    def go_ao_submit_laudo_close(self):
        """
        Se emitió laudo / cerrar
        """
        pass

    @transition(source=['ao-send-to-mediacion','merged'], target='closed', field=state,
        custom=dict(label=CaseStateLabelEnum.SE_LLEGO_A_ACUERDO_TOTAL))
    def go_ao_total_agreement_close(self):
        """
        Se llegó a acuerdo total / cerrar
        """
        pass

    @transition(source=['ao-send-to-mediacion','merged'], target='ao-partial-agreement', field=state,
        custom=dict(label=CaseStateLabelEnum.SE_LLEGO_A_ACUERDO_PARCIAL))
    def go_ao_partial_agreement(self):
        """
        Se llegó a acuerdo parcial
        """
        pass

    @transition(source=['ao-send-to-mediacion', 'merged'], target='ao-no-agreement', field=state,
        custom=dict(label=CaseStateLabelEnum.NO_SE_LLEGO_ACUERDO))
    def go_ao_no_agreement(self):
        """
        No se llegó a acuerdo
        """
        pass

    @transition(source=('ao-partial-agreement', 'ao-no-agreement', 'merged'), target='ao-new-assigned-to', field=state,
        custom=dict(label=CaseStateLabelEnum.NO_SE_LLEGO_ACUERDO))
    def go_ao_new_assigned_to(self):
        """
        Se asignó nuevo I.N.
        """
        pass

    # CA, CO, PE, SD, SA, SM, PD
    
    @transition(source=['ca-new', 'closed'], target='ca-case-type-confirmed', conditions=[has_materia, has_date_accepted],
                field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_ca_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    # start process. goes to investigator
    @transition(source=['ca-case-type-confirmed','merged'], target='ca-enviado-a-investigador', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIADO_A_INVESTIGADOR))
    def go_ca_enviado_a_investigador(self):
        """
        Enviado a investigador
        """
        pass

    @transition(source=['ca-enviado-a-investigador', 'ca-reinvestigar-caso', 'ca-notifica-partes-desestimacion', 'merged'],
                target='ca-informe-investigador', field=state, custom=dict(label=CaseStateLabelEnum.INFORME_INVESTIGADOR))
    def go_ca_informe_investigador(self):
        """
        Informe investigador
        """
        pass


    @transition(source=['ca-informe-investigador','merged'], target='ca-reinvestigar-caso', field=state,
        custom=dict(label=CaseStateLabelEnum.REINVESTIGAR_CASO))
    def go_ca_reinvestigar_caso(self):
        """
        Reinvestigar caso
        """
        pass

    @transition(source=['ca-informe-investigador','merged'], target='ca-enviado-a-ma', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIAR_A_MA))
    def go_ca_enviado_a_ma(self):
        """
        Enviar a MA
        """
        pass

    @transition(source=['ca-enviado-a-ma', 'merged'], target='ca-devolver-a-comision', field=state,
        custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_COMISION))
    def go_ca_devolver_a_comision(self):
        """
        Devolver a comisión
        """
        pass

    @transition(source=['ca-informe-investigador','merged'], target='ca-notifico-partes-desestimacion', field=state,
        custom=dict(label=CaseStateLabelEnum.CASO_DESESTIMADO))
    def go_ca_notifico_partes_desestimacion(self):
        """
        Caso desestimado
        """
        pass

    @transition(source=['ca-informe-investigador', 'merged'], target='ca-notifica-querella-aviso-de-audiencia', field=state,
        custom=dict(label=CaseStateLabelEnum.NOTIFICAR_QUERELLA))
    def go_ca_notifica_querella_aviso_de_audiencia(self):
        """
        Notificar querella
        """
        pass

    @transition(source=['ca-notifico-partes-desestimacion','merged'], target='ca-no-reconsideracion-closed', field=state,
        custom=dict(label=CaseStateLabelEnum.NO_RECONSIDERACION))
    def go_ca_no_reconsideracion_closed(self):
        """
        No reconsideración / Cerrar
        """
        pass

    @transition(source=['ca-notifica-querella-aviso-de-audiencia','merged'], target='ca-enviado-a-legal', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIAR_A_LEGAL))
    def go_ca_enviado_a_legal(self):
        """
        Enviar a legal
        """
        pass

    # legal department
    @transition(source=['ca-enviado-a-legal', 'ca-devolver-a-legal','merged'], target='ca-emision-informe-legal', field=state,
        custom=dict(label=CaseStateLabelEnum.EMISION_INFORME_LEGAL))
    def go_ca_emision_informe_legal(self):
        """
        Emisión de informe legal
        """
        pass

    @transition(source=['ca-emision-informe-legal','merged'], target='ca-devolver-a-legal', field=state,
        custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_LEGAL))
    def go_ca_devolver_a_legal(self):
        """
        Devolver a legal
        """
        pass

    @transition(source=['ca-emision-informe-legal','ca-devolver-a-comision', 'merged'], target='ca-determinacion-final',
                field=state, custom=dict(label=CaseStateLabelEnum.DETERMINACION_FINAL))
    def go_ca_determinacion_final(self):
        """
        Determinación Final
        """
        pass

    @transition(source=['co-new', 'closed'], target='co-case-type-confirmed', conditions=[has_materia, has_date_accepted],
                field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_co_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    # start process. goes to investigator
    @transition(source=['co-case-type-confirmed','merged'], target='co-enviado-a-investigador', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIADO_A_INVESTIGADOR))
    def go_co_enviado_a_investigador(self):
        """
        Enviado a investigador
        """
        pass

    @transition(source=['co-enviado-a-investigador', 'co-reinvestigar-caso', 'co-notifica-partes-desestimacion', 'merged'],
                target='co-informe-investigador', field=state,
                custom=dict(label=CaseStateLabelEnum.INFORME_INVESTIGADOR))
    def go_co_informe_investigador(self):
        """
        Informe investigador
        """
        pass


    @transition(source=['co-informe-investigador','merged'], target='co-reinvestigar-caso', field=state,
        custom=dict(label=CaseStateLabelEnum.REINVESTIGAR_CASO))
    def go_co_reinvestigar_caso(self):
        """
        Reinvestigar caso
        """
        pass

    @transition(source=['co-informe-investigador','merged'], target='co-enviado-a-ma', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIAR_A_MA))
    def go_co_enviado_a_ma(self):
        """
        Enviar a MA
        """
        pass

    @transition(source=['co-enviado-a-ma','merged'], target='co-devolver-a-comision', field=state,
        custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_COMISION))
    def go_co_devolver_a_comision(self):
        """
        Devolver a comisión
        """
        pass

    @transition(source=['co-informe-investigador','merged'], target='co-notifico-partes-desestimacion', field=state,
        custom=dict(label=CaseStateLabelEnum.CASO_DESESTIMADO))
    def go_co_notifico_partes_desestimacion(self):
        """
        Caso desestimado
        """
        pass

    @transition(source=['co-informe-investigador','merged'], target='co-notifica-querella-aviso-de-audiencia', field=state,
        custom=dict(label=CaseStateLabelEnum.NOTIFICAR_QUERELLA))
    def go_co_notifica_querella_aviso_de_audiencia(self):
        """
        Notificar querella
        """
        pass

    @transition(source=['co-notifico-partes-desestimacion','merged'], target='co-no-reconsideracion-closed', field=state,
        custom=dict(label=CaseStateLabelEnum.NO_RECONSIDERACION))
    def go_co_no_reconsideracion_closed(self):
        """
        No reconsideración / Cerrar
        """
        pass

    @transition(source=['co-notifica-querella-aviso-de-audiencia','merged'], target='co-enviado-a-legal', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIAR_A_LEGAL))
    def go_co_enviado_a_legal(self):
        """
        Enviar a legal
        """
        pass

    # legal department
    @transition(source=['co-enviado-a-legal', 'co-devolver-a-legal', 'merged'], target='co-emision-informe-legal', field=state,
        custom=dict(label=CaseStateLabelEnum.EMISION_INFORME_LEGAL))
    def go_co_emision_informe_legal(self):
        """
        Emisión de informe legal
        """
        pass

    @transition(source=['co-emision-informe-legal','merged'], target='co-devolver-a-legal', field=state,
         custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_LEGAL))
    def go_co_devolver_a_legal(self):
        """
        Devolver a legal
        """
        pass

    @transition(source=['co-emision-informe-legal','co-devolver-a-comision', 'merged'], target='co-determinacion-final',
                field=state,  custom=dict(label=CaseStateLabelEnum.DETERMINACION_FINAL))
    def go_co_determinacion_final(self):
        """
        Determinación Final
        """
        pass

    ## PE ##
    @transition(source=['pe-new', 'closed'], target='pe-case-type-confirmed', conditions=[has_materia, has_date_accepted],
                field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_pe_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    # start process. goes to investigator
    @transition(source=['pe-case-type-confirmed','merged'], target='pe-enviado-a-investigador', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIADO_A_INVESTIGADOR))
    def go_pe_enviado_a_investigador(self):
        """
        Enviado a investigador
        """
        pass

    @transition(source=['pe-enviado-a-investigador', 'pe-reinvestigar-caso', 'pe-notifica-partes-desestimacion','merged'],
                target='pe-informe-investigador', field=state,
                custom=dict(label=CaseStateLabelEnum.INFORME_INVESTIGADOR))
    def go_pe_informe_investigador(self):
        """
        Informe investigador
        """
        pass


    @transition(source=['pe-informe-investigador','merged'], target='pe-reinvestigar-caso', field=state,
        custom=dict(label=CaseStateLabelEnum.REINVESTIGAR_CASO))
    def go_pe_reinvestigar_caso(self):
        """
        Reinvestigar caso
        """
        pass

    @transition(source=['pe-informe-investigador','merged'], target='pe-enviado-a-ma', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIAR_A_MA))
    def go_pe_enviado_a_ma(self):
        """
        Enviar a MA
        """
        pass

    @transition(source=['pe-enviado-a-ma','merged'], target='pe-devolver-a-comision', field=state,
        custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_COMISION))
    def go_pe_devolver_a_comision(self):
        """
        Devolver a comisión
        """
        pass

    @transition(source=['pe-informe-investigador','merged'], target='pe-notifico-partes-desestimacion', field=state,
        custom=dict(label=CaseStateLabelEnum.CASO_DESESTIMADO))
    def go_pe_notifico_partes_desestimacion(self):
        """
        Caso desestimado
        """
        pass

    @transition(source=['pe-informe-investigador','merged'], target='pe-notifica-querella-aviso-de-audiencia', field=state,
        custom=dict(label=CaseStateLabelEnum.NOTIFICAR_QUERELLA))
    def go_pe_notifica_querella_aviso_de_audiencia(self):
        """
        Notificar querella
        """
        pass

    @transition(source=['pe-notifico-partes-desestimacion','merged'], target='pe-no-reconsideracion-closed', field=state,
        custom=dict(label=CaseStateLabelEnum.NO_RECONSIDERACION))
    def go_pe_no_reconsideracion_closed(self):
        """
        No reconsideración / Cerrar
        """
        pass

    @transition(source=['pe-notifica-querella-aviso-de-audiencia','merged'], target='pe-enviado-a-legal', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIAR_A_LEGAL))
    def go_pe_enviado_a_legal(self):
        """
        Enviar a legal
        """
        pass

    # legal department
    @transition(source=['pe-enviado-a-legal', 'pe-devolver-a-legal','merged'], target='pe-emision-informe-legal', 
        field=state, custom=dict(label=CaseStateLabelEnum.EMISION_INFORME_LEGAL))
    def go_pe_emision_informe_legal(self):
        """
        Emisión de informe legal
        """
        pass

    @transition(source=['pe-emision-informe-legal','merged'], target='pe-devolver-a-legal', field=state, 
        custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_LEGAL))
    def go_pe_devolver_a_legal(self):
        """
        Devolver a legal
        """
        pass

    @transition(source=['pe-emision-informe-legal','pe-devolver-a-comision','merged'], target='pe-determinacion-final',
                field=state, custom=dict(label=CaseStateLabelEnum.DETERMINACION_FINAL))
    def go_pe_determinacion_final(self):
        """
        Determinación Final
        """
        pass

    # PD
    
    @transition(source=['pd-new', 'closed'], target='pd-case-type-confirmed', conditions=[has_materia, has_date_accepted],
                field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_pd_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    # start process. goes to investigator
    @transition(source=['pd-case-type-confirmed','merged'], target='pd-enviado-a-investigador', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIADO_A_INVESTIGADOR))
    def go_pd_enviado_a_investigador(self):
        """
        Enviado a investigador
        """
        pass

    @transition(source=['pd-enviado-a-investigador', 'pd-reinvestigar-caso', 'pd-notifica-partes-desestimacion','merged'],
                target='pd-informe-investigador', field=state, custom=dict(label=CaseStateLabelEnum.INFORME_INVESTIGADOR))
    def go_pd_informe_investigador(self):
        """
        Informe investigador
        """
        pass


    @transition(source=['pd-informe-investigador','merged'], target='pd-reinvestigar-caso', field=state,
        custom=dict(label=CaseStateLabelEnum.REINVESTIGAR_CASO))
    def go_pd_reinvestigar_caso(self):
        """
        Reinvestigar caso
        """
        pass

    @transition(source=['pd-informe-investigador''merged'], target='pd-enviado-a-ma', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIAR_A_MA))
    def go_pd_enviado_a_ma(self):
        """
        Enviar a MA
        """
        pass

    @transition(source=['pd-enviado-a-ma','merged'], target='pd-devolver-a-comision', field=state,
        custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_COMISION))
    def go_pd_devolver_a_comision(self):
        """
        Devolver a comisión
        """
        pass

    @transition(source=['pd-informe-investigador','merged'], target='pd-notifico-partes-desestimacion', field=state,
        custom=dict(label=CaseStateLabelEnum.CASO_DESESTIMADO))
    def go_pd_notifico_partes_desestimacion(self):
        """
        Caso desestimado
        """
        pass

    @transition(source=['pd-informe-investigador','merged'], target='pd-notifica-querella-aviso-de-audiencia', field=state,
        custom=dict(label=CaseStateLabelEnum.NOTIFICAR_QUERELLA))
    def go_pd_notifica_querella_aviso_de_audiencia(self):
        """
        Notificar querella
        """
        pass

    @transition(source=['pd-notifico-partes-desestimacion','merged'], target='pd-no-reconsideracion-closed', field=state,
        custom=dict(label=CaseStateLabelEnum.NO_RECONSIDERACION))
    def go_pd_no_reconsideracion_closed(self):
        """
        No reconsideración / Cerrar
        """
        pass

    @transition(source=['pd-notifica-querella-aviso-de-audiencia','merged'], target='pd-enviado-a-legal', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIAR_A_LEGAL))
    def go_pd_enviado_a_legal(self):
        """
        Enviar a legal
        """
        pass

    # legal department
    @transition(source=['pd-enviado-a-legal', 'pd-devolver-a-legal','merged'], target='pd-emision-informe-legal', field=state,
        custom=dict(label=CaseStateLabelEnum.EMISION_INFORME_LEGAL))
    def go_pd_emision_informe_legal(self):
        """
        Emisión de informe legal
        """
        pass

    @transition(source=['pd-emision-informe-legal','merged'], target='pd-devolver-a-legal', field=state,
        custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_LEGAL))
    def go_pd_devolver_a_legal(self):
        """
        Devolver a legal
        """
        pass

    @transition(source=['pd-emision-informe-legal','pd-devolver-a-comision','merged'], target='pd-determinacion-final',
                field=state, custom=dict(label=CaseStateLabelEnum.DETERMINACION_FINAL))
    def go_pd_determinacion_final(self):
        """
        Determinación Final
        """
        pass

    # SD
    @transition(source=['sd-new','closed'], target='sd-case-type-confirmed', conditions=[has_materia, has_date_accepted],
                field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_sd_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    # start process. goes to investigator
    @transition(source=['sd-case-type-confirmed','merged'], target='sd-enviado-a-investigador', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIADO_A_INVESTIGADOR))
    def go_sd_enviado_a_investigador(self):
        """
        Enviado a investigador
        """
        pass

    @transition(source=['sd-enviado-a-investigador', 'sd-reinvestigar-caso', 'sd-notifica-partes-desestimacion','merged'],
                target='sd-informe-investigador', field=state,
                custom=dict(label=CaseStateLabelEnum.INFORME_INVESTIGADOR))
    def go_sd_informe_investigador(self):
        """
        Informe investigador
        """
        pass


    @transition(source=['sd-informe-investigador','merged'], target='sd-reinvestigar-caso', field=state,
        custom=dict(label=CaseStateLabelEnum.REINVESTIGAR_CASO))
    def go_sd_reinvestigar_caso(self):
        """
        Reinvestigar caso
        """
        pass

    @transition(source=['sd-informe-investigador','merged'], target='sd-enviado-a-ma', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIAR_A_MA))
    def go_sd_enviado_a_ma(self):
        """
        Enviar a MA
        """
        pass

    @transition(source=['sd-enviado-a-ma','merged'], target='sd-devolver-a-comision', field=state,
        custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_COMISION))
    def go_sd_devolver_a_comision(self):
        """
        Devolver a comisión
        """
        pass

    @transition(source=['sd-informe-investigador','merged'], target='sd-notifico-partes-desestimacion', field=state,
        custom=dict(label=CaseStateLabelEnum.CASO_DESESTIMADO))
    def go_sd_notifico_partes_desestimacion(self):
        """
        Caso desestimado
        """
        pass

    @transition(source=['sd-informe-investigador','merged'], target='sd-notifica-querella-aviso-de-audiencia', field=state,
        custom=dict(label=CaseStateLabelEnum.NOTIFICAR_QUERELLA))
    def go_sd_notifica_querella_aviso_de_audiencia(self):
        """
        Notificar querella
        """
        pass

    @transition(source=['sd-notifico-partes-desestimacion', 'merged'], target='sd-no-reconsideracion-closed', field=state,
        custom=dict(label=CaseStateLabelEnum.NO_RECONSIDERACION))
    def go_sd_no_reconsideracion_closed(self):
        """
        No reconsideración / Cerrar
        """
        pass

    @transition(source=['sd-notifica-querella-aviso-de-audiencia','merged'], target='sd-enviado-a-legal', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIAR_A_LEGAL))
    def go_sd_enviado_a_legal(self):
        """
        Enviar a legal
        """
        pass

    # legal department
    @transition(source=['sd-enviado-a-legal', 'sd-devolver-a-legal', 'merged'], target='sd-emision-informe-legal', field=state,
        custom=dict(label=CaseStateLabelEnum.EMISION_INFORME_LEGAL))
    def go_sd_emision_informe_legal(self):
        """
        Emisión de informe legal
        """
        pass

    @transition(source=['sd-emision-informe-legal','merged'], target='sd-devolver-a-legal', field=state,
        custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_LEGAL))
    def go_sd_devolver_a_legal(self):
        """
        Devolver a legal
        """
        pass

    @transition(source=['sd-emision-informe-legal','sd-devolver-a-comision', 'merged'], target='sd-determinacion-final',
                field=state, custom=dict(label=CaseStateLabelEnum.DETERMINACION_FINAL))
    def go_sd_determinacion_final(self):
        """
        Determinación Final
        """
        pass

    #CD
    @transition(source=['cd-new', 'closed'], target='cd-case-type-confirmed', conditions=[has_materia, has_date_accepted],
                field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_cd_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    # start process. goes to investigator
    @transition(source=['cd-case-type-confirmed','merged'], target='cd-enviado-a-investigador',
     field=state, custom=dict(label=CaseStateLabelEnum.ENVIADO_A_INVESTIGADOR))
    def go_cd_enviado_a_investigador(self):
        """
        Enviado a investigador
        """
        pass

    @transition(source=['cd-enviado-a-investigador', 'cd-reinvestigar-caso', 'cd-notifica-partes-desestimacion', 'merged'],
                target='cd-informe-investigador', field=state, custom=dict(label=CaseStateLabelEnum.INFORME_INVESTIGADOR))
    def go_cd_informe_investigador(self):
        """
        Informe investigador
        """
        pass


    @transition(source=['cd-informe-investigador','merged'], target='cd-reinvestigar-caso',
     field=state, custom=dict(label=CaseStateLabelEnum.REINVESTIGAR_CASO))
    def go_cd_reinvestigar_caso(self):
        """
        Reinvestigar caso
        """
        pass

    @transition(source=['cd-informe-investigador','merged'], target='cd-enviado-a-ma', 
        field=state, custom=dict(label=CaseStateLabelEnum.ENVIAR_A_MA))
    def go_cd_enviado_a_ma(self):
        """
        Enviar a MA
        """
        pass

    @transition(source=['cd-enviado-a-ma','merged'], target='cd-devolver-a-comision', 
        field=state, custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_COMISION))
    def go_cd_devolver_a_comision(self):
        """
        Devolver a comisión
        """
        pass

    @transition(source=['cd-informe-investigador','merged'], target='cd-notifico-partes-desestimacion',
     field=state, custom=dict(label=CaseStateLabelEnum.CASO_DESESTIMADO))
    def go_cd_notifico_partes_desestimacion(self):
        """
        Caso desestimado
        """
        pass

    @transition(source=['cd-informe-investigador','merged'], target='cd-notifica-querella-aviso-de-audiencia',
     field=state, custom=dict(label=CaseStateLabelEnum.NOTIFICAR_QUERELLA))
    def go_cd_notifica_querella_aviso_de_audiencia(self):
        """
        Notificar querella
        """
        pass

    @transition(source=['cd-notifico-partes-desestimacion','merged'], target='cd-no-reconsideracion-closed', 
        field=state, custom=dict(label=CaseStateLabelEnum.NO_RECONSIDERACION))
    def go_cd_no_reconsideracion_closed(self):
        """
        No reconsideración / Cerrar
        """
        pass

    @transition(source=['cd-notifica-querella-aviso-de-audiencia', 'merged'], 
        target='cd-enviado-a-legal', field=state, custom=dict(label=CaseStateLabelEnum.ENVIAR_A_LEGAL))
    def go_cd_enviado_a_legal(self):
        """
        Enviar a legal
        """
        pass

    # legal department
    @transition(source=['cd-enviado-a-legal', 'cd-devolver-a-legal', 'merged'], target='cd-emision-informe-legal',
     field=state, custom=dict(label=CaseStateLabelEnum.EMISION_INFORME_LEGAL))
    def go_cd_emision_informe_legal(self):
        """
        Emisión de informe legal
        """
        pass

    @transition(source=['cd-emision-informe-legal', 'merged'], target='cd-devolver-a-legal', field=state,
      custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_LEGAL))
    def go_cd_devolver_a_legal(self):
        """
        Devolver a legal
        """
        pass

    @transition(source=['cd-emision-informe-legal','cd-devolver-a-comision', 'merged'], target='cd-determinacion-final',
                field=state, custom=dict(label=CaseStateLabelEnum.DETERMINACION_FINAL))
    def go_cd_determinacion_final(self):
        """
        Determinación Final
        """
        pass

    #MU
    @transition(source=['mu-new', 'closed'], target='mu-case-type-confirmed', conditions=[has_materia, has_date_accepted],
                field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_mu_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    # start process. goes to investigator
    @transition(source=['mu-case-type-confirmed', 'merged'], target='mu-enviado-a-investigador', field=state,
     custom=dict(label=CaseStateLabelEnum.ENVIADO_A_INVESTIGADOR))
    def go_mu_enviado_a_investigador(self):
        """
        Enviado a investigador
        """
        pass

    @transition(source=['mu-enviado-a-investigador', 'mu-reinvestigar-caso', 'mu-notifica-partes-desestimacion', 'merged'],
                target='mu-informe-investigador', field=state, custom=dict(label=CaseStateLabelEnum.INFORME_INVESTIGADOR))
    def go_mu_informe_investigador(self):
        """
        Informe investigador
        """
        pass


    @transition(source=['mu-informe-investigador','merged'], target='mu-reinvestigar-caso', field=state,
        custom=dict(label=CaseStateLabelEnum.REINVESTIGAR_CASO))
    def go_mu_reinvestigar_caso(self):
        """
        Reinvestigar caso
        """
        pass

    @transition(source=['mu-informe-investigador','merged'], target='mu-enviado-a-ma', field=state,
        custom=dict(label=CaseStateLabelEnum.ENVIAR_A_MA))
    def go_mu_enviado_a_ma(self):
        """
        Enviar a MA
        """
        pass

    @transition(source=['mu-enviado-a-ma', 'merged'], target='mu-devolver-a-comision', field=state,
        custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_COMISION))
    def go_mu_devolver_a_comision(self):
        """
        Devolver a comisión
        """
        pass

    @transition(source=['mu-informe-investigador','merged'], target='mu-notifico-partes-desestimacion', field=state,
        custom=dict(label=CaseStateLabelEnum.CASO_DESESTIMADO))
    def go_mu_notifico_partes_desestimacion(self):
        """
        Caso desestimado
        """
        pass

    @transition(source=['mu-informe-investigador', 'merged'], target='mu-notifica-querella-aviso-de-audiencia', field=state,
        custom=dict(label=CaseStateLabelEnum.NOTIFICAR_QUERELLA))
    def go_mu_notifica_querella_aviso_de_audiencia(self):
        """
        Notificar querella
        """
        pass

    @transition(source=['mu-notifico-partes-desestimacion','merged'], target='mu-no-reconsideracion-closed', field=state,
        custom=dict(label=CaseStateLabelEnum.NO_RECONSIDERACION))
    def go_mu_no_reconsideracion_closed(self):
        """
        No reconsideración / Cerrar
        """
        pass

    @transition(source=['mu-notifica-querella-aviso-de-audiencia','merged'], target='mu-enviado-a-legal', field=state,
         custom=dict(label=CaseStateLabelEnum.ENVIAR_A_LEGAL))
    def go_mu_enviado_a_legal(self):
        """
        Enviar a legal
        """
        pass

    # legal department
    @transition(source=['mu-enviado-a-legal', 'mu-devolver-a-legal', 'merged'], target='mu-emision-informe-legal', field=state,
         custom=dict(label=CaseStateLabelEnum.EMISION_INFORME_LEGAL))
    def go_mu_emision_informe_legal(self):
        """
        Emisión de informe legal
        """
        pass

    @transition(source=['mu-emision-informe-legal', 'merged'], target='mu-devolver-a-legal', field=state, 
        custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_LEGAL))
    def go_mu_devolver_a_legal(self):
        """
        Devolver a legal
        """
        pass

    @transition(source=['mu-emision-informe-legal','mu-devolver-a-comision', 'merged'], target='mu-determinacion-final',
                field=state, custom=dict(label=CaseStateLabelEnum.DETERMINACION_FINAL))
    def go_mu_determinacion_final(self):
        """
        Determinación Final
        """
        pass

    # CU
    
    @transition(source=['cu-new', 'closed'], target='cu-case-type-confirmed', field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_cu_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    @transition(source=['cu-case-type-confirmed', 'merged'], target='cu-enviar-a-investigador', field=state, custom=dict(label=CaseStateLabelEnum.ENVIADO_A_INVESTIGADOR))
    def go_cu_enviar_a_investigador(self):
        """
        Enviar caso a investigador
        """
        pass

    @transition(source=['cu-enviar-a-investigador', 'cu-reinvestigar-caso', 'merged'], target='cu-notifica-informe-investigador',
                field=state, custom=dict(label=CaseStateLabelEnum.INFORME_INVESTIGADOR))
    def go_cu_notifica_informe_investigador(self):
        """
        Informe de Investigación
        """
        pass

    @transition(source=['cu-notifica-informe-investigador', 'merged'],
                target='cu-informe-interes-sustancial',
                field=state, custom=dict(label=CaseStateLabelEnum.REMITE_INFORME_INTERES_SUSTANCIAL))
    def go_cu_informe_interes_sustancial(self):
        """
        Remite informe de interés sustancial
        """
        pass

    @transition(source=['cu-notifica-informe-investigador', 'merged'], target='cu-reinvestigar-caso', field=state,
        custom=dict(label=CaseStateLabelEnum.REINVESTIGAR_CASO))
    def go_cu_reinvestigar_caso(self):
        """
        Reinvestigar caso
        """
        pass

    @transition(source=['cu-informe-interes-sustancial','merged'], target='cu-cumple-con-interes-sustancial', field=state,
        custom=dict(label=CaseStateLabelEnum.CUMPLE_INTERES_SUSTANCIAL))
    def go_cu_cumple_con_interes_sustancial(self):
        """
        Cumple con interés sustencial
        """
        pass

    @transition(source=['cu-informe-interes-sustancial','merged'], target='cu-no-cumple-con-interes-sustancial', field=state, 
        custom=dict(label=CaseStateLabelEnum.NO_CUMPLE_INTERES_SUSTANCIAL))
    def go_cu_no_cumple_con_interes_sustancial(self):
        """
        No cumple con interés sustencial
        """
        pass

    @transition(source=['cu-no-cumple-con-interes-sustancial', 'cu-cumple-con-interes-sustancial', 'merged'], target='cu-determinacion-final', field=state,
        custom=dict(label=CaseStateLabelEnum.DETERMINACION_FINAL))
    def go_cu_determinacion_final(self):
        """
        Determinación final
        """
        pass


    # EC
    
    @transition(source=['ec-new','closed'], target='ec-case-type-confirmed', field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_ec_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    @transition(source=['ec-case-type-confirmed','merged'], target='ec-enviar-a-investigador', field=state,custom=dict(label=CaseStateLabelEnum.ENVIADO_A_INVESTIGADOR))
    def go_ec_enviar_a_investigador(self):
        """
        Enviar caso a investigador
        """
        pass

    @transition(source=['ec-enviar-a-investigador', 'ec-reinvestigar-caso', 'merged'], target='ec-notifica-informe-investigador',
                field=state, custom=dict(label=CaseStateLabelEnum.INFORME_INVESTIGADOR))
    def go_ec_notifica_informe_investigador(self):
        """
        Informe de Investigación
        """
        pass

    @transition(source=['ec-notifica-informe-investigador','merged'],
                target='ec-informe-interes-sustancial',
                field=state, custom=dict(label=CaseStateLabelEnum.REMITE_INFORME_INTERES_SUSTANCIAL))
    def go_ec_informe_interes_sustancial(self):
        """
        Remite informe de interés sustancial
        """
        pass

    @transition(source=['ec-notifica-informe-investigador','merged'], target='ec-reinvestigar-caso', field=state,
        custom=dict(label=CaseStateLabelEnum.REINVESTIGAR_CASO))
    def go_ec_reinvestigar_caso(self):
        """
        Reinvestigar caso
        """
        pass

    @transition(source=['ec-informe-interes-sustancial', 'merged'], target='ec-cumple-con-interes-sustancial', field=state,
        custom=dict(label=CaseStateLabelEnum.CUMPLE_INTERES_SUSTANCIAL))
    def go_ec_cumple_con_interes_sustancial(self):
        """
        Cumple con interés sustencial
        """
        pass

    @transition(source=['ec-informe-interes-sustancial', 'merged'], target='ec-no-cumple-con-interes-sustancial', field=state,
         custom=dict(label=CaseStateLabelEnum.NO_CUMPLE_INTERES_SUSTANCIAL))
    def go_ec_no_cumple_con_interes_sustancial(self):
        """
        No cumple con interés sustencial
        """
        pass

    @transition(source=['ec-no-cumple-con-interes-sustancial', 'ec-cumple-con-interes-sustancial', 'merged'],
     target='ec-determinacion-final', field=state, custom=dict(label=CaseStateLabelEnum.DETERMINACION_FINAL))
    def go_ec_determinacion_final(self):
        """
        Determinación final
        """
        pass


    # SA
    @transition(source=['sa-new', 'closed'], target='sa-case-type-confirmed', field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_sa_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    @transition(source=['sa-case-type-confirmed','merged'], target='sa-enviar-a-legal', field=state,
     custom=dict(label=CaseStateLabelEnum.ENVIAR_A_LEGAL))
    def go_sa_enviar_a_legal(self):
        """
        Enviar caso a legal
        """
        pass

    @transition(source=['sa-enviar-a-legal', 'sa-devolver-oficial-examinador','merged'], target='sa-notifica-informe-oficial-examinador',
                field=state, custom=dict(label=CaseStateLabelEnum.INFORME_INVESTIGADOR))
    def go_sa_notifica_informe_oficial_examinador(self):
        """
        Informe oficial examinador
        """
        pass

    @transition(source=['sa-notifica-informe-oficial-examinador', 'merged'], target='sa-devolver-oficial-examinador', field=state,
        custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_LEGAL ))
    def go_sa_devolver_oficial_examinador(self):
        """
        Devolver oficial examinador
        """
        pass

    @transition(source=['sa-notifica-informe-oficial-examinador', 'merged'], target='sa-determinacion-final', field=state,
        custom=dict(label=CaseStateLabelEnum.DETERMINACION_FINAL))
    def go_sa_determinacion_final(self):
        """
        Determinación final
        """
        pass

    # SM
    @transition(source=['sm-new', 'closed'], target='sm-case-type-confirmed', field=state,custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_sm_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    @transition(source=['sm-case-type-confirmed','merged'], target='sm-enviar-a-legal', field=state, custom=dict(label=CaseStateLabelEnum.ENVIAR_A_LEGAL))
    def go_sm_enviar_a_legal(self):
        """
        Enviar caso a legal
        """
        pass

    @transition(source=['sm-enviar-a-legal', 'sm-devolver-oficial-examinador','merged'], target='sm-notifica-informe-oficial-examinador',
                field=state, custom=dict(label=CaseStateLabelEnum.INFORME_INVESTIGADOR))
    def go_sm_notifica_informe_oficial_examinador(self):
        """
        Informe oficial examinador
        """
        pass

    @transition(source=['sm-notifica-informe-oficial-examinador','merged'], target='sm-devolver-oficial-examinador',
     field=state, custom=dict(label=CaseStateLabelEnum.DEVOLVER_A_LEGAL))
    def go_sm_devolver_oficial_examinador(self):
        """
        Devolver oficial examinador
        """
        pass

    @transition(source=['sm-notifica-informe-oficial-examinador', 'merged'], target='sm-determinacion-final', field=state,
        custom=dict(label=CaseStateLabelEnum.DETERMINACION_FINAL))
    def go_sm_determinacion_final(self):
        """
        Determinación final
        """
        pass

    # PR
    @transition(source=['pr-new', 'closed'], target='pr-case-type-confirmed', field=state, custom=dict(label=CaseStateLabelEnum.CASE_TYPE_CONFIRMED))
    def go_pr_case_type_confirmed(self):
        """
        Confirmar tipo de caso
        """
        self.did_confirm_case_type = True

        # Set new number only for cases that where not imported
        if not self.was_imported():
            self.number = self.generate_case_number(self.case_type)

    @transition(source=['pr-case-type-confirmed', 'merged'], target='pr-enviar-a-investigador', field=state, custom=dict(label=CaseStateLabelEnum.ENVIADO_A_INVESTIGADOR))
    def go_pr_enviar_a_investigador(self):
        """
        Enviar caso a investigador
        """
        pass

    @transition(source=['pr-enviar-a-investigador', 'pr-reinvestigar-caso', 'merged'], target='pr-notifica-informe-investigador',
                field=state, custom=dict(label=CaseStateLabelEnum.INFORME_INVESTIGADOR))
    def go_pr_notifica_informe_investigador(self):
        """
        Informe de Investigación
        """
        pass

    @transition(source=['pr-notifica-informe-investigador', 'merged'], target='pr-reinvestigar-caso', 
        field=state, custom=dict(label=CaseStateLabelEnum.REINVESTIGAR_CASO))
    def go_pr_reinvestigar_caso(self):
        """
        Reinvestigar caso
        """
        pass

    @transition(source=['pr-notifica-informe-investigador', 'merged'],
                target='pr-informe-interes-sustancial',
                field=state, custom=dict(label=CaseStateLabelEnum.REMITE_INFORME_INTERES_SUSTANCIAL))
    def go_pr_informe_interes_sustancial(self):
        """
        Remite informe de interés sustancial
        """
        pass


    @transition(source=['pr-informe-interes-sustancial', 'merged'], target='pr-cumple-con-interes-sustancial', field=state,
        custom=dict(label=CaseStateLabelEnum.CUMPLE_INTERES_SUSTANCIAL))
    def go_pr_cumple_con_interes_sustancial(self):
        """
        Cumple con interés sustencial
        """
        pass

    @transition(source=['pr-informe-interes-sustancial', 'merged'], target='pr-no-cumple-con-interes-sustancial', field=state,
        custom=dict(label=CaseStateLabelEnum.NO_CUMPLE_INTERES_SUSTANCIAL))
    def go_pr_no_cumple_con_interes_sustancial(self):
        """
        No cumple con interés sustencial
        """
        pass

    @transition(source=['pr-no-cumple-con-interes-sustancial', 'merged'], target='pr-solicitud-archivada', field=state,
        custom=dict(label=CaseStateLabelEnum.SOLICITUD_ARCHIVADA))
    def go_pr_solicitud_archivada(self):
        """
        Solicitud archivada
        """
        pass


    @transition(source=['pr-cumple-con-interes-sustancial', 'merged'], target='pr-eleccion-ordenada', field=state,
        custom=dict(label=CaseStateLabelEnum.ELECCION_ORDENADA))
    def go_pr_eleccion_ordenada(self):
        """
        Elección ordenada
        """
        pass

    @transition(source=['pr-eleccion-ordenada','merged'], target='pr-resultados',
     field=state, custom=dict(label=CaseStateLabelEnum.RESULTADOS))
    def go_pr_resultados(self):
        """
        Resultados
        """
        pass

    @transition(source='*', target='closed', conditions=[has_closing_document], 
        field=state, custom=dict(label=CaseStateLabelEnum.CERRAR_CASO))
    def go_closed(self):
        """
        Cerrar caso
        """
        self.date_closed = datetime.now()
        pass

    @transition(source='*', target='merged', field=state)
    def go_merged(self):
        """
        Caso consolidado
        """
        pass
    


class CaseCategory(models.Model):
    '''
    Materia
    '''
    name = models.CharField(max_length=60)
    description = models.TextField()


    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Case categories'


class CaseSequence(models.Model):
    case_type = models.ForeignKey('CaseType')
    year = models.IntegerField()
    last_id = models.IntegerField()

    def __unicode__(self):
        return self.case_type.name

    @classmethod
    def next(self, case_type):
        print(case_type)
        try:
            cs = CaseSequence.objects.get(case_type=case_type, year=now().year)
            cs.last_id += 1
            cs.save()
            return cs.last_id

        except CaseSequence.DoesNotExist:

            new_cs = CaseSequence.objects.create(
                case_type=case_type, year=now().year, last_id=1)
            return new_cs.last_id
