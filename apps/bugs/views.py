# -*- coding: utf-8 -*-

from django.views.generic import CreateView
from django.core.urlresolvers import reverse_lazy
from django.core.mail import mail_admins, send_mail

from braces.views import LoginRequiredMixin

from .models import Bug
from .forms import BugCreationForm
from .mixins import ProtectBugsCreateMixin
from django.conf import settings

class BugsCreateView(LoginRequiredMixin, ProtectBugsCreateMixin, CreateView):
    model = Bug
    success_url = reverse_lazy('case_list')
    form_class = BugCreationForm

    def get_form_kwargs(self):
        kwargs = super(BugsCreateView, self).get_form_kwargs()
        kwargs['created_by'] = self.request.user
        return kwargs

    def form_valid(self, form):
        '''
        Send email to admins (bugs and feature requests)
            Corrections are sent to users in QUALITY_ASSURANCE list
        '''
        # TODO: Make into async task
        subject = u'{} Report'.format(
            form.cleaned_data['bug_type'].capitalize())
        message = u"""Type: {}
        From: {} - {}

        {}""".format(form.cleaned_data['bug_type'].capitalize(),
                     self.request.user, self.request.user.email,
                     form.cleaned_data['message'])

        # Send emails
        if form.cleaned_data['bug_type'] == 'correction':
            send_mail(
                subject, message, 'casp@ml42.com', settings.QUALITY_ASSURANCE)
        else:
            mail_admins(subject, message)

        return super(BugsCreateView, self).form_valid(form)
