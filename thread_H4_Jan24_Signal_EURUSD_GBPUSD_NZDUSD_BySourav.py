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
import importlib
import sig_lib as sig

importlib.reload(sig)
from Logging import setup_logger
import math


def run_script(script_name,symbol , RISK , ds ,TP,SL,pip):
    try:
        script_module = importlib.import_module(script_name)
        logger = logging.getLogger(f'{script_name}')
        logger.info('entreing execution')
        script_module.Execution(script_name,symbol , RISK , ds ,TP,SL,pip,logger)
    except ImportError:
        print(f"Failed to import {script_name}.")



def files(script_name,symbol , RISK , ds ,TP,SL,pip):
    df_cols = ['signals','orderid','volume','price_open','TP','SL']
        
    df_entry = pd.DataFrame(columns= df_cols) 
    df_entry.to_csv(f'{script_name}_entry_signals.csv',index= False)
    
    logger = setup_logger(f'{symbol}_BA_H4_AddedBySourav.log')


    
     

def premain():
    
    
    

    # login = 25024739
    # password = 'T52wjqWh@7Rv'
    # server = 'Tickmill-Demo'
    login = 25071028
    password = 'pB+#3#6FS3%j'
    server = 'Tickmill-Demo'
    path = r'C:\Program Files\MetaTrader 5\terminal64.exe'
    mt5.initialize( login = login , password = password, server = server)
    #symbol,perrisk = val/100 , qty,TP,SL,TP1,SL1,pipval
    # script_name,symbol , RISK , ds ,TP,SL,pip
    script_args = {
        "EURUSD_Short_H4" : ('EURUSD' , 0.002 , 0.001 , 2 , 3 , 10),
        "GBPUSD_trail_Short_H4" : ('GBPUSD' , 0.002 , 0.001 , 2 , 3 , 10) ,
        "NZDUSD_trail_Short_H4" : ('NZDUSD' , 0.002 , 0.001 , 2 , 3 , 10) 
    }

    for script_name, args in script_args.items():
        symbol = args[0]
        
        files(script_name,*args)
    
    
    # symbols = [['GBPUSD',0.01 , 0.0001,2,3,10],['US500',0.01 , 0.01,2,3,0.01]  ]
        
    if mt5.initialize(login = login , password = password, server = server):
        print(f'Script Started for {symbol}')
        while True:
            if (datetime.now().weekday()) != 5 and    \
                        (datetime.now().weekday()) != 6:
                if mt5.initialize():
                
                    if ((datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)).weekday()) != 5 and                  ((datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)).weekday()) != 6:
            
                        try:
                            time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                            time2 = mt5.symbol_info_tick(symbol).time
                            time3 = mt5.symbol_info_tick(symbol).time


                        except AttributeError:
                            time.sleep(20)
                            
                            
                        '''For all 4 Hour Timeframe apart from 0th Hour'''
                        if  (time2 % (3600 *24)  != 0) :  #not 00:00

                            if (time2 % (3600*4)  == 0) or (time2 % (3600*4)  < 3):
                                    for script_name, args in script_args.items():
                                        # create_file(script_name)  # Create a file for each script
                                        symbol = args[0]
                                        logger = setup_logger(f'{symbol}_BA_H4_AddedBySourav.log')
                                        logger.debug(f'AT the next Hour InTime -- SymbolName : {symbol} BrokerTime : {time1}')
                                        thread = threading.Thread(target=run_script, args=(script_name, *args))
                                        thread.start()

                                    for thread in threading.enumerate():
                                        if thread != threading.current_thread():
                                            thread.join()
                                    
                                    logger.debug(f'AT the next Hour OutTime -- SymbolName : {symbol} BrokerTime : {time1}')
                        
                        
                        '''For the Next Day 0th Hour candle Execution Code'''
                        if  (time1.hour == 0)  :
                                while True:
                                    time2 = mt5.symbol_info_tick(symbol).time
                                    time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                    if (time2 % (3600*4)  < 50) or (time2 % (3600 *4)  < 1200) or (time2 % (3600 *4)  < 600) :
                                    #x = 1
                                    # print('1hour')
                                        for script_name, args in script_args.items():
                                            # create_file(script_name)  # Create a file for each script
                                            symbol = args[0]
                                            logger = setup_logger(f'{symbol}_BA_H4_AddedBySourav.log')
                                            logger.debug(f'AT the next Hour InTime -- SymbolName : {symbol} BrokerTime : {time1}')
                                            thread = threading.Thread(target=run_script, args=(script_name, *args))
                                            thread.start()

                                        for thread in threading.enumerate():
                                            if thread != threading.current_thread():
                                                thread.join()
                                        break
                                    elif time1.hour >= 1:
                                         break

                        
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



if __name__ == "__main__":
    print('step1')
    premain()
     







    
    






