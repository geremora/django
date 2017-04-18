from django.core.exceptions import PermissionDenied

# from django.core.urlresolvers import resolve



class ProtectCaseCreateMixin(object):

    create_permissions = ['cases.add_case']

    def dispatch(self, request, *args, **kwrags):
        response = super(ProtectCaseCreateMixin, self).dispatch(
            request, *args, **kwrags)

        user = request.user

        # user_groups = [slugify(ug.name) for ug in user.groups.all()]

        user_group_permissions = user.get_group_permissions()

        # if not 's-data-entry-2' in user_groups and not 's-supervisor' in
        # user_groups and not 'superuser' in user_groups:
        if not user_group_permissions.issuperset(self.create_permissions):
            if not user.has_perm('cases.add_case'):
                raise PermissionDenied
        return response


class ProtectCaseTypeMixin(object):

    '''
    Checks if case has a type other than XX and raises exception if it does.
    We don't allow to modify case_type after one has been applied.
    '''

    def get_object(self):
        case = super(ProtectCaseTypeMixin, self).get_object()

        if case.did_confirm_case_type:
            raise PermissionDenied

        return case


class ProtectChangeAssignedUserMixin(object):

    def get_object(self):
        case = super(
            ProtectChangeAssignedUserMixin, self).get_object()

        user = self.request.user

        if user.is_superuser:
            return case

        case_type = case.case_type

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['cases.can_change_assigned_user_case']):
            if not user.has_perm('cases.can_change_assigned_user_case'):
                if (case_type == 'XX' and
                        not user_group_permissions.issuperset(['cases.can_change_assigned_user_case_XX'])):
                    if not user.has_perm('cases.can_change_assigned_user_case_XX'):
                        raise PermissionDenied
                elif (case_type == 'AO' and
                        not user_group_permissions.issuperset(['cases.can_change_assigned_user_case_AO'])):
                    if not user.has_perm('cases.can_change_assigned_user_case_AO'):
                        raise PermissionDenied
                elif (case_type == 'AQ' and
                        not user_group_permissions.issuperset(['cases.can_change_assigned_user_case_AQ'])):
                    if not user.has_perm('cases.can_change_assigned_user_case_AQ'):
                        raise PermissionDenied
                elif (case_type == 'SA' and
                        not user_group_permissions.issuperset(['cases.can_change_assigned_user_case_SA'])):
                    if not user.has_perm('cases.can_change_assigned_user_case_SA'):
                        raise PermissionDenied
                elif (case_type == 'SM' and
                        not user_group_permissions.issuperset(['cases.can_change_assigned_user_case_SM'])):
                    if not user.has_perm('cases.can_change_assigned_user_case_SM'):
                        raise PermissionDenied

        return case


class ProtectChangeDescriptionCaseMixin(object):

    '''
    Checks if user has permissions to change the case description.
    '''

    def get_object(self):
        case = super(
            ProtectChangeDescriptionCaseMixin, self).get_object()
        user = self.request.user

        if user.is_superuser:
            return case

        case_type = case.case_type

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['cases.can_change_description_case']):
            if user.has_perm('cases.can_change_description_case'):
                if (case_type == 'XX' and
                        not user_group_permissions.issuperset(['cases.can_change_description_case_XX'])):
                    if not user.has_perm('cases.can_change_description_case_XX'):
                        raise PermissionDenied
                elif (case_type == 'AO' and
                        not user_group_permissions.issuperset(['cases.can_change_description_case_AO'])):
                    if not user.has_perm('cases.can_change_description_case_AO'):
                        raise PermissionDenied
                elif (case_type == 'AQ' and
                        not user_group_permissions.issuperset(['cases.can_change_description_case_AQ'])):
                    if not user.has_perm('cases.can_change_description_case_AQ'):
                        raise PermissionDenied
                elif (case_type == 'SA' and
                        not user_group_permissions.issuperset(['cases.can_change_description_case_SA'])):
                    if not user.has_perm('cases.can_change_description_case_SA'):
                        raise PermissionDenied
                elif (case_type == 'SM' and
                        not user_group_permissions.issuperset(['cases.can_change_description_case_SM'])):
                    if not user.has_perm('cases.can_change_description_case_SM'):
                        raise PermissionDenied
                else:
                    raise PermissionDenied

        return case

