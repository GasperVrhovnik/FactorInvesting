import decimal
from time import sleep

from django_extensions.management.jobs import DailyJob
import pandas as pd
import numpy as np
import pandas_datareader as web
from ...models import Stock, MarketCapInDollars, PriceToBook, OperatingProfitability, Investment, Holding, ExchangeRate

def getMarketCap(s, year):
    rev = 0
    try:
        rev = MarketCapInDollars.objects.filter(stock=s, year=year)[0].marketCap
    except IndexError:
        rev = -99
    return rev


def getPB(s, year):
    rev = 0
    try:
        rev = PriceToBook.objects.filter(stock=s, year=year)[0].PB
    except IndexError:
        rev = -99
    return rev


def getOperatingProfitability(s, year):
    rev = 0
    try:
        rev = OperatingProfitability.objects.filter(stock=s, year=year)[0].OP
    except IndexError:
        rev = -99
    return rev


def getInvestment(s, year):
    rev = 0
    try:
        rev = Investment.objects.filter(stock=s, year=year)[0].investment
    except IndexError:
        rev = -99
    return rev


def filterStocks(stocks, year):
    filtered = []
    x = 0
    y = 0
    z = 0
    for s in stocks:
        marketCap = getMarketCap(s, year)
        PB = getPB(s, year)
        OP = getOperatingProfitability(s, year)
        INV = getInvestment(s, year)

        if marketCap == -99:
            continue

        i = 0

        if PB > 0.001:
            i += 1
            x += 1

        if OP > 0:
            i += 1
            y += 1

        if INV > 0:
            i += 1
            z += 1

        if i >= 2:
            filtered.append(s)

    print(year)
    print("PB: ", x)
    print("OP: ", y)
    print("INV: ", z)
    return filtered


def calculateFactorExposure(s, stocks, year):
    h = Holding()
    h.stock = s

    # value
    stocksPB = sorted(stocks, key=lambda x: getPB(x, year), reverse=True)
    index = stocksPB.index(s)
    if getPB(s, year) == -99:
        index = 0

    h.value = index / len(stocksPB)

    # pbS = getPB(s, year)
    # if pbS > 0:
    #     sumValue = 0
    #     for x in stocks:
    #         pb = getPB(x, year)
    #         if pb > 0:
    #             sumValue += pb ** -1
    #
    #     h.value = pbS ** -1 / sumValue
    # else:
    #     h.value = 0

    # profitability
    stocksOP = sorted(stocks, key=lambda x: getOperatingProfitability(x, year), reverse=False)
    index = stocksOP.index(s)
    if getOperatingProfitability(s, year) == -99:
        index = 0

    h.profitability = index / len(stocksOP)
    # opS = getOperatingProfitability(s, year)
    # if opS > 0:
    #     sumOP = 0
    #     for x in stocks:
    #         op = getOperatingProfitability(x, year)
    #         if op > 0:
    #             sumOP += op
    #
    #     h.profitability = opS / sumOP
    # else:
    #     h.profitability = 0

    # investment
    stocksINV = sorted(stocks, key=lambda x: getInvestment(x, year), reverse=True)
    index = stocksINV.index(s)
    if getInvestment(s, year) == -99:
        index = 0

    h.investment = index / len(stocksINV)

    # invS = getInvestment(s, year)
    # if invS > 0:
    #     sumINV = 0
    #     for x in stocks:
    #         inv = getInvestment(x, year)
    #         if inv > 0:
    #             sumINV += inv ** -1
    #
    #     h.investment = invS ** -1 / sumINV
    # else:
    #     h.investment = 0

    # sum of factors
    h.allFactors = h.profitability + h.investment
    # h.allFactors = h.value + h.profitability
    # h.allFactors = h.value + h.investment



    # print(s)
    # print(year)
    # print("ValueF: ", h.value)
    # print("ProfitabilityF: ", h.profitability)
    # print("InvestmentF: ", h.investment)
    # print("AllFactors: ", h.allFactors)
    # print("------")

    return h


def calculateWeight(holdings, bestOf=100):
    summFactors = 0

    for h in holdings:
        summFactors += h.allFactors

    for h in holdings:
        h.weight = (h.allFactors / summFactors) / 2

    return holdings


def getHoldings(stocks, year):
    holdings = []
    for s in stocks:
        h = calculateFactorExposure(s, stocks, year)
        holdings.append(h)

    holdings = calculateWeight(holdings)
    return holdings



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


