from django.shortcuts import render
from .models import Cds_Fleet

# Create your views here.

def CdsReport(request):
    qs = Cds_Fleet.objects.all()
    template_name = 'cds/cds_report.html'
    content = {'cds_fleet':qs}
    return(request,template_name,content)

def CdsReportExtended(request):
    pass