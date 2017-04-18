from django.db import transaction
from django.db.models import get_models, Model
from django.contrib.contenttypes.generic import GenericForeignKey

from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy


def merge_selected(modeladmin, request, queryset):
    """
    Merge Selected Records Admin Actions

    This first displays the selected records to make you
    choose the master record which will be merged into

    Next, it migrates all of the related items of the record
    and assigns it to the master record and then deletes all
    of the other selected records.
    """
    import copy
    model = queryset.model
    model_name = model._meta.object_name
    return_url = "."
    ids = []

    if hasattr(modeladmin, 'merge_list_display'):
        list_display = copy.deepcopy(modeladmin.merge_list_display)
    else:
        list_display = copy.deepcopy(modeladmin.list_display)

    if '_selected_action' in request.POST:  # List of PK's of the selected models
        ids = request.POST.getlist('_selected_action')

    if 'id' in request.GET:
        # This is passed in for specific merge links.
        # This id comes from the linking model (Consumer, IR, Contact, ...)
        id = request.GET.get('id')
        ids.append(id)
        try:
            queryset = queryset | model.objects.filter(pk=id)
        except AssertionError:
            queryset = model.objects.filter(pk__in=ids)
        return_url = model.objects.get(pk=id).get_absolute_url() or "."

    if 'return_url' in request.POST:
        return_url = request.POST['return_url']

    if 'master' in request.POST:
        master = model.objects.get(id=request.POST['master'])
        queryset = model.objects.filter(pk__in=ids)
        for q in queryset.exclude(pk=master.pk):
            __merge_model_objects(master, q)
        messages.success(request,
                         "All " + model_name + " records have been merged into the selected " + model_name + ".")
        return HttpResponseRedirect(return_url)

    # Build the display_table... This is just for the template.
    # ---------------------------------------------------------
    display_table = []

    titles = []
    for ld in list_display:
        if hasattr(ld, 'short_description'):
            titles.append(ld.short_description)
        elif hasattr(ld, 'func_name'):
            titles.append(ld.func_name)
        elif ld == "__str__":
            titles.append(model_name)
        else:
            titles.append(ld)
    display_table.append(titles)

    for q in queryset:
        row = []
        for ld in list_display:
            if callable(ld):
                row.append(mark_safe(ld(q)))
            elif ld == "__str__":
                row.append(q)
            else:
                row.append(mark_safe(getattr(q, ld)))
        display_table.append(row)
        display_table[-1:][0].insert(0, q.pk)
    # -----------------------------------------------------------

    return render_to_response('admin/merge_preview.html',
                              {'queryset': queryset,
                               'model': model,
                               'return_url': return_url,
                               'display_table': display_table, 'ids': ids},
                              context_instance=RequestContext(request))

merge_selected.short_description = ugettext_lazy("Merge selected %(verbose_name_plural)s")


@transaction.atomic()
def __merge_model_objects(primary_object, alias_objects=[], keep_old=False):
    """
    Use this function to merge model objects (i.e. Users, Organizations, Polls,
    etc.) and migrate all of the related fields from the alias objects to the
    primary object.

    Usage:
    from django.contrib.auth.models import User
    primary_user = User.objects.get(email='good_email@example.com')
    duplicate_user = User.objects.get(email='good_email+duplicate@example.com')
    merge_model_objects(primary_user, duplicate_user)
    """
    if not isinstance(alias_objects, list):
        alias_objects = [alias_objects]

    # check that all aliases are the same class as primary one and that
    # they are subclass of model
    primary_class = primary_object.__class__

    if not issubclass(primary_class, Model):
        raise TypeError('Only django.db.models.Model subclasses can be merged')

    for alias_object in alias_objects:
        if not isinstance(alias_object, primary_class):
            raise TypeError('Only models of same class can be merged')

    # Get a list of all GenericForeignKeys in all models
    # TODO: this is a bit of a hack, since the generics framework should provide a similar
    #       method to the ForeignKey field for accessing the generic related fields.
    generic_fields = []
    for model in get_models():
        for field_name, field in filter(lambda x: isinstance(x[1], GenericForeignKey), model.__dict__.iteritems()):
            generic_fields.append(field)

    blank_local_fields = set([field.attname for field in primary_object._meta.local_fields if
                              getattr(primary_object, field.attname) in [None, '']])

    # Loop through all alias objects and migrate their data to the primary object.
    for alias_object in alias_objects:
        # Migrate all foreign key references from alias object to primary object.
        for related_object in alias_object._meta.get_all_related_objects():
            # The variable name on the alias_object model.
            alias_varname = related_object.get_accessor_name()
            # The variable name on the related model.
            obj_varname = related_object.field.name
            related_objects = getattr(alias_object, alias_varname)
            for obj in related_objects.all():
                setattr(obj, obj_varname, primary_object)
                obj.save()

        # Migrate all many to many references from alias object to primary object.
        for related_many_object in alias_object._meta.get_all_related_many_to_many_objects():
            alias_varname = related_many_object.get_accessor_name()
            obj_varname = related_many_object.field.name

            if alias_varname is not None:
                # standard case
                related_many_objects = getattr(alias_object, alias_varname).all()
            else:
                # special case, symmetrical relation, no reverse accessor
                related_many_objects = getattr(alias_object, obj_varname).all()
            for obj in related_many_objects.all():
                getattr(obj, obj_varname).remove(alias_object)
                getattr(obj, obj_varname).add(primary_object)

        # Migrate all generic foreign key references from alias object to primary object.
        for field in generic_fields:
            filter_kwargs = {}
            filter_kwargs[field.fk_field] = alias_object._get_pk_val()
            filter_kwargs[field.ct_field] = field.get_content_type(alias_object)
            for generic_related_object in field.model.objects.filter(**filter_kwargs):
                setattr(generic_related_object, field.name, primary_object)
                generic_related_object.save()

        # Try to fill all missing values in primary object by values of duplicates
        filled_up = set()
        for field_name in blank_local_fields:
            val = getattr(alias_object, field_name)
            if val not in [None, '']:
                setattr(primary_object, field_name, val)
                filled_up.add(field_name)
        blank_local_fields -= filled_up

        if not keep_old:
            alias_object.delete()
    primary_object.save()
    return primary_object