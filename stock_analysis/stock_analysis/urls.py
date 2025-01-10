from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from stock_app.views import index, CompanyViewSet, FinancialDataViewSet, ProsAndConsViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'financial-data', FinancialDataViewSet)
router.register(r'pros-and-cons', ProsAndConsViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('api/', include(router.urls)),
]