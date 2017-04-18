# -*- coding: utf-8 -*-

from django import forms

from ...utils.widgets import DateTimePickerInput


class ExtraForm(forms.Form):
    direccion_representate_exclusivo = forms.CharField(
        required=False, widget=forms.Textarea(attrs={'class': 'form-control'}), label=u'Nombre y dirección del Representante Exclusivo')

    tipo = forms.ChoiceField(
        required=False,
        label='Seleccione uno de los siguentes',
        choices=(
            ('', '------'),
            ('quejas_agravios', 'Solicitud de Arbitraje de Quejas y Agravios'),
            ('notificacion_estancamiento', 'Notificación de Estancamiento en la Negociación de un Convenio'),
            ('arbitraje_obligatorio', 'Solicitud de Arbitraje Obligatorio'),
            ('mediacion', u'Mediación')
        )
    )

    procedimiento_establecido = forms.BooleanField(
        required=False,
        label=u'¿Se cumplió con el procedimiento establecido en el convenio '
        'colectivo antes de solicitar arbitraje?'
    )

    fecha_de_efectividad_convenio = forms.DateTimeField(
        widget=DateTimePickerInput(attrs={'class': 'form-control'}),
        required=False
    )

    fecha_de_vencimiento_convenio = forms.DateTimeField(
        widget=DateTimePickerInput(attrs={'class': 'form-control'}),
        required=False
    )

    solicitada_por = forms.ChoiceField(
        required=False,
        label='Esta solicitud es radicada por',
        choices=(
            ('', '------'),
            ('representante', 'Representate exclusivo'),
            ('agencia', 'Agencia'),
            ('empleado', 'Empleado')
        )
    )

    otro_foro = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control'}),
        label=u'Si ha sometido la controversia a otro foro, indique el foro, número de caso y fecha de presentación'
    )

    descripcion_hechos = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        label=u'Descripción de hechos y controversia o cláusulas sobre las que existe estancamiento'
    )

    remedio_solicitado = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        label=u'Remedio solicitado o posición de la parte promoverte en caso de estancamiento'
    )

    sometida_por = forms.ChoiceField(
        required=False,
        label=u'Notificaión sometida por (Sólo en caso de Notificación de Estancamiento en la Negociación de un convenio)',
        choices=(
            ('', '------'),
            ('agencia', 'Agencia'),
            ('union', u'Unión'),
            ('acuerdo', u'Acuerdo de las Partes')
        )
    )

    fecha_comienzo_conciliacion = forms.DateTimeField(
        widget=DateTimePickerInput(attrs={'class': 'form-control'}),
        required=False
    )

    fecha_culminacion = forms.DateTimeField(
        widget=DateTimePickerInput(attrs={'class': 'form-control'}),
        required=False
    )

    descripcion_estancamiento = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        label=u'Descripción detallada de las áreas donde existe un estancamiento en las negociaciones (por cláusula o categoría)'
    )
