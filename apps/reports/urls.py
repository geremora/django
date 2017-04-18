from django.conf.urls import patterns, url
from apps.reports.views import CaspCasesByUsers
from .views import (CaspGlobalStats, CaspOrdRadResByMonth, CaspActiveCasesByAgency,
                    CaspActiveCasesByCreatedDate, CaspActiveCasesByCategory)

urlpatterns = patterns('',
    url(r'global-stats/', CaspGlobalStats.as_view(), name='global_stats'),
    url(r'ord-rad-res-stats/', CaspOrdRadResByMonth.as_view(), name='ord_ras_res_stats'),
    url(r'active-cases-by-agency/', CaspActiveCasesByAgency.as_view(),
        name='active_cases_by_agency'),
    url(r'active-cases-by-created-date/', CaspActiveCasesByCreatedDate.as_view(),
        name='active_cases_by_created_date'),
    url(r'active-cases-by-case-category/', CaspActiveCasesByCategory.as_view(),
        name='active_cases_by_case_category'),
    url(r'cases-by-users/', CaspCasesByUsers.as_view(), name='case_by_users'),
  )
