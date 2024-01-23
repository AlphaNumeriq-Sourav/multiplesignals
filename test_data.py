import threading
import importlib

import time


import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
import MetaTrader5 as mt5
import time
from multiprocessing import pool , Process
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
import schedule

import pandas_ta as ta


import warnings
import logging
warnings.filterwarnings("ignore")
import sig_lib as sig
import math


def Execution(symbol , PerCentageRisk , SL_TpRatio ,TP,SL,pipval,logger):
    #print(symbol)
    """
        low[0] > open[9]; low[2] > high[6]; open[5] > high[9]; low[6] > open[9]; low[0] <= low[1]; SMA(close;8)[0] > SMA(close;8)[3]
        
        high[3] > close[4]; open[1] <= close[4]; close[8] <= open[9]; open[7] <= close[9]; low[0] < SMA(close;8)[0]; EMA(close;8)[0] > EMA(close;8)[3]
        open[0] > low[2]; open[0] > close[8]; low[2] > high[6]; high[5] > close[6]; close[6] > high[9]; ValueOpen(5)[1] > ValueLow(5)[2]
        low[0] > open[7]; low[3] > open[4]; low[4] > open[5]; open[0] < HLMedian[0]; ValueLow(5)[2] > ValueLow(5)[4]; ValueOpen(5)[0] <= ValueHigh(5)[1]
    
    """
    time_hr = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=5.5))

    # df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_H1 , 0 , 2700))

    logger.info(f'Running Event Loop for {symbol} at {datetime.now()}')
    logger.info(f'Running Event Loop for {symbol} at {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
    for i in range(1):
        try: 
            df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_M5 , 0 , 2700))
            df['time']= df['time'].map(lambda Date : datetime.fromtimestamp(Date) -  timedelta(hours= 3))
            time_hr = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
            print('data')
            print(time_hr)
            print(df)
            logger.info(f"time: {time_hr} lastindex : {df.iloc[-1]['time'].hour} ")
            if  (df.iloc[-1]['time'].hour == time_hr.hour) and (df.iloc[-1]['time'].minute == time_hr.minute):

                print(df)
                
            else:
                df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_M15 , 0 , 2700))
                df['time']= df['time'].map(lambda Date : datetime.fromtimestamp(Date) -  timedelta(hours= 3))
                print(df)
                logger.info(f"  False time: {time_hr} lastindex : {df.iloc[-1]['time'].hour} ")
            

            df['sma_8'] = sig.SMA(df, 8)
            df['ema_8'] = sig.EMA(df, 8)
            df['ValueOpen'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'open')
            df['ValueLow'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'low')
            df['ValueHigh'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'high')
            df['HLMedian'] = sig.HLMedian(df)
            df['ATR'] = sig.AvgTrueRange(df,7)


            

        except AttributeError:
            if mt5.initialize():
                logger.info(f'connected {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            else:
                logger.info(f' not connected {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
                # login = 	11044024
                # password = 'p9L8VKnL'
                # server = 'ICMarketsSC-MT5-4'

                # mt5.initialize(login = login , password = password, server = server)
                #time.sleep(20)
                logger.info(f'connected ,{mt5.initialize()} , {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            continue
        break
    time.sleep(20)
    return
    
    
                    


# In[19]:


def premain(symbol , RISK , ds ,TP,SL,pip):
    
    
    df_cols = ['signals','orderid','volume','price_open','TP','SL']
        
    # df_entry = pd.DataFrame(columns= df_cols) 
    # df_entry.to_csv(f'{symbol}_entry_signals.csv',index= False)

    login = 51313012
    password = 'JqKKQHdc'
    server = 'ICMarketsSC-Demo'
    # path = r'C:\Program Files\MetaTrader 5\terminal64.exe'
    path = r'C:\Program Files\MetaTrader 5 IC Markets (SC)\terminal64.exe'

    logger = logging.getLogger(f'{symbol}')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(f'{symbol}_BA_atr.log')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

        

    if mt5.initialize(path = path,login = login , password = password, server = server):
        print(f'Script Started for {symbol}')
        while True:
            if (datetime.now().weekday()) != 5 and    \
                        (datetime.now().weekday()) != 6:
                if mt5.initialize():
                
                
                    # print("Connected")
                    if ((datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)).weekday()) != 5 and                  ((datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)).weekday()) != 6:
            
                    
                    #print('step3')
                    

                        try:
                            time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                            time2 = mt5.symbol_info_tick(symbol).time
                            time3 = mt5.symbol_info_tick(symbol).time


                        except AttributeError:
                            time.sleep(20)
                            # continue
                        
                        

                        if  (time2 % (3600 *24)  != 0) :  #not 00:00

                            if (time2 % 300  == 0) or (time2 % 300  < 3):
                                #x = 1
                                logger.info(f'processor {symbol},Time = {time1}')
                                print(symbol)
                                Execution(symbol,RISK , ds,TP,SL,pip,logger)
                                logger.info(f'processor out {symbol},Time = {time1}')
                            
                        

                        if (time2 % (3600 *24)  == 1200) or (time3 % (3600 *24 )  == 1200):
                            
                            logger.info(f'processor {symbol},Time = {time1}')
                            print(symbol)
                            Execution(symbol,RISK , ds,TP,SL,pip,logger)
                            logger.info(f'processor out {symbol},Time = {time1}')
                            #time.sleep(60)
                        
                else:
                    print("Not Connected")
                    
                    time1 = (datetime.now())
                    print(time1)
                    with open(f'NotInitial.txt' , 'a') as file:
                                file.write(f'\n symbol = {symbol},')
                                
                                file.write(f'Time = {time1}')
                    file.close
                    logger.info(f'not connected {symbol},Time = {time1}')
                    cd = mt5.initialize(login = login , password = password, server = server)
                    #print(cd)
                    logger.info(f'connected {cd},Time = {datetime.now()}')




def main():
    #symbol,perrisk = val/100 , qty,TP,SL,TP1,SL1,pipval
    symbols = [['EURUSD',0.01 , 0.0001,2,3,10],['AUDUSD',0.01 , 0.0001,2,3,10] ]
    
    p1 = Process(target = premain, args= symbols[0])
    p2 = Process(target = premain, args= symbols[1])
    # p3 = Process(target =premain , args= symbols[2])
    # p4 = Process(target =premain , args= symbols[3])
    

    p1.start()
    p2.start()
    # p3.start()
    # # p4.start()

    p1.join()
    p2.join()
    # p3.join()
    # p4.join()



if __name__ == '__main__':
    print('step1')
    main()


# In[ ]:




