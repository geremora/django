from django.core.exceptions import PermissionDenied


class ProtectBugsCreateMixin(object):

    """
    Prevent edit from users that should not be creating contacts
    """

    def get_object(self):
        bug = super(ProtectBugsCreateMixin, self).get_object()

        user = self.request.user

        user_group_permissions = user.get_group_permissions()

        if (not user_group_permissions.issuperset(['bugs.add_bug']) and
                not user.has_perm('bugs.add_bug')):
            raise PermissionDenied

        return bug
