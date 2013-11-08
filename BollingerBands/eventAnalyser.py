'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 23, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Event Profiler Tutorial
'''


import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import csv
import bbands as bb
"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""


def find_events(ls_symbols, df_bbands):
    ''' Finding the event dataframe '''

    print "Finding events and creating market orders:"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_bbands)
    df_events = df_events * np.NAN

    outFile = open("eventOrders1_5.csv",'wb')
    writer = csv.writer(outFile, delimiter=',')

    # Time stamps for the event range
    ldt_timestamps = df_events.index

    len_ts = len(ldt_timestamps)
    for s_sym in ls_symbols:
        if s_sym != 'SPY':
            for i in range(1, len_ts):

                f_bband_today = df_bbands[s_sym].ix[ldt_timestamps[i]]
                f_bband_yest = df_bbands[s_sym].ix[ldt_timestamps[i - 1]]
                f_bband_SPY = df_bbands['SPY'].ix[ldt_timestamps[i]]

                        
                if f_bband_today <= -2.0 and  f_bband_yest >= -2.0 and f_bband_SPY>=1.5:
                    df_events[s_sym].ix[ldt_timestamps[i]] = 1
                    #write buy order
                    writer.writerow([ldt_timestamps[i].year, ldt_timestamps[i].month, ldt_timestamps[i].day, s_sym, "Buy", 100])
                    #write buy order
                    futureDay = i+5
                    if futureDay >= len_ts:
                        futureDay = len_ts-1
                    writer.writerow([ldt_timestamps[futureDay].year, ldt_timestamps[futureDay].month, ldt_timestamps[futureDay].day, s_sym, "Sell", 100])

    outFile.close()
    
    return df_events


if __name__ == '__main__':
    
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')

    #Calculate bollinger bands
    df_bbands = bb.calculateBBands("January 1,2008","December 31, 2009", ls_symbols) 
    df_events = find_events(ls_symbols, df_bbands)
    print "Creating Study"

    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    ldt_timestamps.sort()

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='bbandsevent1_5.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')


