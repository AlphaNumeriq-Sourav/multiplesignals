#!/usr/bin/env python
# coding: utf-8

# In[2]:


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



# In[3]:



# function to send a market order



# In[3]:



# function to send a market order
def market_order(symbol, volume, order_type,comment,magic, **kwargs):
    #print(symbol)
    tick = mt5.symbol_info_tick(symbol)

    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_dict[order_type],
        "price": price_dict[order_type],
        "deviation": 2,
        "magic": magic,
        "comment":comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    order_result = mt5.order_send(request)
    #print(order_result)

    return order_result



# In[67]:


# function to close an order base don ticket id
def close_order(ticket):
    positions = mt5.positions_get()

    for pos in positions:
        tick = mt5.symbol_info_tick(pos.symbol)
        type_dict = {0: 1, 1: 0}  # 0 represents buy, 1 represents sell - inverting order_type to close the position
        price_dict = {0: tick.bid, 1: tick.ask}

        if pos.ticket == ticket:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": pos.ticket,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": type_dict[pos.type],
                "price": price_dict[pos.type],
                "deviation": 2,
                
                
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            order_result = mt5.order_send(request)
            #print(order_result)

            return order_result

    return 'Ticket does not exist'





# -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------
# Function to Get H4 Forex Signals for NZDUSD 
# Signal 1 = ADX(5)[4] > ADX(3)[1]; ADX(13)[4] > ADX(9)[10]; ADX(14)[5] > ADX(19)[3]; ADX(18)[6] > ADX(17)[9]; ADX(7)[7] > ADX(19)[7]; ADX(2)[9] > ADX(20)[4]
# -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------


def entry_signal1(data,choice,index):
    index = index
    variable = None
    
    if choice == 1:
        '''
        ADX(5)[4] > ADX(3)[1]; ADX(13)[4] > ADX(9)[10]; ADX(14)[5] > ADX(19)[3]; ADX(18)[6] > ADX(17)[9]; ADX(7)[7] > ADX(19)[7]; ADX(2)[9] > ADX(20)[4]
        '''
        condition = (data.iloc[index-4]['ADX_5'] > data.iloc[index-1]['ADX_3']) and \
                    (data.iloc[index-4]['ADX_13'] > data.iloc[index-10]['ADX_9']) and \
                    (data.iloc[index-5]['ADX_14'] > data.iloc[index-3]['ADX_19']) and \
                    (data.iloc[index-6]['ADX_18'] > data.iloc[index-9]['ADX_17']) and \
                    (data.iloc[index-7]['ADX_7'] > data.iloc[index-7]['ADX_19']) and \
                    (data.iloc[index-9]['ADX_2'] > data.iloc[index-4]['ADX_20']) 
        variable = "Trail"
    
    

                    
    else:
        condition =  False

    if condition:
         return True,variable
    else:
         return False,variable





















# -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------
# Function to Execute the Trades of NZDUSD when a New signal comes from signal 1 and also to Exit the Trades Also
# -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------



