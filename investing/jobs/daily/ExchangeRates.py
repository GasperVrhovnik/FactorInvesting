import datetime
import requests
import json
from django_extensions.management.jobs import DailyJob
import pandas as pd
from ...models import ExchangeRate

from ...models import Stock

class Job(DailyJob):
    help = "My sample job."

    def execute(self):

        dates = [
            "2015-01-31", "2015-02-28", "2015-03-31", "2015-04-30", "2015-05-31", "2015-06-30", "2015-07-31", "2015-08-31", "2015-09-30",
            "2015-10-31", "2015-11-30", "2015-12-31", "2016-01-31", "2016-02-29", "2016-03-31", "2016-04-30", "2016-05-31",
            "2016-06-30", "2016-07-31", "2016-08-31", "2016-09-30", "2016-10-31", "2016-11-30", "2016-12-31", "2017-01-31",
            "2017-02-28", "2017-03-31", "2017-04-30", "2017-05-31", "2017-06-30", "2017-07-31", "2017-08-31", "2017-09-30",
            "2017-10-31", "2017-11-30", "2017-12-31", "2018-01-31", "2018-02-28", "2018-03-31", "2018-04-30", "2018-05-31",
            "2018-06-30", "2018-07-31", "2018-08-31", "2018-09-30", "2018-10-31", "2018-11-30", "2018-12-31", "2019-01-31",
            "2019-02-28", "2019-03-31", "2019-04-30", "2019-05-31", "2019-06-30", "2019-07-31", "2019-08-31", "2019-09-30",
            "2019-10-31", "2019-11-30", "2019-12-31"]

        datesNew = ["2015-01-01", "2014-01-01"]

        for d in datesNew:
            url = "https://openexchangerates.org/api/historical/" + d + ".json?app_id=b343ecb895d34753a16ec07b423671bc"
            params = {
                "symbols": "EUR,SEK,GBP,DKK,NOK,CHF",
            }

            response = requests.get(url, params=params)
            rates = response.json()['rates']
            print(rates)
            eur = ExchangeRate()
            dkk = ExchangeRate()
            sek = ExchangeRate()
            nok = ExchangeRate()
            GBp = ExchangeRate()
            chf = ExchangeRate()

            eur.currency = 'EUR'
            eur.rate = rates['EUR'] ** -1
            eur.date = d

            dkk.currency = 'DKK'
            dkk.rate = rates['DKK'] ** -1
            dkk.date = d

            sek.currency = 'SEK'
            sek.rate = rates['SEK'] ** -1
            sek.date = d

            nok.currency = 'NOK'
            nok.rate = rates['NOK'] ** -1
            nok.date = d

            GBp.currency = 'GBp'
            GBp.rate = rates['GBP'] ** -1
            GBp.date = d

            chf.currency = 'CHF'
            chf.rate = rates['CHF'] ** -1
            chf.date = d

            eur.save()
            dkk.save()
            sek.save()
            nok.save()
            GBp.save()
            chf.save()
