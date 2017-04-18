from apps.cases.models import Case
from django.core.exceptions import PermissionDenied


class ProtectAcceptancePerfomedMixin(object):

    def get_object(self):
        event = super(ProtectAcceptancePerfomedMixin, self).get_object()

        if event.accepted is not None:
            raise PermissionDenied

        return event


class ProtectIncomingEventCreateMixin(object):

    '''
    Prevent edit from users that should not be creating contacts
    '''

    def dispatch(self, request, *args, **kwargs):
        response = super(ProtectIncomingEventCreateMixin, self).dispatch(request, *args, **kwargs)

        case_type = self.case.case_type.code

        user = self.request.user

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['events.add_incomingevent']) and not user.has_perm('events.add_incomingevent'):
            if ((not user_group_permissions.issuperset['events.add_incomingevent_{}'.format(case_type)] and not user.has_perm('events.add_incomingevent_{}'.format(case_type))) or
                (not user_group_permissions.issuperset['events.add_incomingevent_own_{}'.format(case_type)] and not user.has_perm('events.add_incomingevent_own_{}'.format(case_type)))):
                    raise PermissionDenied

        return response


class ProtectIncomingEventUpdateMixin(object):

    '''
    Prevent edit from users that should not be making edits on contacts
    '''

    def get_object(self):
        event = super(
            ProtectIncomingEventUpdateMixin, self).get_object()

        user = self.request.user

        case = Case.objects.get(pk=self.kwargs['pk'])
        case_type = case.case_type.code

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['events.change_incomingevent']) and not user.has_perm('events.change_incomingevent'):
            if ((not user_group_permissions.issuperset['events.change_incomingevent_{}'.format(case_type)] and not user.has_perm('events.change_incomingevent_{}'.format(case_type))) or
                (not user_group_permissions.issuperset['events.change_incomingevent_own_{}'.format(case_type)] and not user.has_perm('events.change_incomingevent_own_{}'.format(case_type)))):
                    raise PermissionDenied

        return event


class ProtectIncomingEventDeleteMixin(object):

    '''
    Prevent edit from users that should not be able to delete a contact.
    '''

    def get_object(self):
        event = super(
            ProtectIncomingEventDeleteMixin, self).get_object()

        user = self.request.user

        case = Case.objects.get(pk=self.kwargs['pk'])
        case_type = case.case_type.code

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['events.delete_incomingevent']) and not user.has_perm('events.delete_incomingevent'):
            if ((not user_group_permissions.issuperset['events.delete_incomingevent_{}'.format(case_type)] and not user.has_perm('events.delete_incomingevent_{}'.format(case_type))) or
                (not user_group_permissions.issuperset['events.delete_incomingevent_own_{}'.format(case_type)] and not user.has_perm('events.delete_incomingevent_own_{}'.format(case_type)))):
                    raise PermissionDenied

        return event


class ProtectOutgoingEventCreateMixin(object):

    '''
    Prevent edit from users that should not be creating contacts
    '''

    def get_object(self):
        event = super(
            ProtectOutgoingEventCreateMixin, self).get_object()

        user = self.request.user

        case = Case.objects.get(pk=self.kwargs['pk'])
        case_type = case.case_type.code

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['events.add_outgoingevent']) and not user.has_perm('events.add_outgoingevent'):
            if ((not user_group_permissions.issuperset['events.add_outgoingevent_{}'.format(case_type)] and not user.has_perm('events.add_outgoingevent_{}'.format(case_type))) or
                (not user_group_permissions.issuperset['events.add_outgoingevent_own_{}'.format(case_type)] and not user.has_perm('events.add_outgoingevent_own_{}'.format(case_type)))):
                    raise PermissionDenied

        return event


class ProtectOutgoingEventUpdateMixin(object):

    '''
    Prevent edit from users that should not be making edits on contacts
    '''

    def get_object(self):
        event = super(ProtectOutgoingEventUpdateMixin, self).get_object()

        user = self.request.user

        case = Case.objects.get(pk=self.kwargs['pk'])
        case_type = case.case_type.code

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['events.change_outgoingevent']) and not user.has_perm('events.change_outgoingevent'):
            if ((not user_group_permissions.issuperset['events.change_outgoingevent_{}'.format(case_type)] and not user.has_perm('events.change_outgoingevent_{}'.format(case_type))) or
                (not user_group_permissions.issuperset['events.change_outgoingevent_own_{}'.format(case_type)] and not user.has_perm('events.change_outgoingevent_own_{}'.format(case_type)))):
                    raise PermissionDenied

        return event


class ProtectOutgoingEventDeleteMixin(object):

    '''
    Prevent edit from users that should not be able to delete a contact.
    '''

    def get_object(self):
        event = super(ProtectOutgoingEventDeleteMixin, self).get_object()

        user = self.request.user

        case = Case.objects.get(pk=self.kwargs['pk'])
        case_type = case.case_type.code

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['events.delete_outgoingevent']) and not user.has_perm('events.delete_outgoingevent'):
            if ((not user_group_permissions.issuperset['events.delete_outgoingevent_{}'.format(case_type)] and not user.has_perm('events.delete_outgoingevent_{}'.format(case_type))) or
                (not user_group_permissions.issuperset['events.delete_outgoingevent_own_{}'.format(case_type)] and not user.has_perm('events.delete_outgoingevent_own_{}'.format(case_type)))):
                    raise PermissionDenied

        return event


class ProtectImportedEventCreateMixin(object):

    '''
    Prevent edit from users that should not be making edits on contacts
    '''

    def dispatch(self, request, *args, **kwargs):

        response = super(ProtectImportedEventCreateMixin, self).dispatch(request, *args, **kwargs)

        user = self.request.user

        case = Case.objects.get(pk=self.kwargs['pk'])
        case_type = case.case_type.code

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['events.add_importedevent']) and not user.has_perm('events.add_importedevent'):
            if ((not user_group_permissions.issuperset['events.add_importedevent_{}'.format(case_type)] and not user.has_perm('events.add_importedevent_{}'.format(case_type))) or
                (not user_group_permissions.issuperset['events.add_importedevent_own_{}'.format(case_type)] and not user.has_perm('events.add_importedevent_own_{}'.format(case_type)))):
                    raise PermissionDenied

        return response


class ProtectImportedEventUpdateMixin(object):

    '''
    Prevent edit from users that should not be making edits on contacts
    '''

    def get_object(self):
        event = super(ProtectImportedEventUpdateMixin, self).get_object()

        user = self.request.user

        case = Case.objects.get(pk=self.kwargs['pk'])
        case_type = case.case_type.code

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['events.change_importedevent']) and not user.has_perm('events.change_importedevent'):
            if ((not user_group_permissions.issuperset['events.change_importedevent_{}'.format(case_type)] and not user.has_perm('events.change_importedevent_{}'.format(case_type))) or
                (not user_group_permissions.issuperset['events.change_importedevent_own_{}'.format(case_type)] and not user.has_perm('events.change_importedevent_own_{}'.format(case_type)))):
                    raise PermissionDenied

        return event