def Execution(script_name,symbol , PerCentageRisk , SL_TpRatio ,TP,SL,pipval,logger):

    time_hr = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))

    df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_H4 , 0 , 2700))

    logger.info(f'Running Event Loop for {symbol} at {datetime.now()} for NZDUSD Short Modified by Sourav')
    logger.info(f'Running Event Loop for {symbol} at {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
    for i in range(2):
        try: 
            df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_H4 , 0 , 2700))
            df['time']= df['time'].map(lambda Date : datetime.fromtimestamp(Date) -  timedelta(hours= 3))

            time_hr = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
            logger.info(f"time: {time_hr} lastindex : {df.iloc[-1]['time']} ")

            for i in range(5):
                if  (df.iloc[-1]['time'].hour == time_hr.hour) or (df.iloc[-1]['time'].hour > time_hr.hour) or ((df.iloc[-1]['time'].hour == 0) and (time_hr.hour >=23)):
                     index = -2
                     break
                else:
                    df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_H4, 0 , 2700))
                    index = -1
                    df['time']= df['time'].map(lambda Date : datetime.fromtimestamp(Date) -  timedelta(hours= 3))
                    time_false = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                    logger.info(f"  False time: {time_hr} lastindex : {df.iloc[-1]['time']}, time now: {time_false} ")
                    if  (df.iloc[-1]['time'].hour == time_hr.hour) or (df.iloc[-1]['time'].hour > time_hr.hour)or ((df.iloc[-1]['time'].hour == 0) and (time_hr.hour >=23)):
                     index = -2

            
            
          
            df['ADX_2'] = sig.ADX(data , 2)
            df['ADX_3'] = sig.ADX(data , 3)
            df['ADX_5'] = sig.ADX(data , 5 )
            df['ADX_7'] = sig.ADX(data , 7 )
            df['ADX_9'] = sig.ADX(data , 9 )
            df['ADX_13'] = sig.ADX(data , 13 )
            df['ADX_14'] = sig.ADX(data , 14 )
            df['ADX_17'] = sig.ADX(data , 17 )
            df['ADX_18'] = sig.ADX(data , 18 )
            df['ADX_19'] = sig.ADX(data , 19 )
            df['ADX_20'] = sig.ADX(data , 20)
            
            
        
           

        except AttributeError:
            if mt5.initialize():
                logger.info(f'connected {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            else:
                logger.info(f' not connected {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
                login = 25071028
                password = 'pB+#3#6FS3%j'
                server = 'Tickmill-Demo'

                mt5.initialize(login = login , password = password, server = server)
                
                
                logger.info(f'connected ,{mt5.initialize()} , {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            continue
        break
    
    
    
    
    
    df.to_csv(f'{script_name}_dataframe')
    df_entry = pd.read_csv(f'{script_name}_entry_signals.csv')
    
    if 'TP1' not in df_entry.columns:
         df_entry['TP1'] = None
    if 'flag' not in df_entry.columns:
         df_entry['flag'] = None
    for i in range(1):
            # Short Condition

            if df_entry.empty:
                for i in range(1,2):
                    
                    
                    signal = f'signal{i}'
                    condition, variable = entry_signal1(df,i,index)

                    if condition:
                        # Got Indication Candle
                       
                        if variable == 'Trail':
                            flag = 0
                            time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                            logger.info(f'Got Short Indication Candle for {signal} {symbol} at {time1}')
                            print(f'Got Short Indication Candle  for signal  {symbol} at {time1}')
                            # index = -2
                            data = df.copy()
                            logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                            SL_dis = 50
                            LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*50),2)
                            
                            order= market_order(symbol , LotSize,'sell',signal,1000+i )
                            tick = mt5.symbol_info_tick(symbol)
                            Price = tick.ask
                            
                            ATR = df.iloc[index]['ATR']
                            StopLoss = Price + SL_dis * SL_TpRatio
                            TP_val = Price - 30 * SL_TpRatio
                            order_id = order.order
                            order_price = order.price
                            print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                            logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}  {flag}')
                            df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss,0,flag]
                        
                        
                        else:
                            logger.info(f"No entry for {signal}  close : {df.iloc[index]['close']} {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}")  
                    
                    
                  
            else:
                column_name = 'signals'
                for i in range(1,2):
                    
                    signal = f'signal{i}'
                    if df_entry[column_name].eq(i).any():
                        logger.info(f"The {signal} entry exists ")      

                    else:
                        condition, variable = entry_signal1(df,i,index)

                        if condition:
                            # Got Indication Candle
                           
                            if variable == 'Trail':
                                flag = 0
                                time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                                logger.info(f'Got Short Indication Candle for {signal} {symbol} at {time1}')
                                print(f'Got Short Indication Candle  for signal  {symbol} at {time1}')
                                # index = -2
                                data = df.copy()
                                logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                                SL_dis = 50
                                LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*50),2)
                                
                                order= market_order(symbol , LotSize,'sell',signal,1000+i )
                                tick = mt5.symbol_info_tick(symbol)
                                Price = tick.ask
                                
                                ATR = df.iloc[index]['ATR']
                                StopLoss = Price + SL_dis * SL_TpRatio
                                TP_val = Price - 30 * SL_TpRatio
                                order_id = order.order
                                order_price = order.price
                                print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                                logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}  {flag}')
                                df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss,0,flag]
                    
                        else:
                        
                            logger.info(f"No entry for {signal}  close : {df.iloc[index]['close']} {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}")  
                    
                            
            # -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------
            # Logic to Exit the Short Trades if hits SL and also the trailing Part
            # -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------
            if not df_entry.empty:
                rows_to_delete = []
                print('checkfor')
                               
                while True:
                    if time_hr.minute  ==  0:
                            dd_time = 4*60*60 - 20
                    elif time_hr.minute >= 19:
                            dd_time = 4*60*60 - 21*60 - 10
                    elif time_hr.minute >= 10:
                            dd_time = 4*60*60 - 15*60
                    elif time_hr.minute >= 5:
                            dd_time = 4*60*60 - 12*60
                    elif time_hr.minute >= 2:
                            dd_time = 4*60*60 - 5*60
                    
                    else:
                            dd_time = 4*60*60 - 70
                            
                    
                    if (  (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)) - time_hr).seconds < dd_time:

                        if (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)).weekday() !=5 and (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)).weekday() !=6:
                                
                                # SL , TP check
                                
                            Price = mt5.symbol_info_tick(symbol).bid
                            Price1 = mt5.symbol_info_tick(symbol).ask
                                    # SL Hit
                            for index, row in df_entry.iterrows():  
                                try:
                                    if index not in rows_to_delete:
                                        
                                            if Price >= row['SL']:
                                                    time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                    print(f'SL Hit at{time_s} ')
                                                    close = close_order(row['orderid'])
                                                    logger.info(f"SL hit long {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']},{close.comment}  ")
                                                    if close.comment == 'Request executed':

                                                        rows_to_delete.append(index)
                                            elif (Price <= row['TP']) and (row['flag'] == 0):
                                                time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                row['SL'] = row['price_open'] - 1*(SL_TpRatio)
                                                row['TP'] = row['TP'] - 1*(SL_TpRatio)
                                                row['flag'] = 1
                                                logger.info(f"Trail 1  hit long {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']}  ")
                                            elif (Price <= row['TP']) and (row['flag'] == 1):
                                                time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                row['SL'] = row['SL'] - 1*(SL_TpRatio)
                                                row['TP'] = row['TP'] - 1*(SL_TpRatio)
                                                logger.info(f"Trail next  hit long {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']} ")

                                                

                                except:
                                     continue

                                        
                    else:
                        df_entry = df_entry.drop(rows_to_delete)
                        df_entry.reset_index(inplace= True)
                        df_entry.drop('index', axis=1, inplace=True)
                        df_entry.to_csv(f'{script_name}_entry_signals.csv',index = False)
                        logger.info(f'fn out by time {dd_time} {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                        return
            else:
                df_entry.to_csv(f'{script_name}_entry_signals.csv',index = False)
                logger.info(f'fn out no current running entry {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                time.sleep(20)
                return
                        
                                        
                                        


                            



if __name__ == '__main__':
    print('step1')
    Execution()






