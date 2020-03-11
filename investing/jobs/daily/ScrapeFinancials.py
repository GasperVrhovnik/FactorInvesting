from django_extensions.management.jobs import DailyJob
import requests

from ...models import Stock, ProfitsToAssets
from bs4 import BeautifulSoup as bs


def parseListFromMW(l):
    parsed = []
    gross_profits_list2 = []
    for i in l:
        x = list(i)
        new = []
        for y in x:
            if y == ',':
                new.append('.')
            else:
                new.append(y)
        parsed.append("".join(new))

    parsedNew = []
    for i in parsed:
        if i[0] == '(':
            profit = i[1:-1]
            if profit[-1] == 'T':
                profit = - float(profit[:-1]) * 10 ** 12
            elif profit[-1] == 'B':
                profit = - float(profit[:-1]) * 10 ** 9
            elif profit[-1] == 'M':
                profit = - float(profit[:-1]) * 10 ** 6
            elif profit != '-':
                profit = - float(profit) * 10 ** 3
            parsedNew.append(profit)
        else:
            if i[-1] == 'T':
                i = float(i[:-1]) * 10 ** 12
            elif i[-1] == 'B':
                i = float(i[:-1]) * 10 ** 9
            elif i[-1] == 'M':
                i = float(i[:-1]) * 10 ** 6
            elif i != '-':
                i = float(i) * 10 ** 3
            parsedNew.append(i)

    return parsedNew


def persistProfitsToAssets(grossIncome, totalAssets, years, stock):
    if len(grossIncome) == len(totalAssets):
        i = 0
        for y in years:
            profit = ProfitsToAssets()

            if grossIncome[i] == '-' or totalAssets[i] == '-':
                profit.stock = stock
                profit.year = y
                profit.profitability = -99
            else:
                profit.stock = stock
                profit.year = y
                profit.profitability = grossIncome[i] / totalAssets[i]

            profit.save()
            i = i + 1
    else:
        print("Problem with list length")


def getProfitability(stock):
    url_financials = 'https://www.marketwatch.com/investing/stock/' + stock.ticker + '/financials'
    url_balancesheet = 'https://www.marketwatch.com/investing/stock/' + stock.ticker + '/financials/balance-sheet'

    text_soup_financials = bs(requests.get(url_financials).text, "lxml")
    text_soup_balancesheet = bs(requests.get(url_balancesheet).text, "lxml")

    # Income statement
    titlesFinancials = text_soup_financials.findAll('td', {'class': 'rowTitle'})
    titlesBalanceSheet = text_soup_balancesheet.findAll('td', {'class': 'rowTitle'})
    yearsF = text_soup_financials.findAll('tr', {'class': 'topRow'})[0].findChildren('th')[1: -1]
    # yearsB = text_soup_balancesheet.findAll('tr', {'class': 'topRow'})[0].findChildren('th')[1: -1]

    grossIncome = []
    totalAssets = []
    years = [int(th.text) for th in yearsF if th.text]

    for title in titlesFinancials:
        if ' Gross Income' == title.text:
            grossIncome = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]
            break

    for title in titlesBalanceSheet:
        if ' Total Assets' == title.text:
            totalAssets = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]
            break

    grossIncome = parseListFromMW(grossIncome)
    totalAssets = parseListFromMW(totalAssets)
    print(grossIncome)
    print(totalAssets)
    print(years)

    persistProfitsToAssets(grossIncome, totalAssets, years, stock)


def getPB(stock):
    url_profile = 'https://www.marketwatch.com/investing/stock/' + stock.ticker + '/profile'

    text_soup_profile = bs(requests.get(url_profile).text, "lxml")

    profile = text_soup_profile.findAll('div', {'class': 'section'})

    for p in profile:
        l = p.findChildren('p')
        if l[0].text == 'Price to Book Ratio':
            pb = l[1].text
            if pb != '-':
                print(pb)
                stock.p_b = float(pb)
                stock.save()




def getFinancialsForTicker(stock):
    print(stock.ticker)
    # Profits to Assets
    getProfitability(stock)

    # P/B
    # getPB(stock)






class Job(DailyJob):
    help = "My sample job."

    def execute(self):
        # errorList = []
        # i = 264
        # stocks = Stock.objects.all()
        # for s in stocks[300:]:
        #     print(i)
        #     i = i + 1
        #     try:
        #         getFinancialsForTicker(s)
        #     except:
        #         errorList.append(s.ticker)
        #
        # print(errorList)

        stocks = Stock.objects.filter(ticker='PEGRF')[0]
        getFinancialsForTicker(stocks)
