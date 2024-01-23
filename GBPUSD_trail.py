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

# In[17]:
def entry_signal1(data,choice,index):
    """
        ValueOpen(5)[1] > ValueLow(5)[3]; ValueClose(5)[0] <= ValueLow(5)[1]; AvgTrueRange(10)[0] <= AvgTrueRange(10)[5]; CompositeRSI(2;24)[0] >= 30; rsi(close;2)[0] >= 10; 
        rateOfChange(close;10)[0] > rateOfChange(close;10)[4]
        close[1] > close[5]; open[2] <= open[7]; low[2] <= low[8]; ValueClose(5)[1] > ValueHigh(5)[2]; rateOfChange(close;5)[0] > rateOfChange(close;5)[2]; rateOfChange(close;10)[0] < rateOfChange(close;10)[1]
        open[2] > open[3]; low[5] <= low[6]; ValueClose(5)[1] > ValueClose(5)[4]; ValueLow(5)[3] <= ValueOpen(5)[5]; ValueClose(5)[1] <= ValueHigh(5)[5]; ParbolSAR(0.02;0.2)[0] = -1            
    variable_trail
    variable_sl_trail
    variable_sl_trail
    """
    index = index
    variable = None
    if choice == 1:
        """
            ValueOpen(5)[1] > ValueLow(5)[3]; ValueClose(5)[0] <= ValueLow(5)[1]; AvgTrueRange(10)[0] <= AvgTrueRange(10)[5]; CompositeRSI(2;24)[0] >= 30; rsi(close;2)[0] >= 10; 
        rateOfChange(close;10)[0] > rateOfChange(close;10)[4]     
        """
        condition =  (data.iloc[index-1]['ValueOpen'] > data.iloc[index-3]['ValueLow']) and (data.iloc[index]['ValueClose'] <= data.iloc[index-1]['ValueLow']) and \
            ((data.iloc[index]['ATR_10'] ) <= (data.iloc[index-2]['ATR_10'] )) \
        and  ((data.iloc[index]['compositersi'] ) >= 30) and (data.iloc[index]['rsi_2'] >= 10) and (data.iloc[index]['roc_10'] > data.iloc[index-4]['roc_10'] )
        variable = 'Trail'

    elif choice == 2:
        """
         close[1] > close[5]; open[2] <= open[7]; low[2] <= low[8]; ValueClose(5)[1] > ValueHigh(5)[2]; rateOfChange(close;5)[0] > rateOfChange(close;5)[2]; rateOfChange(close;10)[0] < rateOfChange(close;10)[1]
        """
        
        condition =  (data.iloc[index-1]['close'] > data.iloc[index-5]['close']) and (data.iloc[index-2]['open'] <= data.iloc[index-7]['open']) and ((data.iloc[index-2]['low'] <= data.iloc[index-8]['low']))\
        and (data.iloc[index-1]['ValueClose'] > data.iloc[index-2]['ValueHigh']) and (data.iloc[index]['roc_5'] > data.iloc[index-2]['roc_5']) and (data.iloc[index]['roc_10'] < data.iloc[index-1]['roc_10'] )
       
        variable = 'sl_Trail'
    elif choice == 3:
        """
        open[2] > open[3]; low[5] <= low[6]; ValueClose(5)[1] > ValueClose(5)[4]; ValueLow(5)[3] <= ValueOpen(5)[5]; ValueClose(5)[1] <= ValueHigh(5)[5]; ParbolSAR(0.02;0.2)[0] = -1          

        
        """
        condition =  (data.iloc[index-2]['open'] > data.iloc[index-3]['open']) and (data.iloc[index-5]['low'] <= data.iloc[index-6]['low']) \
        and (data.iloc[index-1]['ValueClose'] > data.iloc[index-4]['ValueClose']) and (data.iloc[index-3]['ValueLow'] <= data.iloc[index-5]['ValueLow'])and \
            (data.iloc[index-1]['ValueClose'] <= data.iloc[index-5]['ValueHigh']) and (data.iloc[index]['psar'] == -1) 
        variable = 'sl_Trail'
    elif choice == 4:
        """
        close[0] > low[9]; ValueLow(5)[0] > ValueOpen(5)[2]; ValueLow(5)[0] > ValueLow(5)[4]; ValueClose(5)[2] > ValueLow(5)[3]; ValueClose(5)[2] <= ValueHigh(5)[5]; AvgTrueRange(20)[0] > AvgTrueRange(20)[3]
        """

        condition =  (data.iloc[index]['close'] > data.iloc[index-9]['low']) and (data.iloc[index]['ValueLow'] > data.iloc[index-2]['ValueOpen']) \
        and (data.iloc[index]['ValueLow'] > data.iloc[index-4]['ValueLow']) and (data.iloc[index-2]['ValueClose'] > data.iloc[index-3]['ValueLow'])and \
            (data.iloc[index-2]['ValueClose'] <= data.iloc[index-5]['ValueHigh']) and (data.iloc[index]['ATR_20'] > data.iloc[index-3]['ATR_20']) 
        variable = 'Trail_ATR'
        

                    
    else:
        condition =  False

    if condition:
         return True,variable
    else:
         return False,variable





