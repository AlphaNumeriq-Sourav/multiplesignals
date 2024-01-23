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
import sig_lib as sig


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


# In[17]:
def entry_signal1(data,choice):
    
    index = -2
    if choice == 1:
        """
 open[1] <= low[5]; high[3] <= low[7]; ValueOpen(5)[1] > ValueLow(5)[4]; Stochastics(3)[0] <= 20; EMA(close;5)[0] < EMA(close;5)[2]; EMA(close;100)[0] > EMA(close;100)[2]
 """         
        return (data.iloc[index-1]['open'] <= data.iloc[index-5]['low']) and (data.iloc[index - 3]['high'] <= data.iloc[index - 7]['low']) \
            and (data.iloc[index-1]['ValueOpen'] > data.iloc[index - 4]['ValueLow'] )and (data.iloc[index]['stoch_3'] <= 20 )  \
        and (data.iloc[index]['ema_5'] <= data.iloc[index-2]['ema_5'])  and (data.iloc[index]['ema_100'] > data.iloc[index-2]['ema_100']) 
    elif choice == 2:
        """
                
  high[0] > close[8]; low[1] > high[5]; low[7] > low[9]; high[8] > open[9]; high[4] <= high[5]; close[0] >= highest(close;100)[0]
      
                """
        index = -2
        return (data.iloc[index]['high'] > data.iloc[index - 8]['close']) and (data.iloc[index-5 ]['high'] < data.iloc[index - 1]['low']) and (data.iloc[index-7]['low'] > data.iloc[index - 9]['low']) \
        and (data.iloc[index-8]['high'] > data.iloc[index - 9]['open']) and (data.iloc[index-4]['high'] <= data.iloc[index-5]['high']) and (data.iloc[index]['close'] >= data.iloc[index ]['high_close'])

    elif choice == 3:
        """
                    
 high[3] > close[8]; open[4] > open[5]; open[0] <= low[3]; open[1] <= low[2]; open[4] <= close[5]; rateOfChange(close;3)[0] < 0         
         """
        index = -2
        return (data.iloc[index-3]['high'] > data.iloc[index - 8]['close']) and (data.iloc[index-4 ]['open'] > data.iloc[index - 5]['open']) and (data.iloc[index]['open'] <= data.iloc[index - 3]['low']) \
        and (data.iloc[index-1]['open'] <= data.iloc[index - 2]['low'] ) and (data.iloc[index-4]['open'] <= data.iloc[index-5]['close']) and (data.iloc[index]['roc_3'] <= 0)
    elif choice == 4:
        
        """
 low[2] > close[3]; low[4] > close[6]; open[0] > EMA(close;200)[0]; low[0] > EMA(close;100)[0]; rsi(close;14)[0] >= 20; EMA(close;200)[0] > EMA(close;200)[2]        """
        index = -2
        return (data.iloc[index-2]['low'] > data.iloc[index-3]['close']) and (data.iloc[index-4]['low'] > data.iloc[index-6]['close']) and (data.iloc[index]['open'] > data.iloc[index]['ema_200'])\
        and (data.iloc[index]['low'] > data.iloc[index]['ema_100']) and (data.iloc[index]['rsi_14'] >= 20) and (data.iloc[index]['ema_200'] > data.iloc[index-2]['ema_200'])
    
    # elif choice == 5:
        
    #     """
    #     high[0] <= high[1]; ValueLow(5)[0] > ValueLow(5)[4]; ValueLow(5)[0] > ValueLow(5)[1]; close[0] crosses below SMA(close;5)[0]; SMA(close;100)[0] < SMA(close;100)[4]; CompositeSMA(8;20;50;200)[0] <= CompositeSMA(8;20;50;200)[4]        
    #     """
    #     index = -2
    #     return (data.iloc[index]['high'] <= data.iloc[index-1]['high']) and (data.iloc[index]['ValueLow'] > data.iloc[index-4]['ValueLow']) and (data.iloc[index]['ValueLow'] > data.iloc[index-1]['ValueLow'])\
    #     ((data.iloc[index]['close'] <= data.iloc[index]['sma_5']) and (data.iloc[index-1]['close'] > data.iloc[index-1]['sma_5'])) and (data.iloc[index]['sma_100'] < data.iloc[index-4]['sma_100'])\
    #           and (data.iloc[index]['composite_sma'] <= data.iloc[index-4]['composite_sma'])
    # elif choice == 6:
        
    #     """
    #     low[2] > low[3]; high[1] <= open[9]; ValueClose(5)[2] <= ValueOpen(5)[5]; range[0] >= highest(range;5)[0]; CCI(20)[0] <= CCI(20)[1]; CompositeEMA(8;20;50;200)[0] <= CompositeEMA(8;20;50;200)[3]        
    #     """
    #     index = -2
    #     return (data.iloc[index-2]['low'] > data.iloc[index-3]['low']) and (data.iloc[index-1]['high'] <= data.iloc[index-9]['open']) and (data.iloc[index-2]['ValueClose'] <= data.iloc[index-5]['ValueOpen'])\
    #     (data.iloc[index]['range'] >= data.iloc[index]['high_range']) and (data.iloc[index]['CCI'] <= data.iloc[index-1]['CCI']) and (data.iloc[index]['composite_ema'] <= data.iloc[index-3]['composite_ema'])
    
    
    else:
         return False

