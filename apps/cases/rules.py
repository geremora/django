class CaspRules(object):

    # Actions that are always valid
    ANY_TIME_RULES = [
        {
            'action': 'upload_docs',
            'side_effects': [],
            'allowed_groups': ['interventor', 'secretaria']
        },
        {
            'action': 'change_lawyers',
            'side_effects': [],
            'allowed_groups': ['secreatria']
        },
        {
            'action': 'log_calls',
            'side_effects': [],
            'allowed_groups': ['interventor', 'secreatria']
        },
        {
            'action': 'close_case',
            'side_effects': [],
            'allowed_groups': ['interventor', 'secreatria']
        }
    ]

    # Rules for XX - Unasigned cases
    XX = {
        'new': []
    }

    # Rules for AO - Procedimiento de Arbitraje
    AO = {
        'new': [
            {
                'action': 'add_partes',
                'side_effects': [],
                'allowed_groups': ['interventor', 'secreatria']
            },
            {
                'action': 'add_materia',
                'side_effects': [],
                'allowed_groups': ['dir_secretaria', 'sub_dir_secretaria']
            },
            {
                'action': 'assign_case_type_number',
                'side_effects': ['move_to_ao-created'],
                'allowed_groups': ['dir_secretaria', 'sub_dir_secretaria']
            }
        ],

        'ao-created': [
            {
                'action': 'es_mediable_true',
                'side_effects': ['move_to_ao-i-assigned'],
                'allowed_groups': ['dir_metodos_alternos']
            },
            {
                'action': 'es_mediable_false',
                'side_effects': ['move_to_ao-i-assigned-vista'],
                'allowed_groups': ['dir_metodos_alternos']
            },
            {
                'action': 'assign_interventor',
                'side_effects': [],
                'allowed_groups': ['dir_metodos_alternos']
            },
            {
                'action': 'asignar_fecha_visa',
                'side_effects': [],
                'allowed_groups': ['dir_metodos_alternos']
            },
            {
                'action': 'asignar_lugar_visa',
                'side_effects': [],
                'allowed_groups': ['dir_metodos_alternos']
            }
        ],

        'ao-i-assigned': [
            {
                'action': 'notificar_carta',
                'side_effects': ['move_to_ao-sessions'],
                'allowed_groups': ['secretaria']
            },
        ],

        'ao-i-sessions': [
            {
                'action': 'se_celebro_vista_true',
                'side_effects': [],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'se_celebro_vista_false',
                'side_effects': [],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'se_prenseto_vista_false_justificada',
                'side_effects': [],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'se_presento_vista_false_no_justificada',
                'side_effects': [],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'new_date_for_vista',
                'side_effects': [],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'hay_acuerdo',
                'side_effects': ['move_to_ao-i-informe'],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'no_hay_acuerdo',
                'side_effects': ['move_to_ao-d-new-i'],
                'allowed_groups': ['interventor_neutral']
            }
        ],

        'ao-i-informe': [
            {
                'action': 'emitir_upload_informe',
                'side_effects': [],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'hay_acuerdo_parcial',
                'side_effects': ['move_to_ao-d-new-i'],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'hay_acuerdo_total',
                'side_effects': ['move_to_closed'],
                'allowed_groups': ['interventor_neutral']
            }
        ],

        'ao-d-new-i': [
            {
                'action': 'assign_new_interventor',
                'side_effects': [],
                'allowed_groups': ['dir_metodos_alternos']
            },
            {
                'action': 'new_date_for_vista',
                'side_effects': ['move_to_ao-i-assigned-vista'],
                'allowed_groups': ['dir_metodos_alternos']
            }
        ],

        'ao-i-assigned-vista': [
            {
                'action': 'notificar_carta',
                'side_effects': ['move_to_ao-laudo'],
                'allowed_groups': ['secreatria']
            }
        ],

        'ao-laudo': [
            {
                'action': 'se_celebro_vista_true',
                'side_effects': [],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'se_celebro_vista_false',
                'side_effects': [],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'se_prenseto_vista_false_justificada',
                'side_effects': [],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'se_presento_vista_false_no_justificada',
                'side_effects': [],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'new_date_for_vista',
                'side_effects': [],
                'allowed_groups': ['interventor_neutral']
            },
            {
                'action': 'emitir_laudo',
                'side_effects': ['move_to_closed'],
                'allowed_groups': ['interventor_neutral']
            }
        ],

        'closed': [
            {
                'action': 'notificar_carta',
                'side_effects': [],
                'allowed_groups': ['secreatria']
            }
        ]
    }

    def __init__(self, *args, **kwargs):
        '''
        Must pass an instance of Case to initialize
        '''
        self.case = kwargs.get('case', None)

    @classmethod
    def rules_for_type(self, case_type):
        '''
        Returns a list of rules for a CaseType
        '''
        return getattr(self, case_type.code)

    @classmethod
    def rules_for_state_in_type(self, state, case_type):
        '''
        Return a list of rules for a case in state of a case_type
        '''
        type_rules = self.rules_for_type(case_type)
        return type_rules[state]

    def active_rules(self):
        '''
        Returns a list of rules for a case in self.case.state
        of a self.case.case_type
        '''
        return self.rules_for_state_in_type(
            self.case.state, self.case.case_type)

    def valid_actions(self):
        '''
        Returns a list of all available actions based on
        the current self.case.case_type and self.case.state
        '''
        return [r['action'] for r in self.active_rules()]

    def case_event_types(self):
        '''
        Returns a queryset of all available actions for the
        current case taking into account current state and case type
        '''
        from .models import CaseEventType
        return CaseEventType.objects.filter(name__in=self.valid_actions())

    @classmethod
    def any_time_event_types(self):
        from .models import CaseEventType
        return CaseEventType.objects.filter(
            name__in=[r['action'] for r in self.ANY_TIME_RULES])