def simulateYear(portfolioDf, holdings, start, end, errors):
    dates = pd.DatetimeIndex(start='2016-07-31', freq='M', periods=42)

    for h in holdings.values():
        try:
            priceData = get_price_data(h.stock.yahoo_ticker, start, end)
        except:
            errors.append(h.stock.yahoo_ticker)
            continue

        monthlyReturns = get_return_data(h.stock, priceData)

        returns = pd.DataFrame(np.zeros(shape=(42, 1)), index=dates, columns=list('S'))

        for idx in monthlyReturns.index:
            # monthly return * weight
            realReturn = monthlyReturns.at[idx, h.stock.yahoo_ticker] * float(h.weight)
            returns.set_value(idx, 'S', realReturn)

        portfolioDf['P'] = portfolioDf['P'] + returns['S']
        print(monthlyReturns)
        # print(portfolioDf)


    return portfolioDf, errors


def backtestPortfolio(holdings2016, holdings2017, holdings2018, holdings2019):
    # init portfolio df
    dates = pd.DatetimeIndex(start='2016-07-31', freq='M', periods=42)
    portfolioDf = pd.DataFrame(np.zeros(shape=(42, 1)), index=dates, columns=list('P'))
    errors = []
    # print("Start simulation")
    # portfolioDf, errors = simulateYear(portfolioDf, holdings2016, "2015-12-01", "2016-12-31", errors)
    # print("done")
    # portfolioDf, errors = simulateYear(portfolioDf, holdings2017, "2016-12-01", "2017-12-31", errors)
    # print("done")
    # portfolioDf, errors = simulateYear(portfolioDf, holdings2018, "2017-12-01", "2018-12-31", errors)
    # print("done")
    # portfolioDf, errors = simulateYear(portfolioDf, holdings2019, "2018-12-01", "2019-12-31", errors)
    # print("done")


    print("Start simulation")
    portfolioDf, errors = simulateYear(portfolioDf, holdings2016, "2016-06-01", "2017-06-30", errors)
    print("done")
    portfolioDf, errors = simulateYear(portfolioDf, holdings2017, "2017-06-01", "2018-06-30", errors)
    print("done")
    portfolioDf, errors = simulateYear(portfolioDf, holdings2018, "2018-06-01", "2019-06-30", errors)
    print("done")
    portfolioDf, errors = simulateYear(portfolioDf, holdings2019, "2019-06-01", "2019-12-31", errors)
    print("done")

    annulizedReturn = 1
    for idx in portfolioDf.index:
        annulizedReturn *= (1 + portfolioDf.at[idx, 'P'])

    annulizedReturn = (annulizedReturn - 1) * 100
    print(annulizedReturn)
    print(errors)

    return portfolioDf


def filterOutliers(stocks, year):
    stocks1 = sorted(stocks, key=lambda x: getPB(x, year), reverse=False)
    stocks1 = stocks1[10:]

    stocks2 = sorted(stocks1, key=lambda x: getOperatingProfitability(x, year), reverse=True)
    stocks2 = stocks2[10:]

    stocks3 = sorted(stocks2, key=lambda x: getInvestment(x, year), reverse=False)
    stocks3 = stocks3[10:]

    return stocks3


def calculateTurnover(holdings2016, holdings2017):
    change = 0
    change1 = 0

    for k in holdings2017.keys():
        if k in holdings2016:
            change += abs(holdings2016[k].weight - holdings2017[k].weight)
        else:
            change += holdings2017[k].weight

    for k in holdings2016.keys():
        if k in holdings2017:
            change1 += abs(holdings2017[k].weight - holdings2016[k].weight)
        else:
            change1 += holdings2016[k].weight

    if change > change1:
        print(change1)
    else:
        print(change)

