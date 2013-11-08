
# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import dateutil.parser as dtParser
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from math import sqrt
print "Pandas Version", pd.__version__

def calculateBBands(startdate="January 1,2010", enddate="December 31, 2010", ls_symbols = ["GOOG"], lookBack = 20, plot=False):
    
    # Start and End date of the charts
    dt_start = dtParser.parse(startdate)
    #print dt_start
    dt_end=dtParser.parse(enddate)
    #print dt_end

    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    ldt_timestamps.sort()
    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    #define dictionary (relate ls_keys to data columns)
    d_data = dict(zip(ls_keys, ldf_data))

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values

    rolling_mean = pd.rolling_mean(na_price, lookBack)
    rolling_std = pd.rolling_std(na_price, lookBack)
    up_band = rolling_mean + rolling_std
    low_band = rolling_mean - rolling_std

    boll_val = (na_price-rolling_mean)/rolling_std
    

    dt_boll_val = pd.DataFrame(boll_val)
    dt_boll_val.index=ldt_timestamps
    dt_boll_val.columns=ls_symbols

    print dt_boll_val.tail(5)
    
    
    if plot==True:
        fig, axes = plt.subplots(nrows=2)
        # Plotting the plot of daily returns
        plt.clf()
        plt.figure(1)
        plt.subplot(211)
        plt.plot(ldt_timestamps, up_band)  
        plt.plot(ldt_timestamps, na_price)  
        plt.plot(ldt_timestamps, low_band) 
        plt.axhline(y=0, color='r')
        plt.legend(['up','Prices','low'], loc=4)
        plt.ylabel('Rolling Mean')
        plt.xlabel('Dates')

        plt.subplot(212)
        plt.plot(ldt_timestamps, up_band)  
        plt.plot(ldt_timestamps, rolling_mean)  
        plt.plot(ldt_timestamps, low_band) 
        plt.axhline(y=0, color='r')
        plt.legend(['up', 'rolling Mean','low'], loc=4)
        plt.ylabel('BBands')
        plt.xlabel('Dates')
        plt.savefig('bbands.pdf', format='pdf')

    return dt_boll_val
        
#def main():

#       df_boll_val = calculateBBands(ls_symbols=['AAPL','GOOG','IBM','MSFT'])
#       print df_boll_val.loc[dtParser.parse("May 21,2010")+dt.timedelta(hours=16)]
#       print df_boll_val.loc[dtParser.parse("June 23,2010")+dt.timedelta(hours=16)]
#if __name__ == '__main__':
#        main()
