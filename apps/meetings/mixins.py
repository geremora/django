from apps.cases.models import Case
from django.core.exceptions import PermissionDenied


class ProtectAcceptancePerfomedMixin(object):

    def get_object(self):
        meeting = super(ProtectAcceptancePerfomedMixin, self).get_object()

        if meeting.accepted is not None:
            raise PermissionDenied

        return meeting


class ProtectMeetingCreateMixin(object):

    '''
    Prevent edit from users that should not be creating contacts
    '''

    def dispatch(self, request, *args, **kwargs):
        response = super(ProtectMeetingCreateMixin, self).dispatch(request, *args, **kwargs)

        user = self.request.user

        case = Case.objects.get(pk=self.kwargs['pk'])
        case_type = case.case_type.code

        user_group_permissions = user.get_group_permissions()

        if (not user_group_permissions.issuperset(['meetings.add_meeting']) and
                not user.has_perm('meetings.add_meeting')):
            raise PermissionDenied

        if not user_group_permissions.issuperset(['meetings.add_meeting']) and not user.has_perm('meetings.add_meeting'):
            if ((not user_group_permissions.issuperset(['meetings.add_meeting_{}'.format(case_type)]) and not user.has_perm('meetings.add_meeting_{}'.format(case_type))) or
                    (not user_group_permissions.issuperset(['meetings.add_meeting_own_{}'.format(case_type)]) and not user.has_perm('meetings.add_meeting_own_{}'.format(case_type)))):
                    raise PermissionDenied

        return response


class ProtectMeetingUpdateMixin(object):

    '''
    Prevent edit from users that should not be making edits on contacts
    '''

    def get_object(self):
        meeting = super(ProtectMeetingUpdateMixin, self).get_object()

        user = self.request.user

        case = Case.objects.get(pk=self.kwargs['pk'])
        case_type = case.case_type.code

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['meetings.change_meeting']) and not user.has_perm('meetings.change_meeting'):
            if ((not user_group_permissions.issuperset(['meetings.change_meeting_{}'.format(case_type)]) and not user.has_perm('meetings.change_meeting_{}'.format(case_type))) or
                    (not user_group_permissions.issuperset(['meetings.change_meeting_own_{}'.format(case_type)]) and not user.has_perm('meetings.change_meeting_own_{}'.format(case_type)))):
                    raise PermissionDenied

        return meeting


class ProtectMeetingDeleteMixin(object):

    '''
    Prevent edit from users that should not be able to delete a contact.
    '''

    def get_object(self):
        meeting = super(ProtectMeetingDeleteMixin, self).get_object()

        user = self.request.user

        case = Case.objects.get(pk=self.kwargs['pk'])
        case_type = case.case_type.code

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['meetings.delete_meeting']) and not user.has_perm('meetings.delete_meeting'):
            if ((not user_group_permissions.issuperset(['meetings.delete_meeting_{}'.format(case_type)]) and not user.has_perm('meetings.delete_meeting_{}'.format(case_type))) or
                    (not user_group_permissions.issuperset(['meetings.delete_meeting_own_{}'.format(case_type)]) and not user.has_perm('meetings.delete_meeting_own_{}'.format(case_type)))):
                    raise PermissionDenied

        return meeting


class ProtectMeetingAttendanceUpdateMixin(object):

    '''
    Prevent edit from users that should not be making edits on contacts
    '''

    def get_object(self):
        meeting = super(ProtectMeetingAttendanceUpdateMixin, self).get_object()

        user = self.request.user

        case = Case.objects.get(pk=self.kwargs['pk'])
        case_type = case.case_type.code

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['meetings.change_meetingattendee']) and not user.has_perm('meetings.change_meetingattendee'):
            if ((not user_group_permissions.issuperset(['meetings.change_meetingattendee_{}'.format(case_type)]) and not user.has_perm('meetings.change_meetingattendee_{}'.format(case_type))) or
                    (not user_group_permissions.issuperset(['meetings.change_meetingattendee_own_{}'.format(case_type)]) and not user.has_perm('meetings.change_meetingattendee_own_{}'.format(case_type)))):
                    raise PermissionDenied

        return meeting

class ProtectAssignOfficialCreateMixin(object):
    """
    Validates user's permission to create an assignofficial
    """

    def dispatch(self, request, *args, **kwargs):
        response = super(ProtectAssignOfficialCreateMixin, self).dispatch(
            request, *args, **kwargs)

        user = request.user

        user_group_permissions = user.get_group_permissions()

        # Both group and user permissions are validated. If user possesses none a PermissionDenied error is raised
        if (not user_group_permissions.issuperset(['meetings.add_assignofficial']) and
                not user.has_perm('meetings.add_assignofficial')):
            raise PermissionDenied

        return response

class ProtectAssignOfficialUpdateMixin(object):
    '''
    Validates user's permission to edit an assignofficial
    '''

    def get_object(self):
        contact = super(ProtectAssignOfficialUpdateMixin, self).get_object()

        user = self.request.user

        user_group_permissions = user.get_group_permissions()

        # Both group and user permissions are validated. If user possesses none a PermissionDenied error is raised
        if (not user_group_permissions.issuperset(['meetings.change_assignofficial']) and
                not user.has_perm('meetings.change_assignofficial')):
            raise PermissionDenied

        return contact

class ProtectAssignOfficialDeleteMixin(object):
    '''
    Validates user's permission to delete an assignofficial
    '''

    def get_object(self):
        assignofficial = super(ProtectAssignOfficialDeleteMixin, self).get_object()

        user = self.request.user

        user_group_permissions = user.get_group_permissions()

        # Both group and user permissions are validated. If user possesses none a PermissionDenied error is raised
        if (not user_group_permissions.issuperset(['meetings.delete_assignofficial']) and
                not user.has_perm('meetigns.delete_assignofficial')):
            raise PermissionDenied

        return assignofficial
