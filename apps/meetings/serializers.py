# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

__author__ = 'sandlbn'

import json
from datetime import datetime
from django.db.models.query import QuerySet
from django.test.client import RequestFactory

def meeting_serializer(meetings, assigned_officials, user):
    """
    serialize event model
    """
    objects_body = []
    meetings_css_class = {
        'did_happen': 'event-success',
        'cancelled': 'event-important',
        'scheduled': 'event-info'
    }

    meeting_type = {
        'status': 'Vista de Estatus',
        'arbitraje': 'Vista de Arbitraje',
        'continuacion': 'Continuacion de Vista',
        'mediacion': 'Sesion de Medicion',
    }

    case_type_colors = {
        'CD': 'CD6889',
        'SM': '00CD66',
        'SA': 'FFFF00',
        'EC': '8B7500',
        'CU': 'FF0000',
        'MU': '388E8E',
        'SD': 'FF7D40',
        'PD': '8B8682',
        'PE': '006400',
        'CO': '00EEEE',
        'CA': '2F4F4F',
        'PR': '00F5FF',
        'AQ': '9400D3',
        'AO': '1C86EE',
        'XX': '000000',
    }

    meeting_title = "{5} - {0} para Caso: {1} en Sala: {2}. Peticionario: {3}, Peticionado: {4}, Asignado a: {6}"

    if isinstance(meetings, QuerySet):
        for meeting in meetings:
            if meeting.case:
                case = meeting.case
            elif meeting.cases:
                case_list = meeting.cases.all()
                if len(case_list) > 0:
                    case = case_list[0]
            else:
                case = None

            field = {
                "id": meeting.pk,
                "title": meeting_title.format(meeting_type[meeting.meeting_type], case.number if case else ' - ',
                                              meeting.room.name, case.plaintiff, case.defendant, meeting.date_start.strftime('%I:%M:%S'), case.assigned_user),
                "case": case.number if case else ' - ',
                "room": meeting.room.name,
                "url": reverse('case_detail', kwargs={'pk': case.id}) if case else '#',
                "class": meetings_css_class[meeting.status],
                "color": case_type_colors[case.case_type.code],
                "start": int(meeting.date_start.strftime('%s')) * 1000,
                "end": int(meeting.date_end.strftime('%s')) * 1000,
            }
            objects_body.append(field)

    assigned_offical_title = "Oficial del día asignado: {0}"

    if isinstance(assigned_officials, QuerySet):
        user_group_permissions = user.get_group_permissions()

        for official in assigned_officials:
            field = {
                "id": 'OFF' + str(official.id),
                "title": assigned_offical_title.format(official.assigned_official),
                "url": '' if (not user_group_permissions.issuperset(['meetings.change_assignofficial']) and not user.has_perm('meetings.change_assignofficial')) else reverse('assign_official_update', kwargs={'pk': official.id}),
                "assigned_official": True,
                "start": int(official.assigned_date.date().strftime('%s')) * 1000,
                "end": (int(official.assigned_date.date().strftime('%s')) * 1000),
            }
            objects_body.append(field)

    objects_head = {"success": 1}
    objects_head["result"] = objects_body
    return json.dumps(objects_head)
