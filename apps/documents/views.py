from django.views.generic import CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from braces.views import LoginRequiredMixin

from .models import Document, DocumentType
from .forms import DocumentCreationForm

from ..cases.models import Case

from django.http import HttpResponse, StreamingHttpResponse
import os
from django.core.files import File
from docxtpl import DocxTemplate
       
import datetime

import logging
logger = logging.getLogger(__name__)

class DocumentCreateView(LoginRequiredMixin, CreateView):

    '''
    Creates a document for the current case
    '''
    model = Document
    form_class = DocumentCreationForm

    def get_success_url(self):
        cache.clear()
        return reverse_lazy('case_detail', args=[self.kwargs['pk']])

    def get_initial(self):
        # Pre-fill form with case and created_by user
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

        return {
            'case': self.case,
            'created_by': self.request.user
        }

    def post(self, request, pk, *args, **kwargs):

        form = DocumentCreationForm(self.request.POST)
        if form.is_valid():
            document_type = form.cleaned_data['document_type']

        path_to_file = os.path.realpath("apps/documents/templates/files/" + document_type.get_template_name())
        self.case = get_object_or_404(Case, pk=self.kwargs['pk'])

        date = datetime.datetime.now()
        
        doc = DocxTemplate(path_to_file)

        co_apelantes = ''
        another_contacts = self.case.get_all_contacts()[:-2]

        for c in another_contacts:
            co_apelantes = co_apelantes + ',' + c.get_name() + '\n'
        
        logger.debug(co_apelantes)

        context = { 
            'APELANTE' : self.case.plaintiff.get_name(),
            'APELADA': self.case.defendant.get_name(),
            'NUM_CASO': self.case.number,
            'MATERIA': self.case.case_category.name,
            'fcreado': date.strftime("%d/%m/%y"),
            'NOMBREAPE': self.case.plaintiff.get_name(),
            'COAPELANTES': co_apelantes
        }
        doc.render(context)
        name_file = document_type.get_download_file_name(self.case.number)
        path_to_file_for_download = os.path.realpath("apps/documents/templates/files/" + name_file)
        doc.save(path_to_file_for_download)

        f = open(path_to_file_for_download, 'r')
        myfile = File(f)
        response = StreamingHttpResponse(myfile, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename=' + name_file
        os.remove(path_to_file_for_download)
        return response

    def get_context_data(self, *args, **kwargs):
        context = super(DocumentCreateView, self).get_context_data(**kwargs)

        # Add case to context, used by cancel button link
        context['case'] = self.case
       
        
        return context
