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
def entry_signal1(data,choice):
    """
        ValueHigh(5)[0] <= 6; ValueHigh(5)[0] > ValueOpen(5)[3]; ValueClose(5)[2] > ValueOpen(5)[3]; ValueClose(5)[0] <= ValueLow(5)[5]; SMA(close;10)[0] > SMA(close;10)[3]; close[0] <= CompositeSMA(8;20;50;200)[0]
            
    """
    index = -2
    if choice == 1:
         
        return (data.iloc[index]['ValueHigh'] <= 6) and (data.iloc[index]['ValueHigh'] > data.iloc[index - 3]['ValueOpen']) \
        and (data.iloc[index-2]['ValueClose'] > data.iloc[index - 3]['ValueOpen']) and (data.iloc[index]['ValueClose'] <= data.iloc[index - 5]['ValueLow']) \
            and (data.iloc[index]['sma_10'] > data.iloc[index -3]['sma_10']) and (data.iloc[index]['close'] <= data.iloc[index]['composite_sma']) 

    
    elif choice == 2:
        """
                        
            close[0] > low[4]; high[1] > low[8]; OHLC[0] > OHLC[1]; ValueLow(5)[1] <= ValueOpen(5)[3]; momentum(close;10)[0] < momentum(close;10)[5]; SMA(close;100)[0] < SMA(close;100)[5]                
            
        """

        return (data.iloc[index]['close'] > data.iloc[index - 4]['low']) and (data.iloc[index - 1]['high'] > data.iloc[index - 8]['low']) and (data.iloc[index]['OHLC'] > data.iloc[index - 1]['OHLC']) \
    and (data.iloc[index-1]['ValueLow'] <= data.iloc[index - 3]['ValueOpen']) and (data.iloc[index]['momentum_10'] < data.iloc[index-5]['momentum_10']) and (data.iloc[index]['sma_100'] < data.iloc[index - 5]['sma_100'])

    elif choice == 3:
        """
                    
            open[5] > high[8]; OHLC[0] <= OHLC[5]; ValueClose(5)[2] > ValueLow(5)[5]; ValueLow(5)[2] <= ValueClose(5)[3]; momentum(close;3)[0] < 0; momentum(close;3)[0] < momentum(close;3)[4]
        """
    
        return (data.iloc[index-5]['open'] > data.iloc[index - 8]['high']) and (data.iloc[index]['OHLC'] <= data.iloc[index - 5]['OHLC'])and (data.iloc[index -2 ]['ValueClose'] > data.iloc[index - 5]['ValueLow']) \
        and (data.iloc[index-2]['ValueLow'] <= data.iloc[index - 3]['ValueClose']) \
    and (data.iloc[index]['momentum_3'] < data.iloc[index -4]['momentum_3']) and (data.iloc[index]['momentum_3'] < 0)
    elif choice == 4:
         
        """
                close[0] > low[8]; open[2] > high[8]; low[0] <= high[2]; ValueClose(5)[1] <= ValueOpen(5)[2]; SuperSmoother[0] <= SuperSmoother[2]; close[0] <= CompositeEMA(8;20;50;200)[0]
        """
    
        return (data.iloc[index]['close'] > data.iloc[index - 8]['low']) and (data.iloc[index - 2]['open'] > data.iloc[index - 8]['high']) and (data.iloc[index]['low'] <= data.iloc[index - 2]['high']) \
    and (data.iloc[index - 1]['ValueClose'] <= data.iloc[index-2]['ValueOpen']) and (data.iloc[index]['SuperSmoother'] <= data.iloc[index-2]['SuperSmoother'])  and (data.iloc[index]['close'] <= data.iloc[index]['composite_ema']) 

    elif choice == 5:
         
        """
            open[2] > open[8]; low[2] <= high[4]; (open[0] >= low[1]) AND (open[0] <= min(open[1][1];close[1][1])); ValueHigh(5)[2] <= ValueOpen(5)[5]; CompositeEMA(8;20;50;200)[0] <= CompositeEMA(8;20;50;200)[1]    
        """
    
        return False
    # return False
    elif choice == 6:
         
        """
            close[2] > low[6]; open[1] <= low[3]; open[8] <= high[9]; ValueOpen(5)[1] <= ValueHigh(5)[3]; ValueHigh(5)[0] <= ValueHigh(5)[3]; high[0] < EMA(close;20)[0]
        """
        return False
        return (data.iloc[index-2]['close'] > data.iloc[index - 6]['low']) and (data.iloc[index - 1]['open'] <= data.iloc[index - 3]['low']) and (data.iloc[index-8]['open'] <= data.iloc[index - 9]['high']) \
            and (data.iloc[index - 1]['ValueOpen'] <= data.iloc[index-3]['ValueHigh']) and (data.iloc[index]['ValueHigh'] <= data.iloc[index-3]['ValueHigh'])  and (data.iloc[index]['high'] < data.iloc[index]['ema_20']) 

    elif choice == 7:
         
        """
            high[1] > open[4]; open[5] <= close[6]; ValueHigh(5)[0] <= ValueOpen(5)[3]; ValueLow(5)[0] <= ValueLow(5)[3]; CompositeRSI(2;24)[0] <= 40; rateOfChange(close;10)[0] < 0            
        """
        return (data.iloc[index]['high'] > data.iloc[index - 4]['open']) and (data.iloc[index - 5]['open'] <= data.iloc[index - 6]['close']) and (data.iloc[index]['ValueHigh'] <= data.iloc[index - 3]['ValueOpen']) \
             and (data.iloc[index ]['ValueLow'] <= data.iloc[index-3]['ValueLow']) and (data.iloc[index]['composite_rsi'] <= 40)  and (data.iloc[index]['ROC'] < 0) 

    
    elif choice == -1:
        """
            high[5] > high[7]; open[4] <= high[5]; ValueClose(5)[2] > ValueOpen(5)[5]; ValueClose(5)[1] <= ValueClose(5)[4]; low[0] > SMA(close;10)[0]; KaufmanEfficiencyRatio(10)[0] < KaufmanEfficiencyRatio(10)[5]            
        
        """
        return (data.iloc[index-5]['high'] > data.iloc[index-7]['high']) and (data.iloc[index-4]['open'] <= data.iloc[index-5]['high']) and ((data.iloc[index-2]['ValueClose'] ) > (data.iloc[index-5]['ValueOpen'] )) \
        and  ((data.iloc[index-1]['ValueClose'] ) <= (data.iloc[index-4]['ValueClose']  )) and (data.iloc[index]['low'] > data.iloc[index]['sma_10']) and \
        (data.iloc[index]['kaufmaneff_10'] < data.iloc[index-5]['kaufmaneff_10'])
    elif choice == -2:
        """
                low[2] > low[9]; high[4] > open[6]; ValueLow(5)[1] > ValueLow(5)[3]; ValueOpen(5)[3] <= ValueClose(5)[5]; high[0] >= highest(high;5)[0]; Hurst(20)[0] > Hurst(20)[1]        """

        return (data.iloc[index - 2]['low'] > data.iloc[index-9]['low']) and (data.iloc[index - 4]['high'] > data.iloc[index-6]['open']) and (data.iloc[index - 1]['ValueLow'] > data.iloc[index-3]['ValueLow'])\
        and (data.iloc[index - 3]['ValueOpen'] <= data.iloc[index-5]['ValueClose']) and (data.iloc[index]['high'] >= data.iloc[index]['highest_5']) and\
              (data.iloc[index]['hurst_20'] > data.iloc[index-1]['hurst_20'])
    elif choice == -3:
        #  close[0] > high[6]; high[3] > close[8]; low[4] <= low[6]; ValueLow(5)[1] > ValueLow(5)[5]; consecutive(open;2;1)[0] = 1; close[0] > SMA(close;10)[0]

        return (data.iloc[index ]['close'] > data.iloc[index-6]['high']) and (data.iloc[index - 3]['high'] > data.iloc[index-8]['close']) and (data.iloc[index - 4]['low'] <= data.iloc[index-6]['low'])\
        and (data.iloc[index-1]['ValueLow'] > data.iloc[index -5]['ValueLow']) and (data.iloc[index]['cons_open'] == 1)  and\
              (data.iloc[index]['close'] > data.iloc[index]['sma_10'])
    elif choice == -4:
        #  low[0] <= low[1]; high[0] <= low[2]; low[0] <= high[4]; open[0] <= high[6]; high[4] <= close[9]; volume[0] >= SMA(volume;50)[0]
        return False
        return (data.iloc[index-1]['high'] > data.iloc[index-7]['high']) and (data.iloc[index - 2]['close'] > data.iloc[index-3]['close']) and (data.iloc[index - 2]['low'] <= data.iloc[index-8]['open'])\
         and (data.iloc[index]['ValueHigh'] > data.iloc[index-2]['ValueHigh']) and (data.iloc[index-1]['ValueHigh'] > data.iloc[index-4]['ValueHigh'] ) and\
            (data.iloc[index]['ROC_5'] < data.iloc[index-1]['ROC_5'])
    
    elif choice == -5:
        """
        
        low[3] > low[6]; high[7] > high[8]; ValueLow(5)[1] > ValueLow(5)[2]; ValueLow(5)[0] <= ValueClose(5)[1]; IBR[0] >= 50; BollingerBand(c;20;-2)[0] > BollingerBand(c;20;-2)[1]
        """
        return (data.iloc[index-3]['low'] > data.iloc[index-6]['low']) and (data.iloc[index - 7]['high'] > data.iloc[index-8]['high']) and (data.iloc[index - 1]['ValueLow'] > data.iloc[index-2]['ValueLow'])\
         and (data.iloc[index]['ValueLow'] <= data.iloc[index-1]['ValueClose']) and (data.iloc[index]['IBR'] >=  50 ) and\
            (data.iloc[index]['b_lower'] > data.iloc[index-1]['b_lower'])

                    
    else:
        return False





