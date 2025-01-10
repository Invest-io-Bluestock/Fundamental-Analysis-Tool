from rest_framework import serializers
from .models import Company, FinancialData, ProsAndCons

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class FinancialDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialData
        fields = '__all__'

class ProsAndConsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProsAndCons
        fields = '__all__'