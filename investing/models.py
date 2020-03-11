import datetime

from django.db import models
from django.utils import timezone


class Stock(models.Model):
    name = models.CharField(max_length=200)
    ticker = models.CharField(max_length=10, unique=True)
    yahoo_ticker = models.CharField(max_length=10, default='null')
    currency = models.CharField(max_length=10, default='null')
    market_cap = models.DecimalField(verbose_name='Market Cap', default=0, max_digits=20, decimal_places=4)
    p_b = models.DecimalField(verbose_name='P/B', default=0, max_digits=10, decimal_places=2)
    date_updated = models.DateTimeField('date updated')
    p = models.BooleanField('p', default=False)

    def __str__(self):
        return self.ticker


class Assets(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    assets = models.DecimalField(verbose_name='Assets', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.assets)


class Liabilities(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    liabilities = models.DecimalField(verbose_name='Liabilities', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.liabilities)


class Revenue(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    revenue = models.DecimalField(verbose_name='Revenue', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.revenue)


class InterestExpense(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    interestExpense = models.DecimalField(verbose_name='InterestExpense', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.interestExpense)


class CoGS(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    CoGS = models.DecimalField(verbose_name='CoGS', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.CoGS)


class SGA_Expense(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    SGA_Expense = models.DecimalField(verbose_name='SGA_Expense', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.SGA_Expense)


class SharesOutstanding(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    sharesOutstanding = models.DecimalField(verbose_name='Shares Outstanding', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.sharesOutstanding)


class MarketCap(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    marketCap = models.DecimalField(verbose_name='Shares Outstanding', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.marketCap)


class MarketCapInDollars(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    marketCap = models.DecimalField(verbose_name='Shares Outstanding', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.marketCap)


class ProfitsToAssets(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    profitability = models.DecimalField(verbose_name='Profitability', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.profitability)


class OperatingProfitability(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    OP = models.DecimalField(verbose_name='OP', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.OP)


class PriceToBook(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    PB = models.DecimalField(verbose_name='P/B', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.PB)


class Investment(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    year = models.IntegerField('year', default=0)
    investment = models.DecimalField(verbose_name='Investment', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.year) + ", " + str(self.investment)


class Holding(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    weight = models.DecimalField(verbose_name='Weight', default=0, max_digits=20, decimal_places=3)
    value = models.DecimalField(verbose_name='Value', default=0, max_digits=20, decimal_places=3)
    profitability = models.DecimalField(verbose_name='Profitability', default=0, max_digits=20, decimal_places=3)
    investment = models.DecimalField(verbose_name='Investment', default=0, max_digits=20, decimal_places=3)
    allFactors = models.DecimalField(verbose_name='allFactors', default=0, max_digits=20, decimal_places=3)

    def __str__(self):
        return self.stock.__str__() + ", " + str(self.weight) + ", " + str(self.value) + ", " + str(self.profitability) + ", " + str(self.investment) + ", " + str(self.allFactors)


class ExchangeRate(models.Model):
    currency = models.CharField(verbose_name='Currency', max_length=10)
    date = models.CharField(verbose_name='Date', max_length=10)
    rate = models.DecimalField(verbose_name='Rate', default=0, max_digits=12, decimal_places=6)

    def __str__(self):
        return self.currency + ", " + self.date + ", " + str(self.rate)