def generate5FactorPorfolio():
    stocks = Stock.objects.all()

    stocks2016 = filterStocks(stocks, 2015)
    stocks2017 = filterStocks(stocks, 2016)
    stocks2018 = filterStocks(stocks, 2017)
    stocks2019 = filterStocks(stocks, 2018)

    # stocks2016 = filterOutliers(stocks2016, 2015)
    # stocks2017 = filterOutliers(stocks2017, 2016)
    # stocks2018 = filterOutliers(stocks2018, 2017)
    # stocks2019 = filterOutliers(stocks2019, 2018)

    print(len(stocks2016))
    print(len(stocks2017))
    print(len(stocks2018))
    print(len(stocks2019))

    # sort by marketCap

    stocks2016.sort(key=lambda x: x.marketcapindollars_set.filter(year=2015)[0].marketCap, reverse=True)
    stocks2017.sort(key=lambda x: x.marketcapindollars_set.filter(year=2016)[0].marketCap, reverse=True)
    stocks2018.sort(key=lambda x: x.marketcapindollars_set.filter(year=2017)[0].marketCap, reverse=True)
    stocks2019.sort(key=lambda x: x.marketcapindollars_set.filter(year=2018)[0].marketCap, reverse=True)

    num2016 = len(stocks2016)
    num2017 = len(stocks2017)
    num2018 = len(stocks2018)
    num2019 = len(stocks2019)

    largeCap2016 = stocks2016[:round(num2016 * 0.3)]
    largeCap2017 = stocks2017[:round(num2017 * 0.3)]
    largeCap2018 = stocks2018[:round(num2018 * 0.3)]
    largeCap2019 = stocks2019[:round(num2019 * 0.3)]

    smallCap2016 = stocks2016[round(num2016 * 0.7):]
    smallCap2017 = stocks2017[round(num2017 * 0.7):]
    smallCap2018 = stocks2018[round(num2018 * 0.7):]
    smallCap2019 = stocks2019[round(num2019 * 0.7):]

    # largeCap2016.sort(key=lambda x: getPB(x, 2015), reverse=False)
    # largeCap2017.sort(key=lambda x: getPB(x, 2016), reverse=False)
    # largeCap2018.sort(key=lambda x: getPB(x, 2017), reverse=False)
    # largeCap2019.sort(key=lambda x: getPB(x, 2018), reverse=False)
    #
    # smallCap2016.sort(key=lambda x: getPB(x, 2015), reverse=False)
    # smallCap2017.sort(key=lambda x: getPB(x, 2016), reverse=False)
    # smallCap2018.sort(key=lambda x: getPB(x, 2017), reverse=False)
    # smallCap2019.sort(key=lambda x: getPB(x, 2018), reverse=False)
    #
    # largeCapOP2016 = largeCap2016[:round(len(largeCap2016) * 0.2)]
    # largeCapOP2017 = largeCap2017[:round(len(largeCap2017) * 0.2)]
    # largeCapOP2018 = largeCap2018[:round(len(largeCap2018) * 0.2)]
    # largeCapOP2019 = largeCap2019[:round(len(largeCap2019) * 0.2)]
    #
    # smallCapOP2016 = smallCap2016[:round(len(smallCap2016) * 0.2)]
    # smallCapOP2017 = smallCap2017[:round(len(smallCap2017) * 0.2)]
    # smallCapOP2018 = smallCap2018[:round(len(smallCap2018) * 0.2)]
    # smallCapOP2019 = smallCap2019[:round(len(smallCap2019) * 0.2)]

    largeCapHoldings2016 = getHoldings(largeCap2016, 2015)
    largeCapHoldings2017 = getHoldings(largeCap2017, 2016)
    largeCapHoldings2018 = getHoldings(largeCap2018, 2017)
    largeCapHoldings2019 = getHoldings(largeCap2019, 2018)

    smallCapHoldings2016 = getHoldings(smallCap2016, 2015)
    smallCapHoldings2017 = getHoldings(smallCap2017, 2016)
    smallCapHoldings2018 = getHoldings(smallCap2018, 2017)
    smallCapHoldings2019 = getHoldings(smallCap2019, 2018)

    holdings2016 = largeCapHoldings2016 + smallCapHoldings2016
    holdings2017 = largeCapHoldings2017 + smallCapHoldings2017
    holdings2018 = largeCapHoldings2018 + smallCapHoldings2018
    holdings2019 = largeCapHoldings2019 + smallCapHoldings2019

    # holdings2016 = getPortfolio(stocks2016, 2015, 0.20, False)
    # holdings2017 = getPortfolio(stocks2017, 2016, 0.20, False)
    # holdings2018 = getPortfolio(stocks2018, 2017, 0.20, False)
    # holdings2019 = getPortfolio(stocks2019, 2018, 0.20, False)

    # dfPortfolio = backtestPortfolio(holdings2016, holdings2017, holdings2018, holdings2019)
    h2016 = {}
    h2017 = {}
    h2018 = {}
    h2019 = {}

    for h in holdings2016:
        h2016[h.stock.ticker] = h

    for h in holdings2017:
        h2017[h.stock.ticker] = h

    for h in holdings2018:
        h2018[h.stock.ticker] = h

    for h in holdings2019:
        h2019[h.stock.ticker] = h

    calculateTurnover(h2016, h2017)
    calculateTurnover(h2017, h2018)
    calculateTurnover(h2018, h2019)

    # print(len(holdings2016))
    # print(len(holdings2017))
    # print(len(holdings2018))
    # print(len(holdings2019))

    return dfPortfolio


