from django_extensions.management.jobs import DailyJob
from bs4 import BeautifulSoup as bs
import requests

from ...models import Stock, Revenue, InterestExpense, SGA_Expense, CoGS, Assets, Liabilities

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
            else:
                print("no info")
                profit = -99
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
            else:
                print("no info")
                i = -99
            parsedNew.append(i)

    return parsedNew


def saveInfoFinancial(stock, years, rev, intrExp, SGAExp, Cogs):
    i = 0
    for y in years:
        revenues = Revenue()
        interestExpense = InterestExpense()
        sga_Expense = SGA_Expense()
        cogs = CoGS()

        if rev[i] != -99:
            revenues.stock = stock
            revenues.year = y
            try:
                revenues.revenue = rev[i]
            except IndexError:
                revenues.revenue = -99
            revenues.save()

        if intrExp[i] != -99:
            interestExpense.stock = stock
            interestExpense.year = y
            try:
                interestExpense.interestExpense = intrExp[i]
            except IndexError:
                interestExpense.interestExpense = -99
            interestExpense.save()

        if SGAExp[i] != -99:
            sga_Expense.stock = stock
            sga_Expense.year = y
            try:
                sga_Expense.SGA_Expense = SGAExp[i]
            except IndexError:
                sga_Expense.SGA_Expense = -99
            sga_Expense.save()

        if Cogs[i] != -99:
            cogs.stock = stock
            cogs.year = y
            try:
                cogs.CoGS = Cogs[i]
            except IndexError:
                cogs.CoGS = -99

            cogs.save()

        i = i + 1

def saveInfoFBalanceSheet(stock, years, totalAssets, totalLiabilites):
    i = 0
    for y in years:
        assets = Assets()
        liabilities = Liabilities()

        if totalAssets[i] != -99:
            assets.stock = stock
            assets.year = y
            try:
                assets.assets = totalAssets[i]
            except IndexError:
                assets.assets = -99
            assets.save()

        if totalLiabilites[i] != -99:
            liabilities.stock = stock
            liabilities.year = y
            try:
                liabilities.liabilities = totalLiabilites[i]
            except IndexError:
                liabilities.liabilities = -99
            liabilities.save()
        i = i + 1

def getStockInfo(stock):
    url_financials = 'https://www.marketwatch.com/investing/stock/' + stock.ticker + '/financials'
    url_balancesheet = 'https://www.marketwatch.com/investing/stock/' + stock.ticker + '/financials/balance-sheet'

    text_soup_financials = bs(requests.get(url_financials).text, "lxml")
    text_soup_balancesheet = bs(requests.get(url_balancesheet).text, "lxml")

    # Income statement
    titlesFinancials = text_soup_financials.findAll('td', {'class': 'rowTitle'})
    titlesBalanceSheet = text_soup_balancesheet.findAll('td', {'class': 'rowTitle'})

    yearsF = text_soup_financials.findAll('tr', {'class': 'topRow'})[0].findChildren('th')[1: -1]
    yearsB = text_soup_balancesheet.findAll('tr', {'class': 'topRow'})[0].findChildren('th')[1: -1]
    yearsF = [int(th.text) for th in yearsF if th.text]
    yearsB = [int(th.text) for th in yearsB if th.text]

    revenues = []
    CoGS = []
    SGAExpense = []
    InterestExp = []

    totalAssets = []
    totalLiabilities = []


    for title in titlesFinancials:
        if 'Sales/Revenue' in title.text:
            revenues = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]

        if ' Cost of Goods Sold (COGS) incl. D&A' == title.text:
            CoGS = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]

        if ' SG&A Expense' == title.text:
            SGAExpense = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]

        if ' Interest Expense' == title.text:
            InterestExp = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]


    for title in titlesBalanceSheet:
        if ' Total Assets' == title.text:
            totalAssets = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]

        if ' Total Liabilities' == title.text:
            totalLiabilities = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]



    revenues = parseListFromMW(revenues)
    CoGS = parseListFromMW(CoGS)
    SGAExpense = parseListFromMW(SGAExpense)
    InterestExp = parseListFromMW(InterestExp)
    totalAssets = parseListFromMW(totalAssets)
    totalLiabilities = parseListFromMW(totalLiabilities)

    print(stock)
    print(yearsF)
    print(yearsB)

    print(revenues)
    print(CoGS)
    print(SGAExpense)
    print(InterestExp)

    print(totalAssets)
    print(totalLiabilities)

    print("Saving")
    saveInfoFinancial(stock, yearsF, revenues, InterestExp, SGAExpense, CoGS)
    saveInfoFBalanceSheet(stock, yearsB, totalAssets, totalLiabilities)


class Job(DailyJob):
    help = "My sample job."

    def execute(self):
        stocks = Stock.objects.all()
        errorList = []
        for s in stocks:
            try:
                getStockInfo(s)
            except:
                errorList.append(s.ticker)
