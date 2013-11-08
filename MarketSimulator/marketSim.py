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

print "Pandas Version", pd.__version__

def marketSim(cash, inputFile, outputFile):
    reader = csv.reader(open(inputFile, "rU"), delimiter=',')
    ls_symbols=list()
    dates=list()
    for row in reader:
        dateString = row[0]+'/'+row[1]+'/'+row[2]
        date = dtParser.parse(dateString)
        dates.append(date)
        ls_symbols.append(row[3])
    
    #remove duplicate dates and symbols
    dates=list(set(dates))
    dates.sort()

    ls_symbols=list(set(ls_symbols))
    ls_symbols.sort()

    #get first and last days.
    dt_start = dates[0]
    dt_end = dates[len(dates)-1] + dt.timedelta(days=1)

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    dt_timeofday=dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')
    
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

    dt_actualClose = d_data['close']

    dtTrades = pd.DataFrame(index=dt_actualClose.index, columns=ls_symbols)
    dtTrades = dtTrades.fillna(0)
    #print(dtTrades)

    #create trade matrix
    reader = csv.reader(open(inputFile, "rU"), delimiter=',')
    for row in reader:
        dateString = row[0]+'/'+row[1]+'/'+row[2]
        date = dtParser.parse(dateString)+dt_timeofday
        symbol=row[3]
        action=row[4]
        shares=int(float(row[5]))
        if action=="Buy":
            dtTrades[symbol].loc[date]+=shares
        elif action=="Sell":
            dtTrades[symbol].loc[date]-=shares

                        
    df_holdings = copy.deepcopy(dtTrades)
    #calculate cumulative sum per symbol to calculate daily holdings
    for symbol in ls_symbols:
       df_holdings[symbol] =  np.cumsum(df_holdings[symbol])


    s_cash = pd.Series(np.zeros(1), dtTrades.index)
    s_value = pd.Series(np.zeros(1), dtTrades.index)
    s_totalValue = pd.Series(np.zeros(1), dtTrades.index)
    for date in dtTrades.index:
        value=0
        #actual close of specific symbol at specific date
        for symbol in ls_symbols:
            actual_close=dt_actualClose[symbol].loc[date]
            cashAmount = dtTrades[symbol].loc[date]
            numberofShares = df_holdings[symbol].loc[date]
            #calculate cash per spent/gained per symbol
            if cashAmount!=0:
                cash = cash - (cashAmount*actual_close)
            if numberofShares!=0:
                value = value + (numberofShares*actual_close)
            #calculate value per symbol
        #update available cash for specific date        
        s_cash.loc[date]=cash
        #update total holdings value for specific date
        s_value.loc[date]=value
        s_totalValue.loc[date]=cash+value

    
    #print df_holdings
    #print dtTrades
    writer = csv.writer(open(outputFile,'wb'), delimiter=',')
    for date in s_totalValue.index:
        row_to_enter = [date.isoformat(), str(s_totalValue.loc[date])]
        writer.writerow(row_to_enter)


        
def main(argv):

    cash = int(float(argv[0]))
    inputFile = argv[1]
    outputFile = argv[2]
    
    marketSim(cash, inputFile, outputFile)
        
if __name__ == '__main__':
        main(sys.argv[1:])
