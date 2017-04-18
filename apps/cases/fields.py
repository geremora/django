from django.utils.functional import curry
#from django_fsm.db.fields import FSMField
from django_fsm import FSMField

# South support
# see http://south.aeracode.org/docs/tutorial/part4.html#simple-inheritance
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], [r"^apps\.cases\.fields\.MyFSMField"])


# def get_available_FIELD_transitions(instance, field):
#     curr_state = getattr(instance, field.name)
#     result = []
#     for transition in field.transitions:
#         meta = transition._django_fsm
#         if meta.has_transition(instance):
#             try:
#                 _conditions = []
#                 for func in meta.conditions[curr_state]:
#                     _conditions.append({
#                                        'func': func,
#                                        'doc_text': func.__doc__.strip(),
#                                        'condition_met': func(instance)})

#                 result.append({
#                     'target_name': meta.transitions[curr_state],
#                     'doc_text': transition.__doc__.strip(),
#                     'func': transition,
#                     'conditions_met': meta.conditions_met(instance),
#                     'conditions': _conditions
#                 })
#             except KeyError:
#                 _conditions = []
#                 for func in meta.conditions['*']:
#                     _conditions.append({
#                                        'func': func,
#                                        'doc_text': func.__doc__.strip(),
#                                        'condition_met': func(instance)})

#                 result.append({
#                     'target_name': meta.transitions['*'],
#                     'doc_text': transition.__doc__.strip(),
#                     'func': transition,
#                     'conditions_met': meta.conditions_met(instance),
#                     'conditions': _conditions
#                 })

#     return result


class MyFSMField(FSMField):
     def contribute_to_class(self, cls, name):
         super(MyFSMField, self).contribute_to_class(cls, name)
    #     if self.transitions:
    #         setattr(cls, 'get_available_%s_transitions' % self.name,
    #                 curry(get_available_FIELD_transitions, field=self))
