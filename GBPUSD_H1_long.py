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
 open[2] > close[9]; close[6] > close[7]; (open[0] >= low[1]) AND (open[0] <= min(open[1][1];close[1][1])); low[0] < EMA(close;100)[0]; SuperSmoother[0] <= SuperSmoother[1]; ADX(20)[0] <= ADX(20)[5]                
            
    """
    index = -2
    
    return (data.iloc[index-2]['open'] > data.iloc[index-9]['close']) and (data.iloc[index - 6]['close'] > data.iloc[index - 7]['close']) \
        and ((data.iloc[index]['open'] >= data.iloc[index - 1]['low']) and (data.iloc[index]['open'] <= min(data.iloc[index-1]['open'],data.iloc[index-1]['close']))) \
    and (data.iloc[index]['low'] < data.iloc[index]['ema_100']) and (data.iloc[index]['supersmoother'] <= data.iloc[index-1]['supersmoother'] ) and (data.iloc[index]['adx_20'] <= data.iloc[index-5]['adx_20'])
    # return True
def entry_signal2(data):
    """
                
 high[1] > close[4]; low[6] > open[8]; CCI(20)[0] <= CCI(20)[3]; rsi(close;14)[0] <= rsi(close;14)[2]; rateOfChange(close;3)[0] < rateOfChange(close;3)[2]; SMA(close;100)[0] < SMA(close;100)[3] 
    
    """
    index = -2
    return (data.iloc[index-1]['high'] > data.iloc[index - 4]['close']) and (data.iloc[index - 6]['low'] > data.iloc[index - 8]['open']) and (data.iloc[index]['CCI'] <= data.iloc[index - 3]['CCI']) \
    and (data.iloc[index]['RSI_14'] <= data.iloc[index - 2]['RSI_14']) and (data.iloc[index]['ROC_3'] < data.iloc[index-2]['ROC_3']) and (data.iloc[index]['sma_100'] < data.iloc[index - 3]['sma_100'])

def entry_signal3(data):
    """
                
         close[2] > high[8]; open[3] > open[4]; high[0] <= high[1]; ValueHigh(5)[0] > ValueClose(5)[1]; close[0] <= Close[1]+(-0.5)*AvgTrueRange(20)[1]; rateOfChange(close;10)[0] < rateOfChange(close;10)[1]
                
            
    """
    index = -2
    return (data.iloc[index-2]['close'] > data.iloc[index - 8]['high']) and (data.iloc[index -3 ]['open'] > data.iloc[index - 4]['open']) and (data.iloc[index]['high'] <= data.iloc[index-1]['high']) \
    and (data.iloc[index]['ValueHigh'] > data.iloc[index -1]['ValueClose']) and (data.iloc[index]['close'] < data.iloc[index-1]['close'] + (-0.5)*data.iloc[index-1]['ATR_20']) \
          and (data.iloc[index]['ROC_10'] < data.iloc[index-1]['ROC_10']) 
def entry_signal4(data):
    """
                
    
        high[6] > high[9]; close[2] <= low[6]; low[3] <= low[7]; low[3] <= close[8]; AvgTrueRange(10)[0] <= AvgTrueRange(10)[5]; rsi(close;2)[0] <= 30            
    """
    index = -2
    return (data.iloc[index-1]['low'] <= data.iloc[index - 7]['close']) and (data.iloc[index - 6]['close'] <= data.iloc[index - 7]['low']) and (data.iloc[index-2]['ValueHigh'] > data.iloc[index - 4]['ValueOpen']) \
     and (data.iloc[index-3]['ValueHigh'] > data.iloc[index-5]['ValueHigh']) and (data.iloc[index]['ValueLow'] <= data.iloc[index - 5]['ValueHigh']) and (data.iloc[index]['ema_5'] > data.iloc[index-1]['ema_5'])

def entry_signal5(data):
    """
                
    
 open[2] > open[8]; low[2] <= high[4]; (open[0] >= low[1]) AND (open[0] <= min(open[1][1];close[1][1])); ValueHigh(5)[2] <= ValueOpen(5)[5]; CompositeEMA(8;20;50;200)[0] <= CompositeEMA(8;20;50;200)[1]    
    """
    index = -2
    return (data.iloc[index-2]['open'] > data.iloc[index - 8]['open']) and (data.iloc[index - 2]['low'] <= data.iloc[index - 4]['high']) \
        and ((data.iloc[index]['open'] >= data.iloc[index - 1]['low']) and (data.iloc[index]['open'] <= min(data.iloc[index-1]['open'] , data.iloc[index - 1]['close'])) )\
    and (data.iloc[index - 2]['ValueHigh'] <= data.iloc[index-5]['ValueOpen']) and (data.iloc[index]['composite_ema'] <= data.iloc[index-1]['composite_ema'])   
    # return False
def entry_signal6(data):
    """
                
    
 close[2] > low[6]; open[1] <= low[3]; open[8] <= high[9]; ValueOpen(5)[1] <= ValueHigh(5)[3]; ValueHigh(5)[0] <= ValueHigh(5)[3]; high[0] < EMA(close;20)[0]
         """
    index = -2
    # return False
    return (data.iloc[index-2]['close'] > data.iloc[index - 6]['low']) and (data.iloc[index - 1]['open'] <= data.iloc[index - 3]['low']) and (data.iloc[index-8]['open'] <= data.iloc[index - 9]['high']) \
    and (data.iloc[index - 1]['ValueOpen'] <= data.iloc[index-3]['ValueHigh']) and (data.iloc[index]['ValueHigh'] <= data.iloc[index-3]['ValueHigh'])  and (data.iloc[index]['high'] < data.iloc[index]['ema_20']) 

def entry_signal7(data):
    """
                
    
 open[6] > high[8]; open[0] <= open[3]; close[0] <= low[5]; open[3] <= close[8]; ValueOpen(5)[0] <= ValueHigh(5)[5]; ValueOpen(5)[1] <= ValueHigh(5)[3]  
     """
    index = -2
    return (data.iloc[index-6]['open'] > data.iloc[index - 8]['high']) and (data.iloc[index]['open'] <= data.iloc[index - 3]['open']) and (data.iloc[index]['close'] <= data.iloc[index - 5]['low']) \
    and (data.iloc[index -3 ]['open'] <= data.iloc[index-8]['close'])  and (data.iloc[index]['ValueOpen'] <= data.iloc[index-5]['ValueHigh']) and (data.iloc[index-1]['ValueOpen'] <= data.iloc[index-3]['ValueHigh'])

def entry_signal8(data):
    """
                
    
  close[3] > low[8]; low[1] <= high[4]; open[2] <= high[9]; high[3] <= close[7]; open[5] <= close[6]; CompositeSMA(8;20;50;200)[0] <= CompositeSMA(8;20;50;200)[5]
     """
    index = -2
    return (data.iloc[index-3]['close'] > data.iloc[index - 8]['low']) and (data.iloc[index-1]['low'] <= data.iloc[index - 4]['high']) and (data.iloc[index-2]['open'] <= data.iloc[index - 9]['high']) \
    and (data.iloc[index -3 ]['high'] <= data.iloc[index-7]['close'])  and (data.iloc[index-5]['open'] <= data.iloc[index-6]['close']) and (data.iloc[index]['composite_sma'] <= data.iloc[index-5]['composite_sma'])





def Execution(script_name,symbol , PerCentageRisk , SL_TpRatio ,TP,SL,pipval,logger):
    #print(symbol)
    """
          open[2] > close[9]; close[6] > close[7]; (open[0] >= low[1]) AND (open[0] <= min(open[1][1];close[1][1])); low[0] < EMA(close;100)[0]; SuperSmoother[0] <= SuperSmoother[1]; ADX(20)[0] <= ADX(20)[5]
            high[1] > close[4]; low[6] > open[8]; CCI(20)[0] <= CCI(20)[3]; rsi(close;14)[0] <= rsi(close;14)[2]; rateOfChange(close;3)[0] < rateOfChange(close;3)[2]; SMA(close;100)[0] < SMA(close;100)[3]
            close[2] > high[8]; open[3] > open[4]; high[0] <= high[1]; ValueHigh(5)[0] > ValueClose(5)[1]; close[0] <= Close[1]+(-0.5)*AvgTrueRange(20)[1]; rateOfChange(close;10)[0] < rateOfChange(close;10)[1]
            high[6] > high[9]; close[2] <= low[6]; low[3] <= low[7]; low[3] <= close[8]; AvgTrueRange(10)[0] <= AvgTrueRange(10)[5]; rsi(close;2)[0] <= 30
            open[2] > open[8]; low[2] <= high[4]; (open[0] >= low[1]) AND (open[0] <= min(open[1][1];close[1][1])); ValueHigh(5)[2] <= ValueOpen(5)[5]; CompositeEMA(8;20;50;200)[0] <= CompositeEMA(8;20;50;200)[1]
            close[2] > low[6]; open[1] <= low[3]; open[8] <= high[9]; ValueOpen(5)[1] <= ValueHigh(5)[3]; ValueHigh(5)[0] <= ValueHigh(5)[3]; high[0] < EMA(close;20)[0]
            open[6] > high[8]; open[0] <= open[3]; close[0] <= low[5]; open[3] <= close[8]; ValueOpen(5)[0] <= ValueHigh(5)[5]; ValueOpen(5)[1] <= ValueHigh(5)[3]
            close[3] > low[8]; low[1] <= high[4]; open[2] <= high[9]; high[3] <= close[7]; open[5] <= close[6]; CompositeSMA(8;20;50;200)[0] <= CompositeSMA(8;20;50;200)[5]
                        
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

            df['sma_100'] = sig.SMA(df, 100)
            df['ema_100'] = sig.EMA(df, 100)
            df['ema_20'] = sig.EMA(df, 20)
            df['ema_5'] = sig.EMA(df, 5)
            df['RSI_2'] = sig.rsi(df, 2)
            df['RSI_14'] = sig.rsi(df, 14)
            df['adx_20'] = sig.ADX(df,20)
            df['CCI'] = sig.CCI(df,20)
            df['composite_sma'] =sig.CompositeSMA(df,8,20,50,200)
            df['composite_ema'] =sig.CompositeEMA(df,8,20,50,200)
            df['composite_rsi'] =sig.CompositeRSI(df,2,24)
            
            df['ValueOpen'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'open')
            df['ValueLow'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'low')
            df['ValueHigh'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'high')
            df['ValueClose'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'close')
            df['ROC_10'] = sig.rateOfChange(df,10,(1/SL_TpRatio))
            df['ROC_3'] = sig.rateOfChange(df,3,(1/SL_TpRatio))
            df['supersmoother'] = sig.SuperSmoother(df)
            df['ATR'] = sig.AvgTrueRange(df,7)
            df['ATR_10'] = sig.AvgTrueRange(df,10)
            df['ATR_20'] = sig.AvgTrueRange(df,20)

            
            

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
    df.to_csv(f'{script_name}_dataframe')
    df_entry = pd.read_csv(f'{script_name}_entry_signals.csv')
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
                        
                        order= market_order(symbol , LotSize,'buy','signal_1',2000+1 )
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

                        
                        order= market_order(symbol , LotSize,'buy','signal_2',2000+2 )
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
                        
                        order= market_order(symbol , LotSize,'buy','signal_3',2000+3 )
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
                        
                        order= market_order(symbol , LotSize,'buy','signal_4',2000+4 )
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
                        
                        order= market_order(symbol , LotSize,'buy','signal_5',2000+5 )
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
                        
                        order= market_order(symbol , LotSize,'buy','signal_6',2000+6 )
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
                        
                        order= market_order(symbol , LotSize,'buy','signal_7',2000+7 )
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
                if entry_signal8(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal8 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signal8 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")

                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_8',2000+8 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [8,order_id,order.volume,Price,TP_val,StopLoss]
                else:
                    
                        logger.info(f'No entry for signal8 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}')   
                  
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
                        
                        
                        order= market_order(symbol , LotSize,'buy','signal_1',2000+1 )
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
                        
                        order= market_order(symbol , LotSize,'buy','signal_2',2000+2 )
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
                        
                        order= market_order(symbol , LotSize,'buy','signal_3',2000+3 )
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
                        
                        order= market_order(symbol , LotSize,'buy','signal_4',2000+4 )
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
                        
                        order= market_order(symbol , LotSize,'buy','signal_5',2000+5 )
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
                        
                        order= market_order(symbol , LotSize,'buy','signal_6',2000+6 )
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
                        
                        order= market_order(symbol , LotSize,'buy','signal_7',2000+7 )
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
                if df_entry[column_name].eq(8).any():
                    logger.info(f"The signal8 entry exists ")
                else:  
                    if entry_signal8(df):
                        # Got Indication Candle
                        # Got Indication Candle
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for signal8 {symbol} at {time1}')
                        print(f'Got Indication Candle  for signal8 {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")

                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'buy','signal_8',2000+8 )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.ask
                        SL_dis = SL
                        StopLoss = Price - SL_dis * df.iloc[-2]['ATR']
                        TP_val = Price + TP * df.iloc[-2]['ATR']
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [8,order_id,order.volume,Price,TP_val,StopLoss]
                    else:
                    
                        logger.info(f'No entry for signal8 {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                     
                     
                

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
                    elif time_hr.minute >= 19:
                            dd_time = 60*60 - 21*60
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
                        df_entry.to_csv(f'{script_name}_entry_signals.csv',index = False)
                        logger.info(f'fn out by time {dd_time} {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                        return
            else:
                # df_entry = df_entry.drop(rows_to_delete)
                # df_entry.reset_index(inplace= True)
                
                df_entry.to_csv(f'{script_name}_entry_signals.csv',index = False)
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