def orders():
     pass


def Execution(symbol ,entry ,PerCentageRisk , SL_TpRatio ,TP,SL,pipval,logger):
    #print(symbol)
    """
             open[1] <= low[5]; high[3] <= low[7]; ValueOpen(5)[1] > ValueLow(5)[4]; Stochastics(3)[0] <= 20; EMA(close;5)[0] < EMA(close;5)[2]; EMA(close;100)[0] > EMA(close;100)[2]
            high[0] > close[8]; low[1] > high[5]; low[7] > low[9]; high[8] > open[9]; high[4] <= high[5]; close[0] >= highest(close;100)[0]
            high[3] > close[8]; open[4] > open[5]; open[0] <= low[3]; open[1] <= low[2]; open[4] <= close[5]; rateOfChange(close;3)[0] < 0
            low[2] > close[3]; low[4] > close[6]; open[0] > EMA(close;200)[0]; low[0] > EMA(close;100)[0]; rsi(close;14)[0] >= 20; EMA(close;200)[0] > EMA(close;200)[2]
    """
    time_hr = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))

    df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_M15 , 0 , 2700))

    logger.info(f'Running Event Loop for {symbol} at {datetime.now()}')
    logger.info(f'Running Event Loop for {symbol} at {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
    for i in range(2):
        try: 
            df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_M15 , 0 , 2700))
            df['time']= df['time'].map(lambda Date : datetime.fromtimestamp(Date) -  timedelta(hours= 3))

            df['ema_200'] = sig.EMA(df,200)
            df['ema_5'] = sig.EMA(df,5)
            df['ema_100'] = sig.EMA(df,100)
            df['rsi_14'] = sig.rsi(df,14)
            df['stoch_3'] = sig.Stochastic(df,3)

            df['ValueOpen'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'open')
            df['ValueLow'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'low')
            df['ValueHigh'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'high')
            df['ValueClose'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'close')

            df['high_close'] = sig.highest(df,100,'close')
           
            df['roc_3'] = sig.rateOfChange(df,3,(1/SL_TpRatio))       
             
            df['ATR'] = sig.AvgTrueRange(df,7)
            
            

        except AttributeError:
            if mt5.initialize():
                logger.info(f'connected {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            else:
                logger.info(f' not connected {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
                login = 51314848
                password = 'zVQKjwZU'
                server = 'ICMarketsSC-Demo'

                mt5.initialize(login = login , password = password, server = server)
                #time.sleep(20)
                logger.info(f'connected ,{mt5.initialize()} , {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            continue
        break
    df.to_csv(f'{symbol}_{entry}_dataframe')
    df_entry = pd.read_csv(f'{symbol}_{entry}_entry_signals.csv')
    for i in range(1):
        try:                        
                
            # Short Condition

            """
                 open[1] <= low[5]; high[3] <= low[7]; ValueOpen(5)[1] > ValueLow(5)[4]; Stochastics(3)[0] <= 20; EMA(close;5)[0] < EMA(close;5)[2]; EMA(close;100)[0] > EMA(close;100)[2]
                high[0] > close[8]; low[1] > high[5]; low[7] > low[9]; high[8] > open[9]; high[4] <= high[5]; close[0] >= highest(close;100)[0]
                high[3] > close[8]; open[4] > open[5]; open[0] <= low[3]; open[1] <= low[2]; open[4] <= close[5]; rateOfChange(close;3)[0] < 0
                low[2] > close[3]; low[4] > close[6]; open[0] > EMA(close;200)[0]; low[0] > EMA(close;100)[0]; rsi(close;14)[0] >= 20; EMA(close;200)[0] > EMA(close;200)[2]
            
            """
            if df_entry.empty:
                for i in range(1,5):
                    signal = f'signal{i}'
                    if entry_signal1(df,i):
                        # Got Indication Candle
                        # Got Indication Candle
                        
                        signal = f'signal{i}'
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for {signal} {symbol} at {time1}')
                        print(f'Got Indication Candle  for signal {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy',signal,200+i )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss]
                    else:
                        
                        logger.info(f'No entry for {signal} {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}')    
                    
                    
                  
            else:
                column_name = 'signals'
                for i in range(1,5):
                    signal = f'signal{i}'
                    if df_entry[column_name].eq(i).any():
                        logger.info(f"The {signal} entry exists ")
                    else:
                        if entry_signal1(df,i):
                            # Got Indication Candle
                            # Got Indication Candle
                            
                            time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                            logger.info(f'Got Indication Candle for {signal} {symbol} at {time1}')
                            print(f'Got Indication Candle  for {signal} {symbol} at {time1}')
                            index = -2
                            data = df.copy()
                            logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")
                            
                            LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                            
                            
                            order= market_order(symbol , LotSize,'buy',signal,200+i )
                            tick = mt5.symbol_info_tick(symbol)
                            Price = tick.ask
                            SL_dis = SL
                            StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                            TP_val = Price + TP * df.iloc[-2]['ATR']
                            order_id = order.order
                            order_price = order.price
                            print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                            logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                            df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss]
                        else:
                        
                            logger.info(f'No entry for {signal} {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                     
                     
                

            if not df_entry.empty:
                rows_to_delete = []
                print('checkfor')
                               
                while True:
                    if time_hr.minute % 15 ==  0:
                            dd_time = 15*60 - 20
                    # elif time_hr.minute >= 19:
                    #         dd_time = 15*60 - 21*60 - 10
                    # elif time_hr.minute >= 10:
                    #         dd_time = 15*60 - 
                    # elif time_hr.minute >= 5:
                    #         dd_time = 15*60 - 6*60
                    else:
                            dd_time = 15*60 - 90
                    
                    if (  (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)) - time_hr).seconds < dd_time:

                        if (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)).weekday() !=5 and (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)).weekday() !=6:
                                
                                # SL , TP check
                                
                            Price = mt5.symbol_info_tick(symbol).bid
                                    # SL Hit
                            for index, row in df_entry.iterrows():
                                try:
                                    if index not in rows_to_delete:
                                        if Price <= row['SL']:
                                                time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                print(f'SL Hit at{time_s} ')
                                                close = close_order(row['orderid'])
                                                logger.info(f"SL hit {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']},{close.comment}  ")
                                                rows_to_delete.append(index)

                                            # TP Hit
                                            # Trailing Triggere
                                        elif Price >= row['TP']:
                                                time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                print(f'TP Hit at{time_s} ')
                                                close = close_order(row['orderid'])
                                                logger.info(f"TP  hit {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']},{close.comment}  ")
                                                rows_to_delete.append(index)
                                except:
                                     continue

                                        
                    else:
                        df_entry = df_entry.drop(rows_to_delete)
                        df_entry.reset_index(inplace= True)
                        df_entry.drop('index', axis=1, inplace=True)
                        df_entry.to_csv(f'{symbol}_{entry}_entry_signals.csv',index = False)
                        logger.info(f'fn out by time {dd_time} {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                        return
            else:
                # df_entry = df_entry.drop(rows_to_delete)
                # df_entry.reset_index(inplace= True)
                
                df_entry.to_csv(f'{symbol}_{entry}_entry_signals.csv',index = False)
                logger.info(f'fn out no current running entry {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                time.sleep(20)
                return
                        
                                        
                                        


                            

        except AttributeError:
            if mt5.initialize():
                logger.info('connnected in loop')
            else:
                logger.info(f' not connected ifelse{datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
                login = 51314848
                password = 'zVQKjwZU'
                server = 'ICMarketsSC-Demo'
                mt5.initialize(login = login , password = password, server = server)
                #time.sleep(20)
                logger.info(f'connected ,{mt5.initialize()} , {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            continue
        break

    
                    


# In[19]:




if __name__ == '__main__':
    print('step1')
    Execution()



# In[ ]:




