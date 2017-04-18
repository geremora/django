from django.conf.urls import patterns, url

from .views import get_s3_signature, case_ajax_search, case_feed_json, case_categories_ajax_by_case_type
from .views import (CaseListView, CaseDetailView,
                    CaseCreateWizardView, CaseTransitionView,
                    CaseUpdateTypeView, CaseUpdateAssignedUserView,
                    CaseUpdateContactView, CaseUpdateDescriptionView,
                    CaseUpdateRecordView, CasePrintView, CaseMergeView,
                    CaseUnmergeView, CaseMergedListView, CaseUpdateCaseCategoryView, 
                    CaseUpdateDateClosedView, CaseReOpenView,  CaseContactsListView,
                    CaseCreateContactsView, CaseDesactiveView, CaseActiveView,
                    CaseSendCaseMediationView, CaseRemoveCaseMediationView)


urlpatterns = patterns(
    '',  # Empty string as prefix

    url(r'^$', CaseListView.as_view(), name='case_list'),

    url(r'^ajax/s3signature/$', get_s3_signature, name='s3_signature'),

    url(r'^ajax/$', case_ajax_search, name='case_ajax_search'),

    url(r'^ajax/case_category/$', case_categories_ajax_by_case_type, name='case_categories_ajax_by_case_type'),

    url(r'^feed/$', case_feed_json, name='case_feed_json'),

    url(r'^create/$', CaseCreateWizardView.as_view(), name='case_create'),

    url(r'^(?P<pk>\d+)/$', CaseDetailView.as_view(), name='case_detail'),

    url(r'^(?P<pk>\d+)/print/$', CasePrintView.as_view(), name='case_print'),

   # url(r'^(?P<pk>\d+)/reopen/$', 'apps.cases.views.re_open_case', name='case_re_open'),

    url(r'^(?P<pk>\d+)/reopen/$', CaseReOpenView.as_view(), name='case_re_open'),


    url(r'^(?P<pk>\d+)/merged/$', CaseMergedListView.as_view(), name='case_merged_list'),



    url(r'^(?P<pk>\d+)/transition/(?P<state>[-\w]+)/$',
        CaseTransitionView.as_view(), name='case_detail_transition'),

    url(r'^(?P<pk>\d+)/update/type/$',
        CaseUpdateTypeView.as_view(), name='case_update_type'),

    url(r'^(?P<pk>\d+)/update/user/$', CaseUpdateAssignedUserView.as_view(),
        name='case_update_assigned_user'),

    url(r'^(?P<pk>\d+)/update/contact/(?P<pk2>[-\w]+)/$',
        CaseUpdateContactView.as_view(), name='case_contact_update'),

    url(r'^(?P<pk>\d+)/delete/contact/(?P<pk2>[-\w]+)/$',
        view='apps.cases.views.delete_case_contact', name='delete_case_contact'),

    url(r'^(?P<pk>\d+)/contacts/$',
        CaseContactsListView.as_view(), name='case_contacts_list'),

    url(r'^(?P<pk>\d+)/contacts/create/$',
        CaseCreateContactsView.as_view(),  name='case_contact_create'),

    url(r'^(?P<pk>\d+)/update/description/$',
        CaseUpdateDescriptionView.as_view(), name='case_update_description'),

    url(r'^(?P<pk>\d+)/update/casecategory/$',
        CaseUpdateCaseCategoryView.as_view(), name='change_casecategory'),

    url(r'^(?P<pk>\d+)/update/casemediation/send/$',
        CaseSendCaseMediationView.as_view(), name='send_case_mediation'),

    url(r'^(?P<pk>\d+)/update/casemediation/remove/$',
        CaseRemoveCaseMediationView.as_view(), name='remove_case_mediation'),

    url(r'^(?P<pk>\d+)/update/dateclosed/$',
        CaseUpdateDateClosedView.as_view(), name='change_date_closed'),

    url(r'^(?P<pk>\d+)/update/record/$',
        CaseUpdateRecordView.as_view(), name='case_update_record_view'),

    url(r'^(?P<pk>\d+)/update/merge/$',
        CaseMergeView.as_view(), name='case_merge_view'),

    # url(r'^(?P<pk>\d+)/update/unmerge/$',
    #     CaseUnmergeView.as_view(), name='case_unmerge_view'),

    url(r'^(?P<pk>\d+)/update/unmerge/(?P<pk2>[-\w]+)/$',
        CaseUnmergeView.as_view(), name='case_unmerge_view'),


    url(r'^(?P<pk>\d+)/update/desactive/(?P<pk2>[-\w]+)/$',
        CaseDesactiveView.as_view(), name='case_desactive_view'),

    url(r'^(?P<pk>\d+)/update/active/(?P<pk2>[-\w]+)/$',
        CaseActiveView.as_view(), name='case_active_view'),


    url(r'^unmerge/$', CaseUnmergeView.as_view(), name='case_unmerge_list_view'),

    url(r'^add/(?P<model_name>\w+)/?/$',
        'apps.django_popup_add.views.add_new_model', name='add_popup_window'),
)
