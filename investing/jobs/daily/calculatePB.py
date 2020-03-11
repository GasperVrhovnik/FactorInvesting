import pandas as pd
import pandas_datareader as web
from django_extensions.management.jobs import DailyJob
from ...models import Stock, SharesOutstanding, MarketCap, MarketCapInDollars, ExchangeRate, Assets, Liabilities, PriceToBook

def getOutstandingShares(s, year):
    rev = 0
    try:
        rev = SharesOutstanding.objects.filter(stock=s, year=year)[0].sharesOutstanding
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


def getMarketCap(s, year):
    rev = 0
    try:
        rev = MarketCap.objects.filter(stock=s, year=year)[0].marketCap
    except IndexError:
        rev = -99

    return rev


def getMarketCapObj(s, year):
    try:
        rev = MarketCap.objects.filter(stock=s, year=year)[0]
    except:
        rev = MarketCap()

    return rev


def getPB(s, year):

    rev = PriceToBook.objects.filter(stock=s, year=year)[0]

    return rev


def calculatePB(s):
    years = [2014, 2015, 2016, 2017, 2018, 2019]
    for y in years:
        assets = getAssets(s, y)
        liabilities = getLiabilities(s, y)
        mCap = getMarketCap(s, y)

        PB = -99
        if assets != -99 and liabilities != -99 and mCap != -99:
            PB = mCap / (assets - liabilities)

        pb = getPB(s, y)
        pb.stock = s
        pb.year = y
        pb.PB = PB
        pb.save()

        print(assets)
        print(liabilities)
        print(mCap)
        print(PB)
        print("----")


def get_price_data(ticker, start, end):
    price = web.get_data_yahoo(ticker, start, end)
    price = price['Close'] # keep only the Adj Price col
    return price


def getMarketCapDollars(s, year):
    rev = 0
    try:
        rev = MarketCapInDollars.objects.filter(stock=s, year=year)[0].marketCap
    except IndexError:
        rev = -99
    return rev


def calculateMarketCap(s):
    years = [2014, 2015, 2016, 2017, 2018, 2019]
    for y in years:
        try:
            price = get_price_data(s.yahoo_ticker, str(y) + "-01-01", str(y) + "-01-10")
        except:
            continue
        oShares = getOutstandingShares(s, y)
        marketCap = 0

        if oShares != -99:
            try:
                marketCap = price[0] * float(oShares)
            except IndexError:
                marketCap = -99
        else:
            marketCap = -99

        mCap = getMarketCapObj(s, y)
        mCap.stock = s
        mCap.year = y
        mCap.marketCap = marketCap
        mCap.save()

        rate = 1
        date = str(y) + "-01-01"
        currency = s.currency

        if s.currency != "USD":
            rate = ExchangeRate.objects.filter(currency=currency, date=date)[0].rate

        mCapDollars = MarketCapInDollars()
        mCapDollars.stock = s
        mCapDollars.year = y
        mCapDollars.marketCap = marketCap * float(rate)
        mCapDollars.save()

        # print(s.ticker)
        # print(date)
        # print(currency)
        # print(mCap.marketCap)
        # print(mCapDollars.marketCap)


class Job(DailyJob):
    help = "My sample job."

    def execute(self):
        stocks = Stock.objects.all()

        for s in stocks:
            calculateMarketCap(s)
            calculatePB(s)
        PBs = PriceToBook.objects.all()


        x = 0
        y = 0
        z = 0
        q = 0
        w = 0
        for pb in PBs:
            if pb.PB > 0 and pb.PB < 200:
                if pb.year == 2015:
                    x += 1
                if pb.year == 2016:
                    y += 1
                if pb.year == 2017:
                    z += 1
                if pb.year == 2018:
                    q += 1
                if pb.year == 2019:
                    w += 1

        print(x)
        print(y)
        print(z)
        print(q)
        print(w)