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


def run_script(script_name,symbol ,entry ,RISK , ds ,TP,SL,pip):
    try:
        script_module = importlib.import_module(script_name)
        logger = logging.getLogger(f'{symbol}_{entry}')
        logger.info('entreing execution')
        script_module.Execution(symbol ,entry ,RISK , ds ,TP,SL,pip,logger)
    except ImportError:
        print(f"Failed to import {script_name}.")



def files(script_name,symbol , entry,RISK , ds ,TP,SL,pip):
    df_cols = ['signals','orderid','volume','price_open','TP','SL']
        
    df_entry = pd.DataFrame(columns= df_cols) 
    df_entry.to_csv(f'{symbol}_{entry}_entry_signals.csv',index= False)

    logger = logging.getLogger(f'{symbol}_{entry}')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(f'{symbol}_{entry}_BA_atr.log')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

    
     

def premain():
    
    
    

    # login = 25024739
    # password = 'T52wjqWh@7Rv'
    # server = 'Tickmill-Demo'
    login = 51314848
    password = 'zVQKjwZU'
    server = 'ICMarketsSC-Demo'
    path = r'C:\Program Files\MetaTrader 5\terminal64.exe'
    mt5.initialize( login = login , password = password, server = server)
    #symbol,perrisk = val/100 , qty,TP,SL,TP1,SL1,pipval
    script_args = {
        "GBPUSD_M15_long": ('GBPUSD','long',0.002 , 0.0001,2,3,10),
        "USDCAD_M15_long": ('USDCAD','long',0.002 , 0.0001,2,3,10),
        "USDJPY_M15_long": ('USDJPY','long',0.002 , 0.01,2,3,10),
        "USDJPY_M15_short": ('USDJPY','short',0.002 , 0.01,2,3,10)
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
                            # continue
                        if  (time2 % (3600 *24)  != 0) :  #not 00:00

                            if (time2 % 900  == 0) or (time2 % 900  < 3):
                                #x = 1
                                print('1hour')
                                for script_name, args in script_args.items():
                                    # create_file(script_name)  # Create a file for each script
                                    symbol = args[0]
                                    entry = args[1]
                                    logger = logging.getLogger(f'{symbol}_{entry}')
                                    logger.info(f'processor {symbol},Time = {time1}')
                                    thread = threading.Thread(target=run_script, args=(script_name, *args))
                                    thread.start()

                                for thread in threading.enumerate():
                                    if thread != threading.current_thread():
                                        thread.join()
                                
                                print(symbol)
                                # Execution(symbol,RISK , ds,TP,SL,pip,logger)
                                logger.info(f'processor out {symbol},Time = {time1}')
                            
                        

                        if (time2 % (3600 *24)  == 1200) or (time3 % (3600 *24 )  == 1200):
                            
                                print('1hour')
                                for script_name, args in script_args.items():
                                    # create_file(script_name)  # Create a file for each script
                                    symbol = args[0]
                                    logger = logging.getLogger(f'{symbol}_{entry}')
                                    logger.info(f'processor {symbol},Time = {time1}')
                                    thread = threading.Thread(target=run_script, args=(script_name, *args))
                                    thread.start()

                                for thread in threading.enumerate():
                                    if thread != threading.current_thread():
                                        thread.join()
                                
                                print(symbol)
                                # Execution(symbol,RISK , ds,TP,SL,pip,logger)
                                logger.info(f'processor out {symbol},Time = {time1}')
                        
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
     







    
    






