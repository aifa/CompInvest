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
import csv
import copy
import sys, getopt
from math import sqrt

print "Pandas Version", pd.__version__

def analyze(inputFile='./values.csv', benchMarkSymbol='$SPX'):
    reader = csv.reader(open(inputFile, "rU"), delimiter=',')
    dailyValue=list()
    dates=list()
    for row in reader:
        dateString = row[0]
        date = dtParser.parse(dateString)
        dates.append(date)
        dailyValue.append(float(row[1]))

    dates.sort()

    #get first and last days.
    dt_start = dates[0]
    dt_end = dates[len(dates)-1]
    
    benchReturns = getBenchamrkReturns(dt_start, dt_end, benchMarkSymbol)

    #calculate daily returns of portfolio
    na_values = np.array(dailyValue, dtype=np.float64)
 
    na_normalised_values=(na_values/na_values[0])

    tsu.returnize0(na_normalised_values)

    dailyReturnAverage = np.average(na_normalised_values)
    stdev = np.std(na_normalised_values, dtype=np.float64)
    sharpe = sqrt(252)*np.mean(na_normalised_values)/stdev
    return_total = np.cumprod(na_normalised_values+1)
    cumReturn = return_total[return_total.size-1]/return_total[0]
    
    fund=dailyValue[0]
    #calculate fund value with benchmark returns
    s_benchMarkValues = pd.Series(np.zeros(1), dates)
    s_returns = pd.Series(np.zeros(1), dates)
    for date in dates:
        b_date = date;
        #get benchmark return for that date
        b_return = benchReturns.loc[b_date]
        s_returns.loc[date]= b_return
        if b_return!=0:
            fund += fund*b_return
        s_benchMarkValues.loc[date] = fund

    dailyReturnAverage_bc = np.average(benchReturns)
    stdev_bc = benchReturns.std(ddof=0)
    sharpe_bc = sqrt(252)*np.mean(benchReturns)/stdev_bc

    return_total_bc = np.cumprod(benchReturns+1)
    cumReturn_bc = (return_total_bc[return_total_bc.size-1])/(return_total_bc[0])
    
    
    print "The final value of the portfolio using the sample file is :" + str(dates[len(dates)-1]) + ": " +  str(dailyValue[len(dailyValue)-1])
    print "Details of the Performance of the portfolio :"
    print "Data Range :  "+str(dates[0]) +" to "+  str(dates[len(dates)-1])

    print "Sharpe Ratio of Fund :" + "%.15f" % sharpe
    print "Sharpe Ratio of "+ benchMarkSymbol +":" + str(sharpe_bc)

    print "Total Return of Fund :" + str(cumReturn)
    print "Total Return of "+ benchMarkSymbol +":" + str(cumReturn_bc)

    print "Stdev of Fund :" + str(stdev)
    print "stdev of "+ benchMarkSymbol +":" + str(stdev_bc)

    print "Avg daily Return of Fund :" + str(dailyReturnAverage)
    print "Avg daily Return of "+ benchMarkSymbol +":" + str(dailyReturnAverage_bc)

    # Plotting the plot of daily returns
    plt.clf()
    plt.plot(s_benchMarkValues.index, s_benchMarkValues.values)  # benchmark 
    plt.plot(dates, dailyValue)  # portfolio returns
    plt.axhline(y=0, color='r')
    plt.legend([benchMarkSymbol, inputFile], loc=4)
    plt.ylabel('Fund Value')
    plt.xlabel('Date')
    plt.savefig(inputFile+'Plot.pdf', format='pdf')

def getBenchamrkReturns(dt_start, dt_end, symbol):
    # List of symbols
    ls_symbols = [symbol]

    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')
    
    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['close']

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
    print d_data
    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values
    print d_data['close'].index
    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]

    # Copy the normalized prices to a new ndarry to find returns.
    na_rets = na_normalized_price.copy()

    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_rets)

    s_returns = pd.Series(na_rets[0:,0], d_data['close'].index)
    
    return (s_returns)


def main(argv):

    inputFile = argv[0]
    benchMarkSymbol = argv[1]
    
    analyze(inputFile, benchMarkSymbol)
        
if __name__ == '__main__':
        main(sys.argv[1:])
