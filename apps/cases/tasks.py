# coding: utf-8
import os

from celery import shared_task
from apps.profiles.models import CaspUser
from .models import Case, CaseContainer, CaseContainerAction, CaseContainerActionSequence
from django.core.mail import EmailMultiAlternatives
from datetime import datetime

from django.conf import settings

@shared_task
def unmerge_cases(case_id_list, username, action_seq):
    task_start_date = datetime.now()

    case_nums_for_html_email = ''
    case_nums_for_txt_email = ''

    unmerged_container = 0

    for case_id in case_id_list:
        case = Case.objects.get(pk=case_id)
        unmerged_container = CaseContainer.unmerge_cases([case])
        CaseContainerAction.create_case_container_action(action_seq=action_seq, container=unmerged_container.id,
                                                         action_type='unmerge', case=case, user=username)

        case_nums_for_html_email += '<li>{}</li>'.format(case.number)
        case_nums_for_txt_email += '{}'.format(case.number) + os.linesep

    task_end_date = datetime.now()

    msg_body = create_txt_email(action_seq, case_nums_for_txt_email, task_start_date, task_end_date)

    msg_html_body = create_html_email(action_seq, case_nums_for_html_email, task_start_date, task_end_date)

    user = CaspUser.objects.get(username=username)

    msg = EmailMultiAlternatives(subject='Descosolidación: {}'.format(action_seq), body=msg_body,
                                 from_email=settings.DEFAULT_EMAIL_FROM, to=[user.email])

    msg.attach_alternative(content=msg_html_body, mimetype='text/html')
    msg.send()

    return "Container unmergeed: {}".format(str(unmerged_container.id))


def create_html_email(action_seq, email_body, task_start_date, task_end_date):
    """
    Formats the email body for a HTML email.
    :param action_seq:
    :param email_body:
    :param task_start_date:
    :param task_end_date:
    :return:
    """
    return u"""
        <div style="max-width: 500px; min-width: 300px; font-family: helvetica, arial, sans-serif;margin: auto;">
            <p>Su desconsolidación termino exitosamente.</p>
            <h2 id="toc_0">Desconsolidación: {}</h2>
            <hr />
            <p><b>Casos:</b> </p>
            <ul style="list-style: none"> {} </ul>
            <p><b>Fecha Pedido:</b> {}</p>
            <p><b>Fecha Completada:</b> {}</p>
        </div>
    """.format(action_seq, email_body, task_start_date, task_end_date)


def create_txt_email(action_seq, email_body, task_start_date, task_end_date):
    """
    Formats the email body for a text email.
    :param action_seq:
    :param email_body:
    :param task_start_date:
    :param task_end_date:
    :return:
    """
    return """
    Su desconsolidación termino exitosamente.

    Desconsolidación: {}

    Casos:
    {}

    Fecha Pedido: {}
    Fecha Completada: {}
    """.format(action_seq, email_body, task_start_date, task_end_date)