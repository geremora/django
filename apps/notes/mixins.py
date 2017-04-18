from django.core.exceptions import PermissionDenied


class ProtectAcceptancePerfomedMixin(object):

    def get_object(self):
        note = super(ProtectAcceptancePerfomedMixin, self).get_object()

        if note.accepted is not None:
            raise PermissionDenied

        return note


class ProtectNoteCreateMixin(object):

    '''
    Prevent edit from users that should not be creating contacts
    '''

    def dispatch(self, request, *args, **kwargs):
        response = super(ProtectNoteCreateMixin, self).dispatch(
            request, *args, **kwargs)

        user = self.request.user

        user_group_permissions = user.get_group_permissions()

        if (not user_group_permissions.issuperset(['notes.add_note']) and
                not user.has_perm('notes.add_note')):
            if self.case.case_type.code == 'AO':
                if (not user_group_permissions.issuperset(['notes.can_add_note_AO']) and not user.has_perm('notes.can_add_note_AO')) or \
                        (user == self.case.assigned_user and (not user_group_permissions.issuperset(['notes.can_add_note_own_AO']) and not user.has_perm('notes.can_add_note_own_AO'))):
                    raise PermissionDenied
            elif self.case.case_type.code == 'AQ':
                if (not user_group_permissions.issuperset(['notes.can_add_note_AQ']) and not user.has_perm('notes.can_add_note_AQ')) or \
                        (user == self.case.assigned_user and (not user_group_permissions.issuperset(['notes.can_add_note_own_AQ']) and not user.has_perm('notes.can_add_note_own_AQ'))):
                    raise PermissionDenied
            else:
                if (not user_group_permissions.issuperset(['notes.can_add_note_XX']) and not user.has_perm('notes.can_add_note_XX')) or \
                        (user == self.case.assigned_user and (not user_group_permissions.issuperset(['notes.can_add_note_own_XX']) and not user.has_perm('notes.can_add_note_own_XX'))):
                    raise PermissionDenied

        return response


class ProtectNoteUpdateMixin(object):

    '''
    Prevent edit from users that should not be making edits on contacts
    '''

    def get_object(self):
        note = super(
            ProtectNoteUpdateMixin, self).get_object()

        user = self.request.user

        user_group_permissions = user.get_group_permissions()

        if (not user_group_permissions.issuperset(['notes.change_note']) and
                not user.has_perm('notes.change_note')):
            raise PermissionDenied

        return note


class ProtectNoteDeleteMixin(object):

    '''
    Prevent edit from users that should not be able to delete a contact.
    '''

    def get_object(self):
        note = super(
            ProtectNoteDeleteMixin, self).get_object()

        user = self.request.user

        user_group_permissions = user.get_group_permissions()

        if (not user_group_permissions.issuperset(['notes.delete_note']) and
                not user.has_perm('notes.delete_note')):
            raise PermissionDenied

        return note