class ProtectReOpenCaseMixin(object):

    '''
    Checks if user has permissions to change the date closed.
    '''

    def get_object(self):
        case = super(
            ProtectReOpenCaseMixin, self).get_object()
        user = self.request.user

        if user.is_superuser:
            return case

        case_type = case.case_type

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['cases.re_open_case']):
            if user.has_perm('cases.can_re_open_case'):
                if (case_type == 'XX' and
                        not user_group_permissions.issuperset(['cases.can_re_open_case_XX'])):
                    if not user.has_perm('cases.can_re_open_case_XX'):
                        raise PermissionDenied
                elif (case_type == 'AO' and
                        not user_group_permissions.issuperset(['cases.can_re_open_case_AO'])):
                    if not user.has_perm('cases.can_re_open_case_AO'):
                        raise PermissionDenied
                elif (case_type == 'AQ' and
                        not user_group_permissions.issuperset(['cases.can_re_open_case_AQ'])):
                    if not user.has_perm('cases.can_re_open_case_AQ'):
                        raise PermissionDenied
                elif (case_type == 'SA' and
                        not user_group_permissions.issuperset(['cases.can_re_open_case_SA'])):
                    if not user.has_perm('cases.can_re_open_case_SA'):
                        raise PermissionDenied
                elif (case_type == 'SM' and
                        not user_group_permissions.issuperset(['cases.can_re_open_case_SM'])):
                    if not user.has_perm('cases.can_re_open_case_SM'):
                        raise PermissionDenied
                else:
                    raise PermissionDenied

        return case

class ProtectChangeDateClosedCaseMixin(object):

    '''
    Checks if user has permissions to change the date closed.
    '''

    def get_object(self):
        case = super(
            ProtectChangeDateClosedCaseMixin, self).get_object()
        user = self.request.user

        if user.is_superuser:
            return case

        case_type = case.case_type

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['cases.change_date_closed_case']):
            if user.has_perm('cases.change_date_closed_case'):
                if (case_type == 'XX' and
                        not user_group_permissions.issuperset(['cases.change_date_closed_case_XX'])):
                    if not user.has_perm('cases.change_date_closed_case_XX'):
                        raise PermissionDenied
                elif (case_type == 'AO' and
                        not user_group_permissions.issuperset(['cases.change_date_closed_case_AO'])):
                    if not user.has_perm('cases.change_date_closed_case_AO'):
                        raise PermissionDenied
                elif (case_type == 'AQ' and
                        not user_group_permissions.issuperset(['cases.change_date_closed_case_AQ'])):
                    if not user.has_perm('cases.change_date_closed_case_AQ'):
                        raise PermissionDenied
                elif (case_type == 'SA' and
                        not user_group_permissions.issuperset(['cases.change_date_closed_case_SA'])):
                    if not user.has_perm('cases.change_date_closed_case_SA'):
                        raise PermissionDenied
                elif (case_type == 'SM' and
                        not user_group_permissions.issuperset(['cases.change_date_closed_SM'])):
                    if not user.has_perm('cases.change_date_closed_case_SM'):
                        raise PermissionDenied
                else:
                    raise PermissionDenied

        return case

class ProtectMergeCaseMixin(object):

    '''
    Protects from unauthorized case merges.
    '''

    def get_object(self):
        case = super(ProtectMergeCaseMixin, self).get_object()
        user = self.request.user

        case_type = case.case_type

        # Get all permissions from users groups
        user_group_permissions = user.get_group_permissions()

        # First level of validation is against group permissions
        if not user_group_permissions.issuperset(['cases.can_merge_case']) and not user.has_perm('cases.can_merge_case'):
                # Third level of validation depends on the case type. We start validation from
                # groups down to the user again
                if case_type == 'XX':
                    if ((not user_group_permissions.issuperset(['cases.can_merge_case_XX']) and not user.has_perm('cases.can_merge_case_XX')) or
                            (case.assigned_user == user and (not user_group_permissions.issuperset(['cases.can_merge_case_own_XX']) and not user.has_perm('cases.can_merge_case_own_XX')))):
                        raise PermissionDenied
                elif case_type == 'AO':
                    if ((not user_group_permissions.issuperset(['cases.can_merge_case_AO']) and not user.has_perm('cases.can_merge_case_AO')) or
                            (case.assigned_user == user and (not user_group_permissions.issuperset(['cases.can_merge_case_own_AO']) and not user.has_perm('cases.can_merge_case_own_AO')))):
                        raise PermissionDenied
                elif case_type == 'AQ':
                    if ((not user_group_permissions.issuperset(['cases.can_merge_case_AQ']) and not user.has_perm('cases.can_merge_case_AQ')) or
                            (case.assigned_user == user and (not user_group_permissions.issuperset(['cases.can_merge_case_own_AQ']) and not user.has_perm('cases.can_merge_case_own_AQ')))):
                        raise PermissionDenied
                elif case_type == 'SA':
                    if ((not user_group_permissions.issuperset(['cases.can_merge_case_SA']) and not user.has_perm('cases.can_merge_case_SA')) or
                            (case.assigned_user == user and (not user_group_permissions.issuperset(['cases.can_merge_case_own_SA']) and not user.has_perm('cases.can_merge_case_own_SA')))):
                        raise PermissionDenied
                elif case_type == 'SM':
                    if ((not user_group_permissions.issuperset(['cases.can_merge_case_SM']) and not user.has_perm('cases.can_merge_case_SM')) or
                            (case.assigned_user == user and (not user_group_permissions.issuperset(['cases.can_merge_case_own_SM']) and not user.has_perm('cases.can_merge_case_own_SM')))):
                        raise PermissionDenied

        return case


