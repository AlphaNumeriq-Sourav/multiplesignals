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
def entry_signal1(data):
    """
                 ValueHigh(5)[0] <= 6; ValueHigh(5)[0] > ValueOpen(5)[3]; ValueClose(5)[2] > ValueOpen(5)[3]; ValueClose(5)[0] <= ValueLow(5)[5]; SMA(close;10)[0] > SMA(close;10)[3]; close[0] <= CompositeSMA(8;20;50;200)[0]
                
            
    """
    index = -2
    
    return (data.iloc[index]['ValueHigh'] <= 6) and (data.iloc[index]['ValueHigh'] > data.iloc[index - 3]['ValueOpen']) \
        and (data.iloc[index-2]['ValueClose'] > data.iloc[index - 3]['ValueOpen']) and (data.iloc[index]['ValueClose'] <= data.iloc[index - 5]['ValueLow']) \
            and (data.iloc[index]['sma_10'] > data.iloc[index -3]['sma_10']) and (data.iloc[index]['close'] <= data.iloc[index]['composite_sma']) 
    # return True
def entry_signal2(data):
    """
                
            close[0] > low[4]; high[1] > low[8]; OHLC[0] > OHLC[1]; ValueLow(5)[1] <= ValueOpen(5)[3]; momentum(close;10)[0] < momentum(close;10)[5]; SMA(close;100)[0] < SMA(close;100)[5]                
    """
    index = -2
    return (data.iloc[index]['close'] > data.iloc[index - 4]['low']) and (data.iloc[index - 1]['high'] > data.iloc[index - 8]['low']) and (data.iloc[index]['OHLC'] > data.iloc[index - 1]['OHLC']) \
    and (data.iloc[index-1]['ValueLow'] <= data.iloc[index - 3]['ValueOpen']) and (data.iloc[index]['momentum_10'] < data.iloc[index-5]['momentum_10']) and (data.iloc[index]['sma_100'] < data.iloc[index - 5]['sma_100'])

def entry_signal3(data):
    """
                
                 open[5] > high[8]; OHLC[0] <= OHLC[5]; ValueClose(5)[2] > ValueLow(5)[5]; ValueLow(5)[2] <= ValueClose(5)[3]; momentum(close;3)[0] < 0; momentum(close;3)[0] < momentum(close;3)[4]
                
            
    """
    index = -2
    return (data.iloc[index-5]['open'] > data.iloc[index - 8]['high']) and (data.iloc[index]['OHLC'] <= data.iloc[index - 5]['OHLC'])and (data.iloc[index -2 ]['ValueClose'] > data.iloc[index - 5]['ValueLow']) \
        and (data.iloc[index-2]['ValueLow'] <= data.iloc[index - 3]['ValueClose']) \
    and (data.iloc[index]['momentum_3'] < data.iloc[index -4]['momentum_3']) and (data.iloc[index]['momentum_3'] < 0) 
def entry_signal4(data):
    """
                
    
                close[0] > low[8]; open[2] > high[8]; low[0] <= high[2]; ValueClose(5)[1] <= ValueOpen(5)[2]; SuperSmoother[0] <= SuperSmoother[2]; close[0] <= CompositeEMA(8;20;50;200)[0]
            
    """
    index = -2
    return (data.iloc[index]['close'] > data.iloc[index - 8]['low']) and (data.iloc[index - 2]['open'] > data.iloc[index - 8]['high']) and (data.iloc[index]['low'] <= data.iloc[index - 2]['high']) \
    and (data.iloc[index - 1]['ValueClose'] <= data.iloc[index-2]['ValueOpen']) and (data.iloc[index]['SuperSmoother'] <= data.iloc[index-2]['SuperSmoother'])  and (data.iloc[index]['close'] <= data.iloc[index]['composite_ema']) 

