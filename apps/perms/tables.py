import django_tables2 as tables
from django_tables2.utils import A
from ..profiles.models import CaspUser


class CaspUserTable(tables.Table):
    username = tables.LinkColumn(verbose_name='Usuario', viewname='perms-user-detail', args=[A('pk')])
    name = tables.Column(verbose_name='Nombre', accessor=A('get_full_name'), orderable=False)
    email = tables.EmailColumn(verbose_name='Email')

    class Meta:
        model = CaspUser
        fields = ('username', 'name', 'email')
        attrs = {"class": "paleblue table table-striped"}
        template = 'django-tables2/bootstrap-base.html'


class CaspUserPermissionsTable(tables.Table):
    name = tables.Column(verbose_name='Permiso')
    has_perm = tables.Column(verbose_name='Estado del Permiso')

    class Meta:
        attrs = {"class": "paleblue table table-striped"}
        template = 'django-tables2/bootstrap-perms.html'

    def render_has_perm(self, record):
        pass
