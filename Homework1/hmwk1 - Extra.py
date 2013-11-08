
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

def simulate (startdate="January 1,2006", enddate="December 31, 2010", ls_symbols=["AAPL", "GLD", "GOOG", "$SPX", "XOM"], allocations=[0.2,0.3,0.4,0.1]):

    dt_start = dtParser.parse(startdate)
    #print dt_start
    dt_end=dtParser.parse(enddate)
    #print dt_end
    dt_timeofday=dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo')

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    #print ls_symbols
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

    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]
    
    # Copy the normalized prices to a new ndarry to find returns.
    na_rets = na_normalized_price.copy()
    
    na_portrets = np.sum(na_rets * allocations, axis=1)

    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_portrets)
    
    na_port_total = np.cumprod(na_portrets+1)
    
    dailyReturnAverage = np.average(na_portrets)
    stdev = np.std(na_portrets)
    sharpe = sqrt(252)*np.mean(na_portrets)/stdev
    cumReturn = na_port_total[na_port_total.size-1]/na_port_total[0]

    return (sharpe,stdev,dailyReturnAverage,cumReturn, na_port_total)

def getSPYReturns(startdate="January 1,2006", enddate="December 31, 2010"):
    # List of symbols
    ls_symbols = ["SPY"]

    # Start and End date of the charts
    dt_start = dtParser.parse(startdate)
    #print dt_start
    dt_end=dtParser.parse(enddate)
    #print dt_end

    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

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

       # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]

        # Copy the normalized prices to a new ndarry to find returns.
    na_rets = na_normalized_price.copy()

    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_rets)

    return (ldt_timestamps,na_rets+1)

    

def optimiser(startdate="January 1,2006", enddate="December 31, 2010", ls_symbols=["AAPL", "GLD", "GOOG", "$SPX"]):
    #array that contains all possible allocations of a single symbol
    stepArray = np.arange(0.0,1.1,0.1)
    #total number of symbols
    numberOfSymbols=len(ls_symbols)
    #createan array that contains all possible allocations for all symbols
    comboArray = np.zeros((numberOfSymbols, stepArray.size))
    comboArray[:,:] = stepArray.copy()
    #array that will contain alvalid results
    resultAllocations=np.zeros(numberOfSymbols)
    resultSimulate=np.zeros(4)

    spyReturns = getSPYReturns(startdate,enddate)
    returns=np.zeros(len(spyReturns[0]))
    #generate all possible combinations and filter the valid ones (sum=1.0)
    for row1 in comboArray[0,:]:
        for row2 in comboArray[1,:]:
            for row3 in comboArray[2,:]:
                for row4 in comboArray[3,:]:
                    if (row1+row2+row3+row4==1.0):#found a valid comination
                        allocations=[row1, row2, row3, row4]
                        resultAllocations = np.vstack([resultAllocations, allocations])
                        result = simulate(startdate, enddate, ls_symbols, allocations)
                        resultSimulate = np.vstack([resultSimulate, result[0:4]])
                        returns = np.vstack([returns, result[4]])
    rowOfMax = np.argmax(resultSimulate[:,0])
   

        # Plotting the plot of daily returns
    plt.clf()
    plt.plot(spyReturns[0], spyReturns[1])  # SPY 
    plt.plot(spyReturns[0], returns[rowOfMax,:])  # portfolio returns
    plt.axhline(y=0, color='r')
    plt.legend(['SPY', 'portfolio'])
    plt.ylabel('Daily Returns')
    plt.xlabel('Date')
    plt.savefig('compare.pdf', format='pdf')
    
    return (resultAllocations[rowOfMax,:],resultSimulate[rowOfMax,:]) 
                        
            
def main():
     #   print simulate("January 1,2010", "December 31, 2010", ["AXP", "HPQ", "IBM", "HNZ"], [0.0, 0.0, 0.0, 1.0])
     #   print simulate("January 1,2011", "December 31, 2011", ["AAPL", "GLD", "GOOG", "XOM"], [0.4, 0.4, 0.0, 0.2])
     #   print optimiser("January 1,2010", "December 31, 2010", ["AXP", "HPQ", "IBM", "HNZ"])
     #   print optimiser("January 1,2011", "December 31, 2011", ["AAPL", "GLD", "GOOG", "XOM"])
         print optimiser("January 1,2011", "December 31, 2011", ["BRCM", "TXN", "AMD", "ADI"])
        
if __name__ == '__main__':
        main()
