# -*- coding: utf-8 -*-
from django.db.models import Q

from ..events.models import OutgoingEvent


def has_materia(instance):
    '''
    Los casos deben tener una materia asignada antes.
    '''
    if instance.case_category:
        return True

    return False


def has_assigned_user(instance):
    '''
    Los casos debe tener un investigador asignado.
    '''
    if instance.assigned_user:
        return True

    return False


def has_closing_document(instance):
    '''
    Para cerrar un caso es necesario emitir al menos uno de los siguientes:
    Informe final, Laudo de Arbitraje Obligatorio, Cierre por Acuerdo,
    Cierro por Desentimiento o Cierre Administrativo.
    '''
    closing_documents = OutgoingEvent.objects.filter(
        Q(cases__in=[instance]),
        Q(event_type__name='Informe Final') |
        Q(event_type__name='Laudo de Arbitraje Obligatorio') |
        Q(event_type__name='Laudo de Arbitraje') |
        Q(event_type__name='Cierre por Acuerdo') |
        Q(event_type__name='Cierre por Desistimiento') |
        Q(event_type__name='Cierre Administrativo')).count()

    if closing_documents > 0:
        return True

    return False


def has_date_accepted(instance):
    '''
    El caso necesita tener una fecha de aceptado.
    '''
    if instance.date_accepted:
        return True

    return False
