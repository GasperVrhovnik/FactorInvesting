import datetime

from django_extensions.management.jobs import DailyJob
import pandas as pd

from ...models import Stock

class Job(DailyJob):
    help = "My sample job."

    def execute(self):
        data = pd.read_csv("SPEU-holdings.csv", chunksize=1)
        for d in data:
            row_list = d.get_values()[0]
            name = row_list[0]
            ticker = row_list[1]
            marketCap = row_list[2] # in percetages
            marketCap = float(marketCap[:-1])

            stock = Stock.objects.filter(ticker=ticker)
            print(stock)
            if len(stock) == 0:
                stock = Stock(ticker=ticker, market_cap=marketCap)
                stock.date_updated = datetime.date.today()
                stock.save()
                continue

            if len(stock) == 1:
                stock = stock[0]
                # stock.name = name
                # stock.ticker = ticker
                if stock.p_b == 0.00:
                    stock.p_b = -99
                stock.market_cap = marketCap
                stock.date_updated = datetime.date.today()
                stock.save()



