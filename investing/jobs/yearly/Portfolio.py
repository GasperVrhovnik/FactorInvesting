import datetime
from decimal import Decimal

from django_extensions.management.jobs import YearlyJob

from investing.models import Stock, ProfitsToAssets


def filterStocksWithProfitability(stocks):
    filtered = []

    for s in stocks:
        prof = s.profitstoassets_set.filter(year=2018)
        if len(prof) == 0:
            continue

        prof = prof[0]

        if prof is None or round(prof.profitability) == -99:
            continue

        filtered.append(s)

    return filtered


def filterStocksWithPB(stocks):
    filtered = []

    for s in stocks:
        if round(s.p_b) == -99:
            continue

        filtered.append(s)

    return filtered


def generatePortfolioOfLargeAndMidCapStocks(stocksWithPB, stocksWithProf):
    numValue = len(stocksWithPB)
    numProf = len(stocksWithProf)

    davideValue = round(numValue * 0.66)
    davideProf = round(numProf * 0.66)

    largeAndMidCapValue = stocksWithPB[:davideValue]
    largeAndMidCapProf = stocksWithProf[:davideProf]

    numLargeValue = len(largeAndMidCapValue)
    numLargeProf = len(largeAndMidCapProf)

    largeAndMidCapValue.sort(key=lambda x: x.p_b)
    largeAndMidCapProf.sort(key=lambda x: x.profitstoassets_set.filter(year=2018)[0].profitability, reverse=True)

    davideValue = round(numValue * 0.20)
    davideProf = round(numProf * 0.20)

    profPortfolio = largeAndMidCapProf[:davideProf]
    valuePortfolio = largeAndMidCapValue[:davideValue]

    totalProf = 0
    for s in profPortfolio:
        totalProf = totalProf + s.profitstoassets_set.filter(year=2018)[0].profitability

    totalBP = 0
    # print("------")
    for s in valuePortfolio:
        totalBP = totalBP + s.p_b ** -1

    # dictionary key = ticker value = weight
    portfolio = {}
    totalWeight = 0

    for s in profPortfolio:
        weight = round(Decimal(0.66) * abs(s.profitstoassets_set.filter(year=2018)[0].profitability) / (totalProf * 2), 5)
        ticker = s.ticker
        if ticker in portfolio:
            portfolio[ticker] += weight
            totalWeight += weight
            # print("Again Adding " + ticker + ", prof: " + str(s.profitstoassets_set.filter(year=2018)[0].profitability) + ", weight: " + str(weight))
        else:
            portfolio[ticker] = weight
            totalWeight += weight
            # print("Adding " + ticker + ", prof: " + str(s.profitstoassets_set.filter(year=2018)[0].profitability) + ", weight: " + str(weight))

    for s in valuePortfolio:
        weight = round(Decimal(0.66) * s.p_b ** -1 / (totalBP * 2), 5)
        ticker = s.ticker
        if ticker in portfolio:
            portfolio[ticker] += weight
            totalWeight += weight
            # print("Again Adding " + ticker + ", prof: " + str(s.p_b) + ", weight: " + str(weight))
        else:
            portfolio[ticker] = weight
            totalWeight += weight
            # print("Adding " + ticker + ", prof: " + str(s.p_b) + ", weight: " + str(weight))

    # print(len(profPortfolio))
    # print(len(valuePortfolio))
    # print(len(portfolio))
    # print(totalWeight)

    return portfolio