def listToDict(lst):
    op = {lst[i].ticker: lst[i] for i in lst}
    return op


def getTop(stocks, top):
    stocksTop = stocks[:round(len(stocks) * top)]
    return stocksTop


def getHoldings1(stocks, factor, year, equal):
    h = {}
    if factor == "MKT":
        if equal:
            size = len(stocks)
            for s in stocks:
                hld = Holding()
                hld.stock = s
                hld.weight = decimal.Decimal(1 / size) * decimal.Decimal(0.2)
                h[s.ticker] = hld
        else:
            sum = 0
            for s in stocks:
                sum += getMarketCap(s, year)

            for s in stocks:
                hld = Holding()
                hld.stock = s
                hld.weight = (getMarketCap(s, year) / sum) * decimal.Decimal(0.2)
                h[s.ticker] = hld

    elif factor == "SMB":
        smbOP = sorted(stocks, key=lambda x: getOperatingProfitability(x, year), reverse=True)
        smbINV = sorted(stocks, key=lambda x: getInvestment(x, year), reverse=False)
        if year == 2015:
            smbINV = sorted(stocks, key=lambda x: getPB(x, year), reverse=False)

        smbOpTop = getTop(stocks, 0.5)
        smbInvTop = getTop(stocks, 0.5)

        newSMB = smbOpTop

        for x in smbInvTop:
            if x not in newSMB:
                newSMB.append(x)
        if equal:
            size = len(newSMB)
            for s in stocks:
                hld = Holding()
                hld.stock = s
                hld.weight = decimal.Decimal(1 / size) * decimal.Decimal(0.2)
                h[s.ticker] = hld
        else:
            sum = 0
            for s in newSMB:
                sum += getMarketCap(s, year) ** -1

            for s in newSMB:
                hld = Holding()
                hld.stock = s
                hld.weight = (getMarketCap(s, year) ** -1 / sum) * decimal.Decimal(0.2)
                h[s.ticker] = hld
    elif factor == "HML":
        if equal:
            size = len(stocks)
            for s in stocks:
                hld = Holding()
                hld.stock = s
                hld.weight = decimal.Decimal(1 / size) * decimal.Decimal(0.2)
                h[s.ticker] = hld
        else:
            sum = 0
            for s in stocks:
                sum += getPB(s, year) ** -1

            for s in stocks:
                hld = Holding()
                hld.stock = s
                if getPB(s, year) == 0:
                    hld.weight = 0
                else:
                    hld.weight = (getPB(s, year) ** -1 / sum) * decimal.Decimal(0.2)
                h[s.ticker] = hld
    elif factor == "RMW":
        if equal:
            size = len(stocks)
            for s in stocks:
                hld = Holding()
                hld.stock = s
                hld.weight = decimal.Decimal(1 / size) * decimal.Decimal(0.2)
                h[s.ticker] = hld
        else:
            sum = 0
            for s in stocks:
                sum += getOperatingProfitability(s, year)

            for s in stocks:
                hld = Holding()
                hld.stock = s
                hld.weight = (getOperatingProfitability(s, year) / sum) * decimal.Decimal(0.2)
                h[s.ticker] = hld
    elif factor == "CMA":
        if year == 2015:
            if equal:
                size = len(stocks)
                for s in stocks:
                    hld = Holding()
                    hld.stock = s
                    hld.weight = decimal.Decimal(1 / size) * decimal.Decimal(0.2)
                    h[s.ticker] = hld
            else:
                sum = 0
                for s in stocks:
                    sum += getPB(s, year) ** -1

                for s in stocks:
                    hld = Holding()
                    hld.stock = s
                    hld.weight = (getPB(s, year) ** -1 / sum) * decimal.Decimal(0.2)
                    h[s.ticker] = hld
        else:
            if equal:
                size = len(stocks)
                for s in stocks:
                    hld = Holding()
                    hld.stock = s
                    hld.weight = decimal.Decimal(1 / size) * decimal.Decimal(0.2)
                    h[s.ticker] = hld
            else:
                sum = 0
                for s in stocks:
                    sum += getInvestment(s, year) ** -1

                for s in stocks:
                    hld = Holding()
                    hld.stock = s
                    hld.weight = (getInvestment(s, year) ** -1 / sum) * decimal.Decimal(0.2)
                    h[s.ticker] = hld

    return h