def Execution(symbol , PerCentageRisk , SL_TpRatio ,TP,SL,pipval,logger):
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

            df['kaufmaneff_10'] = sig.KaufmanEfficiencyRatio(df,10)
            df['hurst_20'] = sig.Hurst(df,20)
            df['highest_5'] = sig.highest(df,5)
            df['cons_open'] = sig.consecutive(df,'open',2,1)
            df['b_lower'] = sig.BollingerBand(df,20,-2)
            df['IBR'] = sig.IBR(df)

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
    df.to_csv(f'{symbol}_dataframe')
    df_entry = pd.read_csv(f'{symbol}_entry_signals.csv')
    for i in range(1):
        # 
        # try:                        
                
            # long Condition

            """
                 ValueHigh(5)[0] <= 6; ValueHigh(5)[0] > ValueOpen(5)[3]; ValueClose(5)[2] > ValueOpen(5)[3]; ValueClose(5)[0] <= ValueLow(5)[5]; SMA(close;10)[0] > SMA(close;10)[3]; close[0] <= CompositeSMA(8;20;50;200)[0]
                close[0] > low[4]; high[1] > low[8]; OHLC[0] > OHLC[1]; ValueLow(5)[1] <= ValueOpen(5)[3]; momentum(close;10)[0] < momentum(close;10)[5]; SMA(close;100)[0] < SMA(close;100)[5]
                open[5] > high[8]; OHLC[0] <= OHLC[5]; ValueClose(5)[2] > ValueLow(5)[5]; ValueLow(5)[2] <= ValueClose(5)[3]; momentum(close;3)[0] < 0; momentum(close;3)[0] < momentum(close;3)[4]
                close[0] > low[8]; open[2] > high[8]; low[0] <= high[2]; ValueClose(5)[1] <= ValueOpen(5)[2]; SuperSmoother[0] <= SuperSmoother[2]; close[0] <= CompositeEMA(8;20;50;200)[0]

                open[0] > close[1]; high[3] > close[8]; close[0] <= open[8]; close[4] <= high[8]; open[7] <= open[9]; volume[0] > volume[4]
                open[3] > open[4]; high[5] > open[6]; high[4] <= close[6]; low[7] <= high[9]; volume[0] <= volume[4]; ValueOpen(5)[0] > ValueLow(5)[1]
                high[1] > open[4]; open[5] <= close[6]; ValueHigh(5)[0] <= ValueOpen(5)[3]; ValueLow(5)[0] <= ValueLow(5)[3]; CompositeRSI(2;24)[0] <= 40; rateOfChange(close;10)[0] < 0

                short conditions
                high[5] > high[7]; open[4] <= high[5]; ValueClose(5)[2] > ValueOpen(5)[5]; ValueClose(5)[1] <= ValueClose(5)[4]; low[0] > SMA(close;10)[0]; KaufmanEfficiencyRatio(10)[0] < KaufmanEfficiencyRatio(10)[5]
                low[2] > low[9]; high[4] > open[6]; ValueLow(5)[1] > ValueLow(5)[3]; ValueOpen(5)[3] <= ValueClose(5)[5]; high[0] >= highest(high;5)[0]; Hurst(20)[0] > Hurst(20)[1]
                close[0] > high[6]; high[3] > close[8]; low[4] <= low[6]; ValueLow(5)[1] > ValueLow(5)[5]; consecutive(open;2;1)[0] = 1; close[0] > SMA(close;10)[0]
                low[0] <= low[1]; high[0] <= low[2]; low[0] <= high[4]; open[0] <= high[6]; high[4] <= close[9]; volume[0] >= SMA(volume;50)[0]
                low[3] > low[6]; high[7] > high[8]; ValueLow(5)[1] > ValueLow(5)[2]; ValueLow(5)[0] <= ValueClose(5)[1]; IBR[0] >= 50; BollingerBand(c;20;-2)[0] > BollingerBand(c;20;-2)[1]
            """
            if df_entry.empty:
                for i in range(1,6):
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
                        
                        order= market_order(symbol , LotSize,'buy',signal,1000+i )
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
                        index = -2
                        logger.info(f"No entry for {signal} close:{df.iloc[-2]['close']} indication candle time: {df.iloc[index]['time']} current: {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}") 
                    signal = f'signal{i}_short'
                    if entry_signal1(df,-i):
                        # Got Indication Candle
                        # Got Indication Candle
                        
                        if i == 5:
                            TP,SL = 2,2.5
                        else:
                            TP,SL = 2,3

                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.info(f'Got Indication Candle for {signal} {symbol} at {time1}')
                        print(f'Got Indication Candle  for signal short {symbol} at {time1}')
                        index = -2
                        data = df.copy()
                        logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                        
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                        
                        order= market_order(symbol , LotSize,'sell',signal,1100+i )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.bid
                        SL_dis = SL
                        ATR = df.iloc[-2]['ATR']
                        StopLoss = Price + SL_dis * ATR
                        TP_val = Price - TP * ATR
                        order_id = order.order
                        order_price = order.price
                        print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                        df_entry.loc[len(df_entry)] = [-i,order_id,order.volume,Price,TP_val,StopLoss]
                    else:
                        index = -2
                        logger.info(f"No entry for {signal} close:{df.iloc[index]['close']} indication candle time: {df.iloc[index]['time']} current: {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}")    
                    
                    
                  
            else:
                column_name = 'signals'
                for i in range(1,6):
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
                            
                            
                            order= market_order(symbol , LotSize,'buy',signal,1000+i )
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
                            index = -2
                            logger.info(f"No entry for {signal} close:{df.iloc[index]['close']} indication candle time: {df.iloc[index]['time']} \
                                        current: {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}")                     
                            
                    signal = f'signal{i}_short'
                    if df_entry[column_name].eq(-i).any():
                        logger.info(f"The {signal} entry exists ")      

                    else:
                        if entry_signal1(df,-i):
                        # Got Indication Candle
                        # Got Indication Candle
                            if i == 5:
                                TP,SL = 2,2.5
                            else:
                                TP,SL = 2,3
                            signal = f'signal{i}_short'
                            time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                            logger.info(f'Got Indication Candle for {signal} {symbol} at {time1}')
                            print(f'Got Indication Candle  for signal short {symbol} at {time1}')
                            index = -2
                            data = df.copy()
                            logger.info(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                            
                            LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*SL*df.iloc[-2]['ATR']*(1/SL_TpRatio)),2)
                            
                            order= market_order(symbol , LotSize,'sell',signal,1100+i )
                            tick = mt5.symbol_info_tick(symbol)
                            Price = tick.bid
                            SL_dis = SL
                            ATR = df.iloc[-2]['ATR']
                            StopLoss = Price + SL_dis * ATR
                            TP_val = Price - TP * ATR
                            order_id = order.order
                            order_price = order.price
                            print(f'Entry at {time1} for    {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} ')
                            logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}')
                            df_entry.loc[len(df_entry)] = [-i,order_id,order.volume,Price,TP_val,StopLoss]
                        else:
                            index = -2
                            logger.info(f"No entry for {signal} close:{df.iloc[index]['close']} indication candle time: {df.iloc[index]['time']} \
                                        current: {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}") 
                     
                

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
                            dd_time = 60*60 - 50
                    
                    if (  (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)) - time_hr).seconds < dd_time:

                        if (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)).weekday() !=5 and (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)).weekday() !=6:
                                
                                # SL , TP check
                                
                            Price = mt5.symbol_info_tick(symbol).bid
                            Price1 = mt5.symbol_info_tick(symbol).ask
                                    # SL Hit
                            for index, row in df_entry.iterrows():
                                try:
                                    if index not in rows_to_delete:
                                        if row['signals'] > 0:

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
                                        else:
                                            if Price1 >= row['SL']:
                                                    time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                    print(f'SL Hit at{time_s} ')
                                                    close = close_order(row['orderid'])
                                                    logger.info(f"SL hit short {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']},{close.comment}  ")
                                                    rows_to_delete.append(index)

                                                # TP Hit
                                                # Trailing Triggere
                                            elif Price1 <= row['TP']:
                                                    time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                                    print(f'TP Hit at{time_s} ')
                                                    close = close_order(row['orderid'])
                                                    logger.info(f"TP  hit short {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']},{close.comment}  ")
                                                    rows_to_delete.append(index)

                                except:
                                     continue

                                        
                    else:
                        df_entry = df_entry.drop(rows_to_delete)
                        df_entry.reset_index(inplace= True)
                        df_entry.drop('index', axis=1, inplace=True)
                        df_entry.to_csv(f'{symbol}_entry_signals.csv',index = False)
                        logger.info(f'fn out by time {dd_time} {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                        return
            else:
                # df_entry = df_entry.drop(rows_to_delete)
                # df_entry.reset_index(inplace= True)
                
                df_entry.to_csv(f'{symbol}_entry_signals.csv',index = False)
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




