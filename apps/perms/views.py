from django.db.models import Q
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.models import Permission
from django.core.mail import mail_admins
from django.shortcuts import render

from braces.views._access import LoginRequiredMixin
from django_tables2.config import RequestConfig

from apps.perms.tables import CaspUserPermissionsTable
from .forms import PermsUserUpdateForm
from ..profiles.models import CaspUser
from .tables import CaspUserTable


def filter_by_search_field(term, queryset):
    # Filter permissions by search term.

    result = queryset.filter(
        Q(username__icontains=term) | Q(email__icontains=term) |
        Q(first_name__icontains=term) | Q(last_name__icontains=term)
    )

    return result


def filter_permissions(term, queryset):
    # Filter permissions by search term.

    result = queryset.filter(
        Q(name__icontains=term) | Q(codename__icontains=term))

    return result


def check_perms(user, queryset):
    # Verify the permissions of the user that is being viewed.

    permissions = []
    user_perms = []

    for perm in user.get_group_permissions():
        user_perms.append((perm.split('.', 1))[1])

    user_permissions = Permission.objects.filter(user=user)

    for perm in user_permissions:
        permission = {"name": perm.name}
        has_perm = {
            "codename": perm.codename,
            "status": True
        }
        permission["has_perm"] = has_perm
        permissions.append(permission)

    for perm in queryset.all():
        permission = {"name": perm.name}
        has_perm = {"codename": perm.codename}

        has_perm["status"] = perm.codename in user_perms
        permission["has_perm"] = has_perm

        permissions.append(permission)

    return permissions


class PermsUserListView(LoginRequiredMixin, ListView):
    template_name = 'perms/perms_user_list.html'

    def get_queryset(self):
        queryset = CaspUser.objects.filter(is_active=True)
        user = self.request.user

        if not user.is_superuser:
            queryset = CaspUser.objects.filter(is_superuser=False)

        search_field = self.request.GET.get('search')

        if search_field and queryset:
            queryset = filter_by_search_field(search_field, queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(PermsUserListView, self).get_context_data(**kwargs)

        user = self.request.user

        context['can_change_perms'] = user.has_perm('perms.can_change_perms')

        user_table = CaspUserTable(context['object_list'])
        RequestConfig(request=self.request, paginate={"per_page": 20}).configure(user_table)
        context['user_table'] = user_table

        context['object_list'] = None

        return context


class PermsUserDetailView(LoginRequiredMixin, DetailView):
    model = CaspUser
    template_name = 'perms/perms_user_detail.html'

    def get_object(self, queryset=None):
        return CaspUser.objects.get(pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super(PermsUserDetailView, self).get_context_data(**kwargs)
        user = context['object']

        permissions = Permission.objects.all()
        search_field = self.request.GET.get('search')

        # Filter permissions by search term
        if search_field and permissions:
            permissions = filter_permissions(search_field, permissions)

        permissions = check_perms(user, permissions)

        user_permissions_table = CaspUserPermissionsTable(permissions)
        RequestConfig(request=self.request, paginate={"per_page":20}).configure(user_permissions_table)
        context['user_permissions_table'] = user_permissions_table

        return context


class PermsUserUpdateView(LoginRequiredMixin, UpdateView):
    model = CaspUser
    form_class = PermsUserUpdateForm
    template_name = 'perms/perms_user_detail.html'

    def get_success_url(self):
        return reverse_lazy('perms-user-detail', args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super(PermsUserUpdateView, self).get_context_data(**kwargs)

        context['is_update'] = True

        return context


class PermsUserRequestView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        '''
            Send email to admins for permission requests
        '''

        perm = Permission.objects.get(codename=request.POST.get('codename'))
        reason = request.POST.get('reason')
        template = 'perms/perm_user_request_sent.html'

        subject = 'Permission request'
        message = (
            'User: {} - {}\n Permission name: {} \n Permission codename: {} \n Reason: {}'
        ).format(request.user.get_full_name(), request.user.email, perm.name, perm.codename, reason)

        mail_admins(subject, message)

        context = {'object': request.user}

        return render(request, template, context)