class ProtectUnmergeCaseMixin(object):

    '''
    Protects from unauthorized case merges.
    '''

    def get_object(self):
        case = super(ProtectUnmergeCaseMixin, self).get_object()
        user = self.request.user

        if user.is_superuser:
            return case

        case_type = case.case_type

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['cases.can_unmerge_case']):
            if not user.has_perm('can_unmerge_case'):
                if case_type == 'XX' and not user_group_permissions.issuperset(['cases.can_unmerge_case_XX']):
                    if not user.has_perm('cases.can_unmerge_case_XX'):
                        raise PermissionDenied
                elif case_type == 'AO' and not user_group_permissions.issuperset(['cases.can_unmerge_case_AO']):
                    if not user.has_perm('cases.can_unmerge_case_AO'):
                        raise PermissionDenied
                elif case_type == 'AQ' and not user_group_permissions.issuperset(['cases.can_unmerge_case_AQ']):
                    if not user.has_perm('cases.can_merge_case_AQ'):
                        raise PermissionDenied
                elif case_type == 'SA' and not user_group_permissions.issuperset(['cases.can_unmerge_case_SA']):
                    if not user.has_perm('cases.can_merge_case_SA'):
                        raise PermissionDenied
                elif case_type == 'SM' and not user_group_permissions.issuperset(['cases.can_unmerge_case_SM']):
                    if not user.has_perm('cases.can_merge_case_SM'):
                        raise PermissionDenied
                else:
                    raise PermissionDenied

        return case


class ProtectClosedCaseMixin(object):

    '''
    Prevent edit after clase is closed
    '''

    def get_object(self):
        case = super(ProtectClosedCaseMixin, self).get_object()

        if case.state == 'closed':
            raise PermissionDenied

        return case


class ProtectChangeCaseMixin(object):

    '''
    Prevent edit from users that should not be making edits on cases
    '''

    def get_object(self):
        case = super(ProtectChangeCaseMixin, self).get_object()

        case_type = case.case_type

        user = self.request.user

        if user.is_superuser:
            return case

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['cases.change_case']):
            if not user.has_perm('cases.change_case'):
                if case_type == 'XX' and not user_group_permissions.issuperset(['cases.can_change_case_XX']):
                    if not user.has_perm('cases.can_change_case_XX'):
                        raise PermissionDenied
                elif case_type == 'AO' and not user_group_permissions.issuperset(['cases.can_change_case_AO']):
                    if not user.has_perm('cases.can_change_case_AO'):
                        raise PermissionDenied
                elif case_type == 'AQ' and not user_group_permissions.issuperset(['cases.can_change_case_AQ']):
                    if not user.has_perm('cases.can_change_case_AQ'):
                        raise PermissionDenied
                elif case_type == 'SA' and not user_group_permissions.issuperset(['cases.can_change_case_SA']):
                    if not user.has_perm('cases.can_change_case_SA'):
                        raise PermissionDenied
                elif case_type == 'SM' and not user_group_permissions.issuperset(['cases.can_change_case_SM']):
                    if not user.has_perm('cases.can_change_case_SM'):
                        raise PermissionDenied

        return case


