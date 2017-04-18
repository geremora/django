import os

TEMPLATE = 'can_{}_{}_{}'

class CaseTypesCached():
    case_types = None

    @staticmethod
    def _get_all_case_types():
        from django.db import connection
        cursor = connection.cursor()
        try:
            cursor.execute('SELECT * FROM cases_casetype')
            result = [r[2] for r in cursor.fetchall()]
        except:
            result = []

        return result

    @staticmethod
    def get_all_case_types():
        if not CaseTypesCached.case_types:
            CaseTypesCached.case_types = CaseTypesCached._get_all_case_types()
        return CaseTypesCached.case_types


def get_custom_permissions(name, perms=['add', 'change', 'delete']):
    if os.getenv('syncdb') == 'True':
        return []
    else:
        case_types = CaseTypesCached.get_all_case_types()

    templates = []

    for perm in perms:
        templates.append(TEMPLATE.format(perm, name, '{}'))
        templates.append(TEMPLATE.format(perm, name, 'own_{}'))

    perm_strings = []

    for ct in case_types:
        for template in templates:
            perm_strings.append((template.format(ct),
                                _readable_name(ct, template)))

    return perm_strings


def _readable_name(ct, template):
    _readable = template.format(ct).split('_')
    return '{} {}'.format(' '.join(_readable[:-1]).title(), _readable[-1])
