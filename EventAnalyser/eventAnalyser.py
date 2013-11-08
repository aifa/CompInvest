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


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_actualClose = d_data['actual_close']

    print "Finding events and creating market orders:"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_actualClose)
    df_events = df_events * np.NAN

    outFile = open("eventOrders.csv",'wb')
    writer = csv.writer(outFile, delimiter=',')

    # Time stamps for the event range
    ldt_timestamps = df_actualClose.index
    len_ts = len(ldt_timestamps)
    for s_sym in ls_symbols:
        for i in range(1, len_ts):
            # Calculating the returns for this timestamp
            f_symprice_today = df_actualClose[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_actualClose[s_sym].ix[ldt_timestamps[i - 1]]

            # Event if the symbol actual close price the specific day is below $5.0,
            # and the actual close price the day before was equal or above 5.0
                    
            if f_symprice_today < 10.0 and  f_symprice_yest >= 10.0:
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
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    ldt_timestamps.sort()
    
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = find_events(ls_symbols, d_data)
    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='sp5002008_7event.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')


