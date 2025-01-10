from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=10)
    bse_code = models.CharField(max_length=10)
    nse_code = models.CharField(max_length=10)
    website = models.URLField()
    logo_url = models.URLField()
    book_value = models.DecimalField(max_digits=10, decimal_places=2)
    face_value = models.DecimalField(max_digits=10, decimal_places=2)
    roce = models.DecimalField(max_digits=5, decimal_places=2)
    roe = models.DecimalField(max_digits=5, decimal_places=2)
    about = models.TextField()

class FinancialData(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    year = models.IntegerField()
    sales = models.DecimalField(max_digits=15, decimal_places=2)
    expenses = models.DecimalField(max_digits=15, decimal_places=2)
    operating_profit = models.DecimalField(max_digits=15, decimal_places=2)
    opm = models.DecimalField(max_digits=5, decimal_places=2)

class ProsAndCons(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    pros = models.TextField()
    cons = models.TextField()