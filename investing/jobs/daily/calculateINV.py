import datetime

from django_extensions.management.jobs import DailyJob
import pandas as pd

from ...models import Stock, Assets, Investment


def getAssets(s, year):
    rev = 0
    try:
        rev = Assets.objects.filter(stock=s, year=year)[0].assets
    except IndexError:
        rev = -99

    return rev


def calculateINV(s):
    years = [2015, 2016, 2017, 2018, 2019]

    for y in years:
        assetst1 = getAssets(s, y-1)
        assetst2 = getAssets(s, y-2)

        investment = -99
        if assetst1 != -99 and assetst2 != -99:
            investment = (assetst1 - assetst2) / assetst2

        INV = Investment()
        INV.stock = s
        INV.year = y
        INV.investment = investment
        INV.save()

        print(s.ticker)
        print(y)
        print(investment)
        print("-----")


class Job(DailyJob):
    help = "My sample job."

    def execute(self):
        # stocks = Stock.objects.all()
        #
        # for s in stocks:
        #     calculateINV(s)

        Inv = Investment.objects.all()
        x = 0
        y = 0
        z = 0
        q = 0
        w = 0
        for inv in Inv:
            if inv.investment != -99:
                if inv.year == 2015:
                    x += 1
                if inv.year == 2016:
                    y += 1
                if inv.year == 2017:
                    z += 1
                if inv.year == 2018:
                    q += 1
                if inv.year == 2019:
                    w += 1

        print(x)
        print(y)
        print(z)
        print(q)
        print(w)
