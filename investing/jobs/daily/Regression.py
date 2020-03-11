import datetime

from django_extensions.management.jobs import DailyJob
import pandas as pd
# Datareader to download price data from Yahoo Finance
import pandas_datareader as web
# Statsmodels to run our multiple regression model
import statsmodels.api as smf
# To download the Fama French data from the web
import urllib.request
# To unzip the ZipFile
import zipfile
from .FiveFactorPortfolio import generate5FactorPorfolio

from ...models import Stock
def get_fama_french():
    # Web url
    ff_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Europe_5_Factors_CSV.zip"
    urllib.request.urlretrieve(ff_url, 'fama_french.zip')
    zip_file = zipfile.ZipFile('fama_french.zip', 'r')
    zip_file.extractall()
    zip_file.close()
    ff_factors = pd.read_csv('Europe_5_Factors.csv', skiprows=3, index_col=0)
    ff_row = ff_factors.isnull().any(1).nonzero()[0][0]
    ff_factors = pd.read_csv('Europe_5_Factors.csv', skiprows=3, nrows=ff_row, index_col=0)
    ff_factors.index = pd.to_datetime(ff_factors.index, format='%Y%m')
    ff_factors.index = ff_factors.index + pd.offsets.MonthEnd()
    ff_factors = ff_factors.apply(lambda x: x / 100)
    return ff_factors


class Job(DailyJob):
    help = "My sample job."

    def execute(self):
        ff_data = get_fama_french()
        # print(ff_data.tail())

        ff_last = ff_data.index[ff_data.shape[0] - 1].date()

        price_data = generate5FactorPorfolio()
        price_data = price_data.loc[:ff_last]
        price_data.columns = ['portfolio']

        # print(ff_data.tail())
        # print(price_data.tail())

        all_data = pd.merge(price_data, ff_data, how='inner', left_index=True, right_index=True)
        # Rename the columns
        all_data.rename(columns={"Mkt-RF": "mkt_excess"}, inplace=True)
        # Calculate the excess returns
        all_data['port_excess'] = all_data['portfolio'] - all_data['RF']
        # all_data['portfolio_return'] = all_data['portfolio']
        # print(all_data.tail())

        # model = smf.formula.ols(formula="port_excess ~ mkt_excess + SMB + HML + RMW + CMA", data=all_data).fit()
        model1 = smf.formula.ols(formula="port_excess ~ mkt_excess + SMB + HML", data=all_data).fit()
        model2 = smf.formula.ols(formula="port_excess ~ mkt_excess + SMB + HML + RMW + CMA", data=all_data).fit()
        model3 = smf.formula.ols(formula="port_excess ~ mkt_excess + SMB + RMW + CMA", data=all_data).fit()
        print(model1.summary())
        print(model2.summary())
        print(model3.summary())

        price_data.to_csv("out.csv", encoding='utf-8')
