from django.urls import path
from . import views

urlpatterns = [
    # Managers
    path('managers/', views.managers_list, name='managers-list'),
    path('managers/<uuid:pk>/', views.manager_detail, name='manager-detail'),

    # Funds
    path('funds/', views.funds_list, name='funds-list'),
    path('funds/<uuid:pk>/', views.fund_detail, name='fund-detail'),

    # Analytics
    path('analytics/dashboard/', views.analytics_dashboard, name='analytics-dashboard'),
    path('analytics/scatter/', views.analytics_scatter, name='analytics-scatter'),
    path('analytics/top-managers/', views.analytics_top_managers, name='analytics-top'),
    path('analytics/quartile-dist/', views.analytics_quartile_dist, name='analytics-quartile'),

    # Workflows
    path('workflows/', views.workflows_list, name='workflows-list'),
    path('workflows/<uuid:pk>/', views.workflow_detail, name='workflow-detail'),
    path('workflows/<uuid:pk>/comments/', views.workflow_add_comment, name='workflow-comment'),

    # Import
    path('import/excel/', views.import_excel, name='import-excel'),
]
