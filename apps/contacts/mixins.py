from django.core.exceptions import PermissionDenied


class ProtectCreateMixin(object):
    """
    Validates user's permission to create a contact
    """

    def dispatch(self, request, *args, **kwargs):
        response = super(ProtectCreateMixin, self).dispatch(
            request, *args, **kwargs)

        user = request.user

        user_group_permissions = user.get_group_permissions()

        # Both group and user permissions are validated. If user possesses none a PermissionDenied error is raised
        if (not user_group_permissions.issuperset(['contacts.add_contact']) and
                not user.has_perm('contacts.add_contact')):
            raise PermissionDenied

        return response


class ProtectUpdateMixin(object):
    '''
    Validates user's permission to edit a contact
    '''

    def get_object(self):
        contact = super(ProtectUpdateMixin, self).get_object()

        user = self.request.user

        user_group_permissions = user.get_group_permissions()

        # Both group and user permissions are validated. If user possesses none a PermissionDenied error is raised
        if (not user_group_permissions.issuperset(['contacts.change_contact']) and
                not user.has_perm('contacts.change_contact')):
            raise PermissionDenied

        return contact


class ProtectDeleteMixin(object):
    '''
    Validates user's permission to delete a contact
    '''

    def get_object(self):
        contact = super(ProtectDeleteMixin, self).get_object()

        user = self.request.user

        user_group_permissions = user.get_group_permissions()

        # Both group and user permissions are validated. If user possesses none a PermissionDenied error is raised
        if (not user_group_permissions.issuperset(['contacts.delete_contact']) and
                not user.has_perm('contacts.delete_contact')):
            raise PermissionDenied

        return contact