def mergeFactorPortfolios(mktH, smbH, hmlH, rmwH, cmaH):
    portfolio = {}

    for h in mktH.values():
        if h.stock.ticker in portfolio.keys():
            portfolio[h.stock.ticker].weight += h.weight
        else:
            portfolio[h.stock.ticker] = h

    for h in smbH.values():
        if h.stock.ticker in portfolio.keys():
            portfolio[h.stock.ticker].weight += h.weight
        else:
            portfolio[h.stock.ticker] = h

    for h in hmlH.values():
        if h.stock.ticker in portfolio.keys():
            portfolio[h.stock.ticker].weight += decimal.Decimal(h.weight)
        else:
            portfolio[h.stock.ticker] = h

    for h in rmwH.values():
        if h.stock.ticker in portfolio.keys():
            portfolio[h.stock.ticker].weight += decimal.Decimal(h.weight)
        else:
            portfolio[h.stock.ticker] = h

    for h in cmaH.values():
        if h.stock.ticker in portfolio.keys():
            portfolio[h.stock.ticker].weight += decimal.Decimal(h.weight)
        else:
            portfolio[h.stock.ticker] = h

    return portfolio



def getPortfolio(stocks, year, top, equal):

    if year == 2015:
        mkt = sorted(stocks, key=lambda x: getMarketCap(x, year), reverse=True)
        smb = sorted(stocks, key=lambda x: getMarketCap(x, year), reverse=False)
        hml = sorted(stocks, key=lambda x: getPB(x, year), reverse=False)
        rmw = sorted(stocks, key=lambda x: getOperatingProfitability(x, year), reverse=True)
        cma = sorted(stocks, key=lambda x: getPB(x, year), reverse=False)

        mktTop = getTop(mkt, top)
        smbTop = getTop(smb, top)
        hmlTop = getTop(hml, top)
        rmwTop = getTop(rmw, top)
        cmaTop = getTop(cma, top)

        mktH = getHoldings1(mktTop, "MKT", year, equal)
        smbH = getHoldings1(smbTop, "SMB", year, equal)
        hmlH = getHoldings1(hmlTop, "HML", year, equal)
        rmwH = getHoldings1(rmwTop, "RMW", year, equal)
        cmaH = getHoldings1(cmaTop, "CMA", year, equal)

        portfolio = mergeFactorPortfolios(mktH, smbH, hmlH, rmwH, cmaH)

        return portfolio
    else:
        mkt = sorted(stocks, key=lambda x: getMarketCap(x, year), reverse=True)
        smb = sorted(stocks, key=lambda x: getMarketCap(x, year), reverse=False)
        hml = sorted(stocks, key=lambda x: getPB(x, year), reverse=False)
        rmw = sorted(stocks, key=lambda x: getOperatingProfitability(x, year), reverse=True)
        cma = sorted(stocks, key=lambda x: getInvestment(x, year), reverse=False)

        mktTop = getTop(mkt, top)
        smbTop = getTop(smb, top)
        hmlTop = getTop(hml, top)
        rmwTop = getTop(rmw, top)
        cmaTop = getTop(cma, top)

        mktH = getHoldings1(mktTop, "MKT", year, equal)
        smbH = getHoldings1(smbTop, "SMB", year, equal)
        hmlH = getHoldings1(hmlTop, "HML", year, equal)
        rmwH = getHoldings1(rmwTop, "RMW", year, equal)
        cmaH = getHoldings1(cmaTop, "CMA", year, equal)

        portfolio = mergeFactorPortfolios(mktH, smbH, hmlH, rmwH, cmaH)

        return portfolio



class Job(DailyJob):
    help = "My sample job."

    def execute(self):
        generate5FactorPorfolio()