def generateSmallCapPortfolio(stocksWithProf, stocksWithPB):
    numValue = len(stocksWithPB)
    numProf = len(stocksWithProf)

    davideValue = round(numValue * 0.66)
    davideProf = round(numProf * 0.66)

    stocksValue = stocksWithPB[davideValue:]
    stocksProf = stocksWithProf[davideProf:]

    numValue = len(stocksValue)
    numProf = len(stocksProf)

    stocksValue.sort(key=lambda x: x.p_b)
    stocksProf.sort(key=lambda x: x.profitstoassets_set.filter(year=2018)[0].profitability, reverse=True)

    davideValue = round(numValue * 0.20)
    davideProf = round(numProf * 0.20)

    profPortfolio = stocksProf[:davideProf]
    valuePortfolio = stocksValue[:davideValue]

    totalProf = 0
    for s in profPortfolio:
        totalProf = totalProf + s.profitstoassets_set.filter(year=2018)[0].profitability

    totalBP = 0
    # print("------")
    for s in valuePortfolio:
        totalBP = totalBP + s.p_b ** -1

    # dictionary key = ticker value = weight
    portfolio = {}
    totalWeight = 0

    for s in profPortfolio:
        weight = round(Decimal(0.34) * abs(s.profitstoassets_set.filter(year=2018)[0].profitability) / (totalProf * 2), 5)
        ticker = s.ticker
        if weight < 0.00:
            print("NEGATIVE-----------------------------")
            print(ticker, weight)
        if ticker in portfolio:
            portfolio[ticker] += weight
            totalWeight += weight
            # print("Again Adding " + ticker + ", prof: " + str(s.profitstoassets_set.filter(year=2018)[0].profitability) + ", weight: " + str(weight))
        else:
            portfolio[ticker] = weight
            totalWeight += weight
            # print("Adding " + ticker + ", prof: " + str(s.profitstoassets_set.filter(year=2018)[0].profitability) + ", weight: " + str(weight))

    for s in valuePortfolio:
        weight = round(Decimal(0.34) * s.p_b ** -1 / (totalBP * 2), 5)
        ticker = s.ticker
        if ticker in portfolio:
            portfolio[ticker] += weight
            totalWeight += weight
            # print("Again Adding " + ticker + ", prof: " + str(s.p_b) + ", weight: " + str(weight))
        else:
            portfolio[ticker] = weight
            totalWeight += weight
            # print("Adding " + ticker + ", prof: " + str(s.p_b) + ", weight: " + str(weight))

    # print(len(profPortfolio))
    # print(len(valuePortfolio))
    # print(len(portfolio))
    # print(totalWeight)

    return portfolio


def generatePortfolio():
    stocks = Stock.objects.all()

    stocksWithPB = filterStocksWithPB(stocks)
    stocksWithProf = filterStocksWithProfitability(stocks)

    stocksWithPB.sort(key=lambda x: x.market_cap, reverse=True)
    stocksWithProf.sort(key=lambda x: x.market_cap, reverse=True)

    # for s in stocksWithProf:
    #     print(s.ticker, s.profitstoassets_set.filter(year=2018)[0].profitability, s.market_cap)

    largeMidCapPortfolio = generatePortfolioOfLargeAndMidCapStocks(stocksWithProf, stocksWithProf)
    smallCapPortfolio = generateSmallCapPortfolio(stocksWithProf, stocksWithPB)

    portfolio = {}

    for ticker in largeMidCapPortfolio:
        weight = largeMidCapPortfolio[ticker]

        if ticker in portfolio:
            portfolio[ticker] += weight
            # print("Addeed again")
            # print(ticker)
        else:
            portfolio[ticker] = weight

    for ticker in smallCapPortfolio:
        weight = smallCapPortfolio[ticker]

        if ticker in portfolio:
            portfolio[ticker] += weight
            # print("Addeed again")
            # print(ticker)
        else:
            portfolio[ticker] = weight

    totalWeight = 0
    for ticker in portfolio:
        totalWeight += portfolio[ticker]

    # print(totalWeight)

    # if 'ARYN' in smallCapPortfolio and 'ARYN' in largeMidCapPortfolio:
    #     # print("wtf")
    #
    # if 'TKO' in smallCapPortfolio and 'TKO' in largeMidCapPortfolio:
    #     # print("wtf")
    #


    for ticker in portfolio:
        stock = Stock.objects.filter(ticker=ticker)[0]
        if len(stock.profitstoassets_set.filter(year=2018)) > 0:
            print(portfolio[ticker], stock.ticker, stock.p_b, stock.market_cap, stock.profitstoassets_set.filter(year=2018)[0].profitability)
        else:
            print(portfolio[ticker], stock.ticker, stock.p_b, stock.market_cap)




class Job(YearlyJob):
    help = "My sample job."

    def execute(self):
        generatePortfolio()
