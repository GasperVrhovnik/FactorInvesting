import datetime

from django_extensions.management.jobs import DailyJob
import pandas as pd

from ...models import Stock

class Job(DailyJob):
    help = "My sample job."

    def execute(self):

        stocks = Stock.objects.all()
        for s in stocks:
            listP = s.profitstoassets_set.all()

            if len(listP) > 0:
                for p in listP:
                    if round(p.profitability) != -99:
                        s.p = True
                        s.save()
                        break