def Execution(script_name,symbol , PerCentageRisk , SL_TpRatio ,TP,SL,pipval,logger):
    #print(symbol)
    """
          close[4] > low[6]; open[0] <= open[3]; ValueLow(5)[4] > ValueLow(5)[5]; ValueHigh(5)[0] <= ValueClose(5)[4]; ValueHigh(5)[3] <= ValueClose(5)[5]; ValueLow(5)[0] <= ValueClose(5)[1]
        close[0] > high[8]; close[5] > open[6]; high[7] > close[9]; ValueOpen(5)[0] <= 6; ValueLow(5)[0] > -6; KeltnerChannel(c;20;1.5)[0] < KeltnerChannel(c;20;1.5)[1]
                        
    """
    time_hr = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))

    df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_H4 , 0 , 2700))

    logger.info(f'Running Event Loop for {symbol} at {datetime.now()}')
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

            
            
            df['ValueOpen'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'open')
            df['ValueLow'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'low')
            df['ValueHigh'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'high')
            df['ValueClose'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'close')
            
            df['ATR'] = sig.AvgTrueRange(df,7)
            df['ATR_10'] = sig.AvgTrueRange(df,10)
            df['ATR_20'] = sig.AvgTrueRange(df,20)
            df['compositersi'] = sig.CompositeRSI(df,2,24)
            df['rsi_2'] = sig.rsi(df,2)
            df['roc_10'] = sig.rateOfChange(df,10,(1/SL_TpRatio))
            df['roc_5'] = sig.rateOfChange(df,5,(1/SL_TpRatio))
            df['psar'] = sig.parbolsar(df,0.02,0.2)
           
           

        except AttributeError:
            if mt5.initialize():
                logger.info(f'connected {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            else:
                logger.info(f' not connected {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
                login = 25071028
                password = 'pB+#3#6FS3%j'
                server = 'Tickmill-Demo'

                mt5.initialize(login = login , password = password, server = server)
                #time.sleep(20)
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
        # try:                        
                
            # long Condition

            """
                low[0] > open[9]; low[2] > high[6]; open[5] > high[9]; low[6] > open[9]; low[0] <= low[1]; SMA(close;8)[0] > SMA(close;8)[3]
                
                high[3] > close[4]; open[1] <= close[4]; close[8] <= open[9]; open[7] <= close[9]; low[0] < SMA(close;8)[0]; EMA(close;8)[0] > EMA(close;8)[3]
                open[0] > low[2]; open[0] > close[8]; low[2] > high[6]; high[5] > close[6]; close[6] > high[9]; ValueOpen(5)[1] > ValueLow(5)[2]
                low[0] > open[7]; low[3] > open[4]; low[4] > open[5]; open[0] < HLMedian[0]; ValueLow(5)[2] > ValueLow(5)[4]; ValueOpen(5)[0] <= ValueHigh(5)[1]


                short conditions
                    ValueLow(5)[0] > -4; ValueHigh(5)[0] <= 12; ValueLow(5)[0] <= ValueOpen(5)[5]; ValueClose(5)[3] <= ValueLow(5)[4]; rateOfChange(close;3)[0] > rateOfChange(close;3)[4]; high[0] >= KeltnerChannel(c;20;1.5)[0]
                    open[1] > high[9]; open[2] > close[9]; low[5] > open[6]; ValueLow(5)[2] <= ValueHigh(5)[5]; KaufmanEfficiencyRatio(10)[0] < KaufmanEfficiencyRatio(10)[5]; Stochastics(14)[0] > Stochastics(14)[1]
                    open[0] > open[5]; close[1] > low[2]; close[5] > high[6]; open[5] > low[7]; Vix[0] > Vix[2]; ValueOpen(5)[0] > 0
                    open[1] > low[3]; high[1] > close[8]; high[3] > high[5]; open[0] > CubeHLC[0]; ValueOpen(5)[4] <= ValueLow(5)[5]; ValueLow(5)[0] <= ValueOpen(5)[3]
                    close[0] > close[3]; high[2] > low[3]; close[1] <= high[9]; ValueLow(5)[0] > ValueOpen(5)[4]; KeltnerChannel(c;20;1.5)[0] > KeltnerChannel(c;20;1.5)[1]; macdhist(c;12;26;9)[0] <= macdhist(c;12;26;9)[5]
                    high[1] > high[7]; close[2] > close[3]; low[2] <= open[8]; ValueHigh(5)[0] > ValueHigh(5)[2]; ValueHigh(5)[1] > ValueHigh(5)[4]; rateOfChange(close;5)[0] < rateOfChange(close;5)[1]
                    open[0] > low[5]; high[2] > open[7]; low[6] > close[8]; low[6] <= high[8]; OHLC[0] <= OHLC[5]; EMA(close;8)[0] < EMA(close;8)[1]
            
            """
            if df_entry.empty:
                for i in range(1,5):
                    
                    
                    signal = f'signal{i}'
                    condition, variable = entry_signal1(df,i,index)

                    if condition:
                        # Got Indication Candle
                        # Got Indication Candle
                        if variable == 'ATR':
                            flag = 2
                            time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                            logger.info(f'Got Indication Candle for ATR model {signal} {symbol} at {time1}')
                            print(f'Got Indication Candle  for signal  {symbol} at {time1}')
                            # index = -2
                            data = df.copy()
                            logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                            
                            LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[index]['ATR']*(1/SL_TpRatio)),2)
                            
                            order= market_order(symbol , LotSize,'buy',signal,1000+i )
                            tick = mt5.symbol_info_tick(symbol)
                            Price = tick.ask
                            SL_dis = SL
                            ATR = df.iloc[index]['ATR']
                            StopLoss = Price - SL_dis * ATR
                            TP_val = Price + TP * ATR
                            order_id = order.order
                            order_price = order.price
                            print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                            logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}  {flag}')
                            df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss,0,flag]

                        elif variable == 'Trail':
                            flag = 0
                            time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                            logger.info(f'Got Indication Candle for {signal} {symbol} at {time1}')
                            print(f'Got Indication Candle  for signal  {symbol} at {time1}')
                            # index = -2
                            data = df.copy()
                            logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                            SL_dis = 50
                            LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*50),2)
                            
                            order= market_order(symbol , LotSize,'buy',signal,1000+i )
                            tick = mt5.symbol_info_tick(symbol)
                            Price = tick.ask
                            
                            ATR = df.iloc[index]['ATR']
                            StopLoss = Price - SL_dis * SL_TpRatio
                            TP_val = Price + 30 * SL_TpRatio
                            order_id = order.order
                            order_price = order.price
                            print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                            logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}  {flag}')
                            df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss,0,flag]
                        elif variable == 'Trail_ATR':
                            flag = 0
                            time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                            logger.info(f'Got Indication Candle for {signal} {symbol} at {time1}')
                            print(f'Got Indication Candle  for signal  {symbol} at {time1}')
                            # index = -2
                            data = df.copy()
                            logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                            LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[index]['ATR']*(1/SL_TpRatio)),2)
                            
                            order= market_order(symbol , LotSize,'buy',signal,1000+i )
                            tick = mt5.symbol_info_tick(symbol)
                            Price = tick.ask
                            SL_dis = SL
                            ATR = df.iloc[index]['ATR']
                            StopLoss = Price - SL * ATR 
                            TP_val = Price + TP * ATR 
                            order_id = order.order
                            order_price = order.price
                            print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                            logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}  {flag}')
                            df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss,0,flag]
                        elif variable == 'sl_Trail':
                            flag = 5
                            time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                            logger.info(f'Got Indication Candle for sl trail {signal} {symbol} at {time1}')
                            print(f'Got Indication Candle  for signal  {symbol} at {time1}')
                            # index = -2
                            data = df.copy()
                            logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")
                            tick = mt5.symbol_info_tick(symbol)
                            Price = tick.ask
                            sl = Price - 0.5*0.01*Price
                            tp = Price + 0.5*0.01*Price
                            tp1 = Price + 0.25*0.01*Price
                            SL_dis = abs(sl - Price)*(1/SL_TpRatio)
                            LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL_dis),2)
                            
                            order= market_order(symbol , LotSize,'buy',signal,1000+i )
                            tick = mt5.symbol_info_tick(symbol)
                            Price = tick.ask
                            
                            ATR = df.iloc[index]['ATR']
                            StopLoss = sl
                            TP_val = tp
                            order_id = order.order
                            order_price = order.price
                            print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                            logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}  {flag}')
                            df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss,tp1,flag]
                        
                    else:
                        
                        logger.info(f"No entry for {signal}  close : {df.iloc[index]['close']} {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}")  
                    
                    
                  
            else:
                column_name = 'signals'
                for i in range(1,5):
                    
                    signal = f'signal{i}'
                    if df_entry[column_name].eq(i).any():
                        logger.info(f"The {signal} entry exists ")      

                    else:
                        condition, variable = entry_signal1(df,i,index)

                        if condition:
                            # Got Indication Candle
                            # Got Indication Candle
                            if variable == 'ATR':
                                flag = 2
                                time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                                logger.info(f'Got Indication Candle for ATR model {signal} {symbol} at {time1}')
                                print(f'Got Indication Candle  for signal  {symbol} at {time1}')
                                # index = -2
                                data = df.copy()
                                logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                                
                                LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[index]['ATR']*(1/SL_TpRatio)),2)
                                
                                order= market_order(symbol , LotSize,'buy',signal,1000+i )
                                tick = mt5.symbol_info_tick(symbol)
                                Price = tick.ask
                                SL_dis = SL
                                ATR = df.iloc[index]['ATR']
                                StopLoss = Price - SL_dis * ATR
                                TP_val = Price + TP * ATR
                                order_id = order.order
                                order_price = order.price
                                print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                                logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}  {flag}')
                                df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss,0,flag]

                            elif variable == 'Trail':
                                flag = 0
                                time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                                logger.info(f'Got Indication Candle for {signal} {symbol} at {time1}')
                                print(f'Got Indication Candle  for signal  {symbol} at {time1}')
                                # index = -2
                                data = df.copy()
                                logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                                SL_dis = 50
                                LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*50),2)
                                
                                order= market_order(symbol , LotSize,'buy',signal,1000+i )
                                tick = mt5.symbol_info_tick(symbol)
                                Price = tick.ask
                                
                                ATR = df.iloc[index]['ATR']
                                StopLoss = Price - SL_dis * SL_TpRatio
                                TP_val = Price + 30 * SL_TpRatio
                                order_id = order.order
                                order_price = order.price
                                print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                                logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}  {flag}')
                                df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss,0,flag]
                            elif variable == 'sl_Trail':
                                flag = 5
                                time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                                logger.info(f'Got Indication Candle for sl trail {signal} {symbol} at {time1}')
                                print(f'Got Indication Candle  for signal  {symbol} at {time1}')
                                # index = -2
                                data = df.copy()
                                logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")
                                tick = mt5.symbol_info_tick(symbol)
                                Price = tick.ask
                                sl = Price - 0.5*0.01*Price
                                tp = Price + 0.5*0.01*Price
                                tp1 = Price + 0.25*0.01*Price
                                SL_dis = abs(sl - Price)*(1/SL_TpRatio)
                                LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL_dis),2)
                                
                                order= market_order(symbol , LotSize,'buy',signal,1000+i )
                                tick = mt5.symbol_info_tick(symbol)
                                Price = tick.ask
                                
                                ATR = df.iloc[index]['ATR']
                                StopLoss = sl
                                TP_val = tp
                                order_id = order.order
                                order_price = order.price
                                print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                                logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}  {flag}')
                            
                                df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss,tp1,flag]
                            elif variable == 'Trail_ATR':
                                flag = 0
                                time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                                logger.info(f'Got Indication Candle for {signal} {symbol} at {time1}')
                                print(f'Got Indication Candle  for signal  {symbol} at {time1}')
                                # index = -2
                                data = df.copy()
                                logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                                LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[index]['ATR']*(1/SL_TpRatio)),2)
                                
                                order= market_order(symbol , LotSize,'buy',signal,1000+i )
                                tick = mt5.symbol_info_tick(symbol)
                                Price = tick.ask
                                SL_dis = SL
                                ATR = df.iloc[index]['ATR']
                                StopLoss = Price - SL * ATR
                                TP_val = Price + TP * ATR
                                order_id = order.order
                                order_price = order.price
                                print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                                logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}  {flag}')
                                df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss,0,flag]
                        else:
                        
                            logger.info(f"No entry for {signal}  close : {df.iloc[index]['close']} {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}")  
                    
                            
                

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
                                        
                                            if Price <= row['SL']:
                                                    time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                    print(f'SL Hit at{time_s} ')
                                                    close = close_order(row['orderid'])
                                                    logger.info(f"SL hit long {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']},{close.comment}  ")
                                                    if close.comment == 'Request executed':

                                                        rows_to_delete.append(index)
                                            elif (Price >= row['TP']) and (row['flag'] == 0):
                                                time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                row['SL'] = row['price_open'] + 1*(SL_TpRatio)
                                                row['TP'] = row['TP'] + 1*(SL_TpRatio)
                                                row['flag'] = 1
                                                logger.info(f"Trail 1  hit long {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']}  ")
                                            elif (Price >= row['TP']) and (row['flag'] == 1):
                                                time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                row['SL'] = row['SL'] + 1*(SL_TpRatio)
                                                row['TP'] = row['TP'] + 1*(SL_TpRatio)
                                                logger.info(f"Trail next  hit long {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']} ")

                                                # TP Hit
                                                # Trailing Triggere
                                            elif (Price >= row['TP']) and ((row['flag'] == 2) or (row['flag'] >= 5)):
                                                    time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                    print(f'TP Hit at{time_s} ')
                                                    close = close_order(row['orderid'])
                                                    logger.info(f"TP  hit long {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']},{close.comment}  ")
                                                    if close.comment == 'Request executed':

                                                        rows_to_delete.append(index)
                                            elif (Price >= row['TP1']) and (row['flag'] == 5):
                                                time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                row['SL'] = row['TP1'] - 10*(SL_TpRatio)
                                                row['TP'] = row['TP'] + 1*(SL_TpRatio)
                                                row['flag'] = 6
                                                logger.info(f"Trail sl   hit long {time_s} SL at {row['SL']} PT {row['TP']}, {row['TP1']},{row['signals']}  ")
                                            elif (Price >= row['TP1']) and (row['flag'] == 6):
                                                time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                row['SL'] = row['SL'] + 1*(SL_TpRatio)
                                                row['TP'] = row['TP'] + 1*(SL_TpRatio)
                                            
                                                logger.info(f"Trail sl   hit long {time_s} SL at {row['SL']} PT {row['TP']}, {row['TP1']},{row['signals']} ")
                                            

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
                        
                                        
                                        


                            

        # except AttributeError:
        #     if mt5.initialize():
        #         logger.info('connnected in loop')
        #     else:
        #         logger.info(f' not connected ifelse{datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
        #         login = 51313012
        #         password = 'JqKKQHdc'
        #         server = 'ICMarketsSC-Demo'
        #         mt5.initialize(login = login , password = password, server = server)
        #         #time.sleep(20)
        #         logger.info(f'connected ,{mt5.initialize()} , {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
        #     continue
        # break

    
                    


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




