from django_extensions.management.jobs import YearlyJob
from investing.models import Stock, Holding, ExchangeRate
import pandas as pd
import numpy as np
import pandas_datareader as web


def filterStocksWithProfitability(stocks, year):
    filtered = []

    for s in stocks:
        prof = s.operatingprofitability_set.filter(year=year)
        if len(prof) == 0:
            continue

        prof = prof[0]

        if prof is None or round(prof.OP) == -99 or round(prof.OP, 4) <= 0:
            continue

        filtered.append(s)

    return filtered

def sumProfitability(stocks, year):
    total = 0
    for s in stocks:
        total += s.operatingprofitability_set.filter(year=year)[0].OP

    return total


def getHoldings(stocks, year):
    totalP = sumProfitability(stocks, year)
    holdings = []

    for s in stocks:
        h = Holding()
        h.stock = s
        h.weight = s.operatingprofitability_set.filter(year=year)[0].OP / totalP
        holdings.append(h)

    return holdings



def generatePortfolio():
    stocks = Stock.objects.all()

    stocks2015 = filterStocksWithProfitability(stocks, 2014)
    stocks2016 = filterStocksWithProfitability(stocks, 2015)
    stocks2017 = filterStocksWithProfitability(stocks, 2016)
    stocks2018 = filterStocksWithProfitability(stocks, 2017)
    stocks2019 = filterStocksWithProfitability(stocks, 2018)

    stocks2015.sort(key=lambda x: x.pricetobook_set.filter(year=2014)[0].OP, reverse=True)
    stocks2016.sort(key=lambda x: x.pricetobook_set.filter(year=2015)[0].OP, reverse=True)
    stocks2017.sort(key=lambda x: x.pricetobook_set.filter(year=2016)[0].OP, reverse=True)
    stocks2018.sort(key=lambda x: x.pricetobook_set.filter(year=2017)[0].OP, reverse=True)
    stocks2019.sort(key=lambda x: x.pricetobook_set.filter(year=2018)[0].OP, reverse=True)

    num2015 = len(stocks2015)
    num2016 = len(stocks2016)
    num2017 = len(stocks2017)
    num2018 = len(stocks2018)
    num2019 = len(stocks2019)

    print(num2015)
    print(num2016)
    print(num2017)
    print(num2018)
    print(num2019)

    firstPentile2015 = stocks2015[:round(num2015 * 0.2)]
    firstPentile2016 = stocks2016[:round(num2016 * 0.2)]
    firstPentile2017 = stocks2017[:round(num2017 * 0.2)]
    firstPentile2018 = stocks2018[:round(num2018 * 0.2)]
    firstPentile2019 = stocks2019[:round(num2019 * 0.2)]


    # firstPentile2015 = stocks2015[500:125 + 125+ 125+ 125+ 125]
    # firstPentile2016 = stocks2016[600:150 + 150+ 150+ 150+ 150]
    # firstPentile2017 = stocks2017[600:150 + 150+ 150+ 150+ 150]
    # firstPentile2018 = stocks2018[600:150 + 150+ 150+ 150+ 150]
    # firstPentile2019 = stocks2019[600:150 + 150+ 150+ 150+ 150]

    print(len(firstPentile2015))
    print(len(firstPentile2016))
    print(len(firstPentile2017))
    print(len(firstPentile2018))
    print(len(firstPentile2019))

    portfolio2015 = getHoldings(firstPentile2015, 2014)
    portfolio2016 = getHoldings(firstPentile2016, 2015)
    portfolio2017 = getHoldings(firstPentile2017, 2016)
    portfolio2018 = getHoldings(firstPentile2018, 2017)
    portfolio2019 = getHoldings(firstPentile2019, 2018)

    dfPortfolio = backtestPortfolio(portfolio2015, portfolio2016, portfolio2017, portfolio2018, portfolio2019)
    return dfPortfolio


def simulateYear(portfolioDf, holdings, start, end, errors):
    dates = pd.DatetimeIndex(start='2016-01-31', freq='M', periods=48)

    for h in holdings:
        print(h)
        try:
            priceData = get_price_data(h.stock.yahoo_ticker, start, end)
        except:
            errors.append(h.stock.yahoo_ticker)
            continue

        monthlyReturns = get_return_data(h.stock, priceData)

        returns = pd.DataFrame(np.zeros(shape=(48, 1)), index=dates, columns=list('S'))

        for idx in monthlyReturns.index:
            # monthly return * weight
            realReturn = monthlyReturns.at[idx, h.stock.yahoo_ticker] * float(h.weight)
            returns.set_value(idx, 'S', realReturn)

        portfolioDf['P'] = portfolioDf['P'] + returns['S']
        print(monthlyReturns)
        # print(portfolioDf)


    return portfolioDf, errors


def backtestPortfolio(holdings2015, holdings2016, holdings2017, holdings2018, holdings2019):
    # init portfolio df
    dates = pd.DatetimeIndex(start='2016-01-31', freq='M', periods=48)
    portfolioDf = pd.DataFrame(np.zeros(shape=(48, 1)), index=dates, columns=list('P'))
    errors = []
    print("Start simulation")
    # portfolioDf, errors = simulateYear(portfolioDf, holdings2015, "2014-12-01", "2015-12-31", errors)
    # print("done")
    portfolioDf, errors = simulateYear(portfolioDf, holdings2016, "2015-12-01", "2016-12-31", errors)
    print("done")
    portfolioDf, errors = simulateYear(portfolioDf, holdings2017, "2016-12-01", "2017-12-31", errors)
    print("done")
    portfolioDf, errors = simulateYear(portfolioDf, holdings2018, "2017-12-01", "2018-12-31", errors)
    print("done")
    portfolioDf, errors = simulateYear(portfolioDf, holdings2019, "2018-12-1", "2019-12-31", errors)
    print("done")

    annulizedReturn = 1
    for idx in portfolioDf.index:
        annulizedReturn *= (1 + portfolioDf.at[idx, 'P'])

    annulizedReturn = (annulizedReturn - 1) * 100
    print(annulizedReturn)
    print(errors)

    return portfolioDf



def get_price_data(ticker, start, end):
    price = web.get_data_yahoo(ticker, start, end)
    price = price['Adj Close'] # keep only the Adj Price col
    return price


def get_return_data(stock, price_data, period="M"):
    # Resample the data to monthly price
    price = price_data.resample(period).last()

    if stock.currency != 'USD':

        exchange = []
        for idx in price.index.date:
            # print(idx)
            # print(stock.currency)
            exchange.append(float(ExchangeRate.objects.filter(currency=stock.currency, date=str(idx))[0].rate))

        exchangeDf = pd.DataFrame(exchange, index=price.index, columns=list('R'))

        price = pd.DataFrame(price)
        price.columns = [stock.ticker]

        price[stock.ticker] = price[stock.ticker] * exchangeDf['R']

    # Calculate the percent change
    ret_data = price.pct_change()[1:]

    # convert from series to DataFrame
    ret_data = pd.DataFrame(ret_data)

    # Rename the Column
    ret_data.columns = [stock.yahoo_ticker]
    return ret_data


class Job(YearlyJob):

    def execute(self):
        generatePortfolio()

