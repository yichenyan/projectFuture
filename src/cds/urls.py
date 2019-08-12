from django.urls import path, include
from .views import CdsReport, CdsReportExtended

urlpatterns = [
    path('cds_report/', CdsReport, name='cds'),
    path('cds_report_extended/', CdsReportExtended, name='cds_extended'),
    
]
