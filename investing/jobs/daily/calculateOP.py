import datetime

from django_extensions.management.jobs import DailyJob
from ...models import Stock, Revenue, InterestExpense, SGA_Expense, CoGS, Assets, Liabilities, OperatingProfitability


def getRevenue(s, year):
    rev = 0
    try:
        rev = Revenue.objects.filter(stock=s, year=year)[0].revenue
    except IndexError:
        rev = -99

    return rev

def getCOGS(s, year):
    rev = 0
    try:
        rev = CoGS.objects.filter(stock=s, year=year)[0].CoGS
    except IndexError:
        rev = -99

    return rev


def getIntExp(s, year):
    rev = 0
    try:
        rev = InterestExpense.objects.filter(stock=s, year=year)[0].interestExpense
    except IndexError:
        rev = -99

    return rev


def getSGAExp(s, year):
    rev = 0
    try:
        rev = SGA_Expense.objects.filter(stock=s, year=year)[0].SGA_Expense
    except IndexError:
        rev = -99

    return rev


def getLiabilities(s, year):
    rev = 0
    try:
        rev = Liabilities.objects.filter(stock=s, year=year)[0].liabilities
    except IndexError:
        rev = -99

    return rev


def getAssets(s, year):
    rev = 0
    try:
        rev = Assets.objects.filter(stock=s, year=year)[0].assets
    except IndexError:
        rev = -99

    return rev


def calculateOP(s):
    years = [2014, 2015, 2016, 2017, 2018, 2019]
    for y in years:
        revenue = getRevenue(s, y)
        cogs = getCOGS(s, y)
        intExp = getIntExp(s, y)
        sgaExp = getSGAExp(s, y)
        assets = getAssets(s, y - 1)
        liabilities = getLiabilities(s, y - 1)

        if revenue == -99:
            continue
        if assets == -99 or liabilities == -99 or assets - liabilities <= 0:
            continue
        else:
            operatingProfitability = revenue
            if cogs != -99:
                operatingProfitability -= cogs
            if intExp != -99:
                operatingProfitability -= intExp
            if sgaExp != -99:
                operatingProfitability -= sgaExp

            if operatingProfitability == revenue:
                continue

            operatingProfitability = operatingProfitability / (assets - liabilities)

            op = OperatingProfitability()
            op.year = y
            op.stock = s
            op.OP = operatingProfitability
            op.save()


class Job(DailyJob):
    help = "My sample job."

    def execute(self):
        stocks = Stock.objects.all()

        for s in stocks:
            calculateOP(s)

        print(len(OperatingProfitability.objects.filter(year=2014)))
        print(len(OperatingProfitability.objects.filter(year=2015)))
        print(len(OperatingProfitability.objects.filter(year=2016)))
        print(len(OperatingProfitability.objects.filter(year=2017)))
        print(len(OperatingProfitability.objects.filter(year=2018)))
        print(len(OperatingProfitability.objects.filter(year=2019)))