class ProtectCaseUpdateContactsMixin(object):

    '''
    Prevents unauthorized contact updates on cases
    '''

    def get_object(self):
        case = super(ProtectCaseUpdateContactsMixin, self).get_object()

        case_type = case.case_type

        user = self.request.user

        if user.is_superuser:
            return case

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['cases.change_contact']):
            if not user.has_perm('cases.change_contact'):
                if case_type == 'XX' and not user_group_permissions.issuperset(['cases.can_change_contact_XX']):
                    if not user.has_perm('cases.can_change_contact_XX'):
                        raise PermissionDenied
                elif case_type == 'AO' and not user_group_permissions.issuperset(['cases.can_change_contact_AO']):
                    if not user.has_perm('cases.can_change_contact_AO'):
                        raise PermissionDenied
                elif case_type == 'AO' and not user_group_permissions.issuperset(['cases.can_change_contact_AQ']):
                    if not user.has_perm('cases.can_change_contact_AQ'):
                        raise PermissionDenied
                elif case_type == 'SA' and not user_group_permissions.issuperset(['cases.can_change_contact_SA']):
                    if not user.has_perm('cases.can_change_contact_SA'):
                        raise PermissionDenied
                elif case_type == 'SM' and not user_group_permissions.issuperset(['cases.can_change_contact_SM']):
                    if not user.has_perm('cases.can_change_contact_SM'):
                        raise PermissionDenied

        return case


class ProtectChangeCaseCategoryCaseMixin(object):

    '''
    Prevents unauthorized case category updates on cases
    '''

    def get_object(self):
        case = super(ProtectChangeCaseCategoryCaseMixin, self).get_object()

        case_type = case.case_type

        user = self.request.user

        if user.is_superuser:
            return case

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['cases.change_casecategory']):
            if not user.has_perm('cases.change_casecategory'):
                if case_type == 'XX' and not user_group_permissions.issuperset(['cases.change_casecategory_XX']):
                    if not user.has_perm('cases.change_casecategory_XX'):
                        raise PermissionDenied
                elif case_type == 'AO' and not user_group_permissions.issuperset(['cases.change_casecategory_AO']):
                    if not user.has_perm('cases.change_casecategory_AO'):
                        raise PermissionDenied
                elif case_type == 'AO' and not user_group_permissions.issuperset(['cases.change_casecategory_AQ']):
                    if not user.has_perm('cases.change_casecategory_AQ'):
                        raise PermissionDenied
                elif case_type == 'SA' and not user_group_permissions.issuperset(['cases.change_casecategory_SA']):
                    if not user.has_perm('cases.change_casecategory_SA'):
                        raise PermissionDenied
                elif case_type == 'SM' and not user_group_permissions.issuperset(['cases.change_casecategory_SM']):
                    if not user.has_perm('cases.change_casecategory_SM'):
                        raise PermissionDenied

        return case


class ProtectCaseUpdateRecordHolderMixin(object):
    def get_object(self):
        case = super(ProtectCaseUpdateRecordHolderMixin, self).get_object()

        case_type = case.case_type

        user = self.request.user

        if user.is_superuser:
            return case

        user_group_permissions = user.get_group_permissions()

        if not user_group_permissions.issuperset(['cases.change_record_holder']) and not user.has_perm('cases.change_record_holder'):
            if case_type == 'XX':
                if not ((user_group_permissions.issuperset(['cases.can_change_record_holder_case_XX']) or user.has_perm('cases.can_change_record_holder_case_XX')) or
                        (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_change_record_holder_case_own_XX']) or user.has_perm('cases.can_change_record_holder_case_own_XX')))):
                    raise PermissionDenied
            elif case_type == 'AO':
                if not ((user_group_permissions.issuperset(['cases.can_change_record_holder_case_AO']) or user.has_perm('cases.can_change_record_holder_case_AO')) or
                        (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_change_record_holder_case_own_AO']) or user.has_perm('cases.can_change_record_holder_case_own_AO')))):
                    raise PermissionDenied
            elif case_type == 'AQ':
                if not ((user_group_permissions.issuperset(['cases.can_change_record_holder_case_AQ']) or user.has_perm('cases.can_change_record_holder_case_AQ')) or
                        (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_change_record_holder_case_own_AQ']) or user.has_perm('cases.can_change_record_holder_case_own_AQ')))):
                    raise PermissionDenied
            elif case_type == 'SA':
                if not ((user_group_permissions.issuperset(['cases.can_change_record_holder_case_SA']) or user.has_perm('cases.can_change_record_holder_case_SA')) or
                        (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_change_record_holder_case_own_SA']) or user.has_perm('cases.can_change_record_holder_case_own_SA')))):
                    raise PermissionDenied
            elif case_type == 'SM':
                if not ((user_group_permissions.issuperset(['cases.can_change_record_holder_case_SM']) or user.has_perm('cases.can_change_record_holder_case_SM')) or
                        (user == case.assigned_user and (user_group_permissions.issuperset(['cases.can_change_record_holder_case_own_SM']) or user.has_perm('cases.can_change_record_holder_case_own_SM')))):
                    raise PermissionDenied
        return case