def entry_signal5(data):
    """
                
    
 open[0] > close[1]; high[3] > close[8]; close[0] <= open[8]; close[4] <= high[8]; open[7] <= open[9]; volume[0] > volume[4]            
    """
    index = -2
    # return (data.iloc[index]['close'] > data.iloc[index - 8]['low']) and (data.iloc[index - 2]['open'] > data.iloc[index - 8]['high']) and (data.iloc[index]['low'] <= data.iloc[index - 2]['high']) \
    # and (data.iloc[index - 1]['ValueClose'] < data.iloc[index-2]['ValueOpen']) and (data.iloc[index]['SuperSmoother'] <= data.iloc[index-2]['SuperSmoother'])  and (data.iloc[index]['close'] <= data.iloc[index]['composite_ema']) 
    return False
def entry_signal6(data):
    """
                
    
 open[3] > open[4]; high[5] > open[6]; high[4] <= close[6]; low[7] <= high[9]; volume[0] <= volume[4]; ValueOpen(5)[0] > ValueLow(5)[1]            
    """
    index = -2
    return False
    return (data.iloc[index]['close'] > data.iloc[index - 8]['low']) and (data.iloc[index - 2]['open'] > data.iloc[index - 8]['high']) and (data.iloc[index]['low'] <= data.iloc[index - 2]['high']) \
    and (data.iloc[index - 1]['ValueClose'] < data.iloc[index-2]['ValueOpen']) and (data.iloc[index]['SuperSmoother'] <= data.iloc[index-2]['SuperSmoother'])  and (data.iloc[index]['close'] <= data.iloc[index]['composite_ema']) 

def entry_signal7(data):
    """
                
    
 high[1] > open[4]; open[5] <= close[6]; ValueHigh(5)[0] <= ValueOpen(5)[3]; ValueLow(5)[0] <= ValueLow(5)[3]; CompositeRSI(2;24)[0] <= 40; rateOfChange(close;10)[0] < 0            
    """
    index = -2
    return (data.iloc[index]['high'] > data.iloc[index - 4]['open']) and (data.iloc[index - 5]['open'] <= data.iloc[index - 6]['close']) and (data.iloc[index]['ValueHigh'] <= data.iloc[index - 3]['ValueOpen']) \
    and (data.iloc[index ]['ValueLow'] <= data.iloc[index-3]['ValueLow']) and (data.iloc[index]['composite_rsi'] <= 40)  and (data.iloc[index]['ROC'] < 0) 




