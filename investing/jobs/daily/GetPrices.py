from django_extensions.management.jobs import DailyJob
# Pandas to read csv file and other things
import pandas as pd
# Datareader to download price data from Yahoo Finance
import pandas_datareader as web
# Statsmodels to run our multiple regression model
import statsmodels.api as smf
# To download the Fama French data from the web
import urllib.request
# To unzip the ZipFile
import zipfile


def get_return_data(price_data, period="M"):
    # Resample the data to monthly price
    price = price_data.resample(period).last()

    # Calculate the percent change
    ret_data = price.pct_change()[1:]

    # convert from series to DataFrame
    ret_data = pd.DataFrame(ret_data)

    # Rename the Column
    ret_data.columns = ['portfolio']
    return ret_data



def get_fama_french():
    # Web url
    ff_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Europe_5_Factors_CSV.zip"

    # Download the file and save it
    # We will name it fama_french.zip file

    urllib.request.urlretrieve(ff_url, 'fama_french.zip')
    zip_file = zipfile.ZipFile('fama_french.zip', 'r')

    # Next we extact the file data

    zip_file.extractall()

    # Make sure you close the file after extraction

    zip_file.close()

    # Now open the CSV file

    ff_factors = pd.read_csv('F-F_Research_Data_Factors.csv', skiprows=3, index_col=0)
    # We want to find out the row with NULL value
    # We will skip these rows

    ff_row = ff_factors.isnull().any(1).nonzero()[0][0]

    # Read the csv file again with skipped rows
    ff_factors = pd.read_csv('F-F_Research_Data_Factors.csv', skiprows=3, nrows=ff_row, index_col=0)

    # Format the date index
    ff_factors.index = pd.to_datetime(ff_factors.index, format='%Y%m')

    # Format dates to end of month
    ff_factors.index = ff_factors.index + pd.offsets.MonthEnd()

    # Convert from percent to decimal
    ff_factors = ff_factors.apply(lambda x: x / 100)
    return ff_factors
# Build the get_price function
# We need 3 arguments, ticker, start and end date


def get_price_data(ticker, start, end):
    price = web.get_data_yahoo(ticker, start, end)
    price = price['Adj Close'] # keep only the Adj Price col
    return price


class Job(DailyJob):
    help = "My sample job."

    def execute(self):
        # Last day of FF data
        ff_data = get_fama_french()
        print(ff_data.tail())
        ff_last = ff_data.index[ff_data.shape[0] - 1].date()
        # Get Price data for Fidelity's fund
        price_data = get_price_data("IJS", "1980-01-01", "2020-01-30")
        # Make sure to only have data upto last date of Fama French data
        price_data = price_data.loc[:ff_last]
        print(price_data.tail())

        ret_data = get_return_data(price_data, "M")
        print(ret_data.tail())

        # Merging the data
        all_data = pd.merge(pd.DataFrame(ret_data), ff_data, how='inner', left_index=True, right_index=True)
        # Rename the columns
        all_data.rename(columns={"Mkt-RF": "mkt_excess"}, inplace=True)
        # Calculate the excess returns
        all_data['port_excess'] = all_data['portfolio'] - all_data['RF']
        print(all_data.tail(20))

        model = smf.formula.ols(formula="port_excess ~ mkt_excess + SMB + HML", data=all_data).fit()
        print(model.summary())

        ret_data.to_csv("out.csv", encoding='utf-8')



