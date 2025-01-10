from django.shortcuts import render
from rest_framework import viewsets
from .models import Company, FinancialData, ProsAndCons
from .serializers import CompanySerializer, FinancialDataSerializer, ProsAndConsSerializer

def index(request):
    return render(request, 'index.html')

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class FinancialDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FinancialData.objects.all()
    serializer_class = FinancialDataSerializer

class ProsAndConsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProsAndCons.objects.all()
    serializer_class = ProsAndConsSerializer