def Execution(scrip_name,symbol , PerCentageRisk , SL_TpRatio ,TP,SL,pipval,logger):
    #print(symbol)
    """
         ValueHigh(5)[0] <= 6; ValueHigh(5)[0] > ValueOpen(5)[3]; ValueClose(5)[2] > ValueOpen(5)[3]; ValueClose(5)[0] <= ValueLow(5)[5]; SMA(close;10)[0] > SMA(close;10)[3]; close[0] <= CompositeSMA(8;20;50;200)[0]
        close[0] > low[4]; high[1] > low[8]; OHLC[0] > OHLC[1]; ValueLow(5)[1] <= ValueOpen(5)[3]; momentum(close;10)[0] < momentum(close;10)[5]; SMA(close;100)[0] < SMA(close;100)[5]
        open[5] > high[8]; OHLC[0] <= OHLC[5]; ValueClose(5)[2] > ValueLow(5)[5]; ValueLow(5)[2] <= ValueClose(5)[3]; momentum(close;3)[0] < 0; momentum(close;3)[0] < momentum(close;3)[4]
        close[0] > low[8]; open[2] > high[8]; low[0] <= high[2]; ValueClose(5)[1] <= ValueOpen(5)[2]; SuperSmoother[0] <= SuperSmoother[2]; close[0] <= CompositeEMA(8;20;50;200)[0]

        open[0] > close[1]; high[3] > close[8]; close[0] <= open[8]; close[4] <= high[8]; open[7] <= open[9]; volume[0] > volume[4]
        open[3] > open[4]; high[5] > open[6]; high[4] <= close[6]; low[7] <= high[9]; volume[0] <= volume[4]; ValueOpen(5)[0] > ValueLow(5)[1]
        high[1] > open[4]; open[5] <= close[6]; ValueHigh(5)[0] <= ValueOpen(5)[3]; ValueLow(5)[0] <= ValueLow(5)[3]; CompositeRSI(2;24)[0] <= 40; rateOfChange(close;10)[0] < 0
            
    """
    time_hr = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))

    df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_H1 , 0 , 2700))

    logger.info(f'Running Event Loop for {symbol} at {datetime.now()}')
    logger.info(f'Running Event Loop for {symbol} at {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
    for i in range(2):
        try: 
            df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_H1 , 0 , 2700))
            df['time']= df['time'].map(lambda Date : datetime.fromtimestamp(Date) -  timedelta(hours= 3))

            time_hr = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
            logger.info(f"time: {time_hr} lastindex : {df.iloc[-1]['time'].hour} ")

            for i in range(5):
                if  (df.iloc[-1]['time'].hour == time_hr.hour) or (df.iloc[-1]['time'].hour >= time_hr.hour):
                     break
                else:
                    df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_H1, 0 , 2700))
                    df['time']= df['time'].map(lambda Date : datetime.fromtimestamp(Date) -  timedelta(hours= 3))
                    time_false = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                    logger.info(f"  False time: {time_hr} lastindex : {df.iloc[-1]['time'].hour}, time now: {time_false} ")

            df['sma_10'] = sig.SMA(df, 10)
            df['composite_sma'] =sig.CompositeSMA(df,8,20,50,200)
            df['composite_ema'] =sig.CompositeEMA(df,8,20,50,200)
            df['composite_rsi'] =sig.CompositeRSI(df,2,24)
            df['sma_100'] = sig.SMA(df, 100)
            df['OHLC'] = sig.OHLC(df)

            df['ValueOpen'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'open')
            df['ValueLow'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'low')
            df['ValueHigh'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'high')
            df['ValueClose'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'close')

            df['momentum_10'] = sig.momentum(df,10)
            df['momentum_3'] = sig.momentum(df,3)
            df['SuperSmoother'] = sig.SuperSmoother(df)
            df['ATR'] = sig.AvgTrueRange(df,7)
            df['ROC'] = sig.rateOfChange(df,10,(1/SL_TpRatio))
            

        except AttributeError:
            if mt5.initialize():
                logger.info(f'connected {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            else:
                logger.info(f' not connected {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
                login = 51313012
                password = 'JqKKQHdc'
                server = 'ICMarketsSC-Demo'

                mt5.initialize(login = login , password = password, server = server)
                #time.sleep(20)
                logger.info(f'connected ,{mt5.initialize()} , {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            continue
        break
    df.to_csv(f'{scrip_name}_dataframe')
    df_entry = pd.read_csv(f'{scrip_name}_entry_signals.csv')
    for i in range(1):
        try:                        
                
            # Short Condition

            """
                low[0] > open[9]; low[2] > high[6]; open[5] > high[9]; low[6] > open[9]; low[0] <= low[1]; SMA(close;8)[0] > SMA(close;8)[3]
                
                high[3] > close[4]; open[1] <= close[4]; close[8] <= open[9]; open[7] <= close[9]; low[0] < SMA(close;8)[0]; EMA(close;8)[0] > EMA(close;8)[3]
                open[0] > low[2]; open[0] > close[8]; low[2] > high[6]; high[5] > close[6]; close[6] > high[9]; ValueOpen(5)[1] > ValueLow(5)[2]
                low[0] > open[7]; low[3] > open[4]; low[4] > open[5]; open[0] < HLMedian[0]; ValueLow(5)[2] > ValueLow(5)[4]; ValueOpen(5)[0] <= ValueHigh(5)[1]
            
            """
            if df_entry.empty:
                 
                if entry_signal1(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal1 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signal {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_1',1000+1 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [1,order_id,order.volume,Price,TP_val,StopLoss]
                else:
                    
                    logger.info(f'No entry for signal1 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}')    
                    
                    
                if entry_signal2(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal2 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signal2 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)

                        
                        order= market_order(symbol , LotSize,'buy','signal_2',1000+2 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [2,order_id,order.volume,Price,TP_val,StopLoss]
                else:
                    
                    logger.info(f'No entry for signal2{(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}')    
                if entry_signal3(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal3 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signal3 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_3',1000+3 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [3,order_id,order.volume,Price,TP_val,StopLoss]
                else:
                    
                    logger.info(f'No entry for signal3 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}')    
                if entry_signal4(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal4 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signa4 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_4',1000+4 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [4,order_id,order.volume,Price,TP_val,StopLoss]
                else:
                    
                    logger.info(f'No entry for signal4 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}')  
                if entry_signal5(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal5 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signa5 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")

                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_5',1000+5 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [5,order_id,order.volume,Price,TP_val,StopLoss]
                else:
                    
                    logger.info(f'No entry for signal5 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}')    
                if entry_signal6(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal6 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signal6 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")

                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_6',1000+6 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [6,order_id,order.volume,Price,TP_val,StopLoss]
                else:
                    
                    logger.info(f'No entry for signal6 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}')    
                if entry_signal7(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal7 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signa7 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")

                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_7',1000+7 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [7,order_id,order.volume,Price,TP_val,StopLoss]
                else:
                    
                    logger.info(f'No entry for signal7 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}')     
                  
            else:
                column_name = 'signals'
                if df_entry[column_name].eq(1).any():
                    logger.info(f"The signal1 entry exists ")
                else:
                    if entry_signal1(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal1 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signal {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")

                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        
                        order= market_order(symbol , LotSize,'buy','signal_1',1000+1 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [1,order_id,order.volume,Price,TP_val,StopLoss]
                    else:
                    
                        logger.info(f'No entry for signal1 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                if df_entry[column_name].eq(2).any():
                    logger.info(f"The signal2 entry exists ")
                else:
                    if entry_signal2(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal2 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signal2 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")
                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_2',1000+2 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [2,order_id,order.volume,Price,TP_val,StopLoss]
                    else:
                    
                        logger.info(f'No entry for signal2 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                if df_entry[column_name].eq(3).any():
                    logger.info(f"The signal3 entry exists ")
                else:
                    if entry_signal3(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal3 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signal3 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")
                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_3',1000+3 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [3,order_id,order.volume,Price,TP_val,StopLoss]
                    else:
                        
                        logger.info(f'No entry for signal3 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}')    
                   
                if df_entry[column_name].eq(4).any():
                    logger.info(f"The signal4 entry exists ")
                else:  
                    if entry_signal4(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal4 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signa4 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")
                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_4',1000+4 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [4,order_id,order.volume,Price,TP_val,StopLoss]
                    else:
                    
                        logger.info(f'No entry for signal4 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                if df_entry[column_name].eq(5).any():
                    logger.info(f"The signal4 entry exists ")
                else:  
                    if entry_signal5(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal5 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signa5 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")
                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_5',1000+5 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [5,order_id,order.volume,Price,TP_val,StopLoss]
                    else:
                    
                        logger.info(f'No entry for signal5 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                if df_entry[column_name].eq(6).any():
                    logger.info(f"The signal4 entry exists ")
                else:  
                    if entry_signal6(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal6 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signal6 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")
                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_6',1000+6 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [6,order_id,order.volume,Price,TP_val,StopLoss]
                    else:
                    
                        logger.info(f'No entry for signal6 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                if df_entry[column_name].eq(7).any():
                    logger.info(f"The signal7 entry exists ")
                else:  
                    if entry_signal7(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal7 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signa7 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")

                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_7',1000+7 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [7,order_id,order.volume,Price,TP_val,StopLoss]
                    else:
                    
                        logger.info(f'No entry for signal7 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                     
                     
                

            if not df_entry.empty:
                rows_to_delete = []
                print('checkfor')
                               
                while True:
                    if time_hr.minute  ==  0:
                            dd_time = 60*60 - 20
                    # elif time_hr.minute >= 19:
                    #         dd_time = 15*60 - 21*60 - 10
                    # elif time_hr.minute >= 10:
                    #         dd_time = 15*60 - 
                    # elif time_hr.minute >= 5:
                    #         dd_time = 15*60 - 6*60
                    else:
                            dd_time = 60*60 - 90
                    
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
                        df_entry.to_csv(f'{scrip_name}_entry_signals.csv',index = False)
                        logger.info(f'fn out by time {dd_time} {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                        return
            else:
                # df_entry = df_entry.drop(rows_to_delete)
                # df_entry.reset_index(inplace= True)
                
                df_entry.to_csv(f'{scrip_name}_entry_signals.csv',index = False)
                logger.info(f'fn out no current running entry {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                time.sleep(20)
                return
                        
                                        
                                        


                            

        except AttributeError:
            if mt5.initialize():
                logger.info('connnected in loop')
            else:
                logger.info(f' not connected ifelse{datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
                login = 51313012
                password = 'JqKKQHdc'
                server = 'ICMarketsSC-Demo'
                mt5.initialize(login = login , password = password, server = server)
                #time.sleep(20)
                logger.info(f'connected ,{mt5.initialize()} , {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            continue
        break

    
                    


# In[19]:


# def premain(symbol , RISK , ds ,TP,SL,pip):
    
    
    # df_cols = ['signals','orderid','volume','price_open','TP','SL']
        
    # # df_entry = pd.DataFrame(columns= df_cols) 
    # # df_entry.to_csv(f'{symbol}_entry_signals.csv',index= False)

    # login = 	11044024
    # password = 'p9L8VKnL'
    # server = 'ICMarketsSC-MT5-4'

    # logger = logging.getLogger(f'{symbol}')
    # logger.setLevel(logging.DEBUG)
    # # create file handler which logs even debug messages
    # fh = logging.FileHandler(f'{symbol}_BA_atr.log')
    # fh.setLevel(logging.DEBUG)
    # logger.addHandler(fh)

        

    # if mt5.initialize(login = login , password = password, server = server):
    #     print(f'Script Started for {symbol}')
    #     while True:
    #         if (datetime.now().weekday()) != 5 and    \
    #                     (datetime.now().weekday()) != 6:
    #             if mt5.initialize():
                
                
    #                 # print("Connected")
    #                 if ((datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)).weekday()) != 5 and                  ((datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)).weekday()) != 6:
            
                    
    #                 #print('step3')
                    

    #                     try:
    #                         time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
    #                         time2 = mt5.symbol_info_tick(symbol).time
    #                         time3 = mt5.symbol_info_tick(symbol).time


    #                     except AttributeError:
    #                         time.sleep(20)
    #                         # continue
                        
                        

    #                     if  (time2 % (3600 *24)  != 0) :  #not 00:00

    #                         if (time2 % 3600  == 0) or (time2 % 3600  < 3):
    #                             #x = 1
    #                             logger.info(f'processor {symbol},Time = {time1}')
    #                             print(symbol)
    #                             Execution(symbol,RISK , ds,TP,SL,pip,logger)
    #                             logger.info(f'processor out {symbol},Time = {time1}')
                            
                        

    #                     if (time2 % (3600 *24)  == 1200) or (time3 % (3600 *24 )  == 1200):
                            
    #                         logger.info(f'processor {symbol},Time = {time1}')
    #                         print(symbol)
    #                         Execution(symbol,RISK , ds,TP,SL,pip,logger)
    #                         logger.info(f'processor out {symbol},Time = {time1}')
    #                         #time.sleep(60)
                        
    #             else:
    #                 print("Not Connected")
                    
    #                 time1 = (datetime.now())
    #                 print(time1)
    #                 with open(f'NotInitial.txt' , 'a') as file:
    #                             file.write(f'\n symbol = {symbol},')
                                
    #                             file.write(f'Time = {time1}')
    #                 file.close
    #                 logger.info(f'not connected {symbol},Time = {time1}')
    #                 cd = mt5.initialize(login = login , password = password, server = server)
    #                 #print(cd)
    #                 logger.info(f'connected {cd},Time = {datetime.now()}')




if __name__ == '__main__':
    print('step1')
    Execution()



# In[ ]:




