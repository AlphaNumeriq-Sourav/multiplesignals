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

    return order_result





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

            return order_result

    return 'Ticket does not exist'




# -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------
# Function to Get H4 Forex Signals for EURUSD 
# Signal 1 = high[2] > close[9]; low[5] > open[9]; open[6] > close[8]; low[4] <= high[8]; ValueHigh(5)[0] <= ValueOpen(5)[5]
# -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------

def entry_signal1(data,choice,index):
    index = index
    variable = None
    
    
    '''
    high[2] > close[9]; low[5] > open[9]; open[6] > close[8]; low[4] <= high[8]; ValueHigh(5)[0] <= ValueOpen(5)[5]; 
    WinsLast(close;5)[0] >= 1
    '''
    
    if choice == 1:
        condition = (data.iloc[index-2]['high'] > data.iloc[index-9]['close']) and \
                    (data.iloc[index-5]['low'] > data.iloc[index-9]['open']) and \
                    (data.iloc[index-6]['open'] > data.iloc[index-8]['close']) and \
                    (data.iloc[index-4]['low'] <= data.iloc[index-8]['high'] ) and \
                    (data.iloc[index-0]['ValueHigh'] <= data.iloc[index-5]['ValueOpen']) and \
                    (data.iloc[index-0]['WinsLast'] >= 1)
                    
        variable = 'Trail'    
    else:
        condition =  False

    if condition:
         return True,variable
    else:
         return False,variable











# -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------
# Function to Execute the Trades of EURUSD when a New signal comes from signal 1 and also to Exit the Trades Also
# -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------


def Execution(script_name,symbol , PerCentageRisk , SL_TpRatio ,TP,SL,pipval,logger):
    time_hr = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))

    df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_H4 , 0 , 2700))

    logger.debug(f'Running Event Loop of Instrument:{symbol} at ServerTime : {datetime.now()}  BrokerTime : {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}  for the New Short Signal Modified by Sourav')

    # -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------
    # Logic to Get the H4 DataFrame for the Instrument
    # -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------

    
    for i in range(2):
        try: 
            df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_H4 , 0 , 2700))
            df['time']= df['time'].map(lambda Date : datetime.fromtimestamp(Date) -  timedelta(hours= 3))

            time_hr = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
            logger.debug(f"Checking DataFrameLastIndex and BrokerTime of Instrument : {symbol} BrokerTime: {time_hr} H4DfLastIndex : {df.iloc[-1]['time']}")

            for i in range(5):
                if  (df.iloc[-1]['time'].hour == time_hr.hour) or (df.iloc[-1]['time'].hour > time_hr.hour) or ((df.iloc[-1]['time'].hour == 0) and (time_hr.hour >=23)):
                     index = -2
                     break
                else:
                    df = pd.DataFrame(mt5.copy_rates_from_pos(symbol ,mt5.TIMEFRAME_H4, 0 , 2700))
                    index = -1
                    df['time']= df['time'].map(lambda Date : datetime.fromtimestamp(Date) -  timedelta(hours= 3))
                    time_false = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                    logger.debug(f"Retrying getting Latest candle for H4data of Instrument : {symbol} FalseBrokerTime: {time_hr} H4DfLastIndex : {df.iloc[-1]['time']} NowBrokerTime : {time_false}")
                    if  (df.iloc[-1]['time'].hour == time_hr.hour) or (df.iloc[-1]['time'].hour > time_hr.hour) or ((df.iloc[-1]['time'].hour == 0) and (time_hr.hour >=23)):
                     index = -2
                

            
            
            df['ValueOpen'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'open')
            df['ValueLow'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'low')
            df['ValueHigh'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'high')
            df['ValueClose'] = sig.ValueCharts(df,5,(1/SL_TpRatio),'close')
            df['WinsLast'] = sig.WinsLast(df, 5 , column='close')
            
            df['ATR'] = sig.AvgTrueRange(df,7)
           
            
            df['rsi_14'] = sig.rsi(df,14)
            df['OHLC'] = sig.OHLC(df)
            df['sma_5'] = sig.SMA(df,5)
            df['sma_20'] = sig.SMA(df,20)
           
           

        except AttributeError:
            if mt5.initialize():
                logger.info(f'MT5 Connect Reestablished at BrokerTime : {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            else:
                logger.error(f'MT5 Connection Not able to connect at BrokerTime : {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}  Again Trying......')
                login = 25071028
                password = 'pB+#3#6FS3%j'
                server = 'Tickmill-Demo'

                mt5.initialize(login = login , password = password, server = server)
                #time.sleep(20)
                logger.debug(f'MT5 Connect Reestablished after Retry Status : {mt5.initialize()}  at BrokerTime : {datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3)}')
            continue
        break
    
    
    
    
    
    
    
    
    df.to_csv(f'{script_name}_dataframe')
    df_entry = pd.read_csv(f'{script_name}_entry_signals.csv')
    if 'TP1' not in df_entry.columns:
         df_entry['TP1'] = None
    if 'flag' not in df_entry.columns:
         df_entry['flag'] = None
         
    # -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------
    # Logic to Push the Market Order to the Broker One we got any signals if we don't have active trade from the signals
    # -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------

    if df_entry.empty:
        
        for i in range(1,2):
            
            
            signal = f'signal{i}'
            condition, variable = entry_signal1(df,i,index)

            if condition:
                # Got Indication Candle
                if variable == 'Trail':
                    flag = 0
                    time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                    logger.debug(f'Got Short Indication Candle for {signal} {symbol} at BrokerTime : {time1}')
                    data = df.copy()
                    logger.debug(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                    SL_dis = 50
                    LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*50),2)
                    
                    order= market_order(symbol , LotSize,'sell','minors_short_h4',3001+i )
                    tick = mt5.symbol_info_tick(symbol)
                    Price = tick.bid
                    
                    ATR = df.iloc[index]['ATR']
                    StopLoss = Price + (SL_dis * SL_TpRatio)
                    TP_val = Price - (30 * SL_TpRatio)
                    order_id = order.order
                    order_price = order.price
                    logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}  {flag}')
                    df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss,0,flag]
                
                
            else:
                
                logger.debug(f"No entry for {signal} of Instrument : {symbol}  close : {df.iloc[index]['close']} at BrokerTime : {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}")  
            
            
    # -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------
    # Logic to Push the Market Order to the Broker One we got any signal2 if we  have active trade from the signal1 and Vice versa
    # -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------
     
    else:
        column_name = 'signals'
        for i in range(1,2):
            
            signal = f'signal{i}'
            if df_entry[column_name].eq(i).any():
                logger.debug(f"The {signal} entry exists ")      

            else:
                condition, variable = entry_signal1(df,i,index)

                if condition:
                    # Got Indication Candle
                    
                    if variable == 'Trail':
                        flag = 0
                        time1 = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time)- timedelta(hours=3))
                        logger.debug(f'Got Short Indication Candle for {signal} {symbol} at {time1}')
                        # index = -2
                        data = df.copy()
                        logger.debug(f"{data.iloc[index]['close']} atr: {data.iloc[index]['ATR']} ")


                        SL_dis = 50
                        LotSize = round((PerCentageRisk * mt5.account_info().equity)/(pipval*50),2)
                        
                        order= market_order(symbol , LotSize,'sell','minors_short_h4',3001+i )
                        tick = mt5.symbol_info_tick(symbol)
                        Price = tick.bid
                        
                        ATR = df.iloc[index]['ATR']
                        StopLoss = Price + (SL_dis * SL_TpRatio)
                        TP_val = Price - (30 * SL_TpRatio)
                        order_id = order.order
                        order_price = order.price
                        logger.info(f'Entry at {time1} for {symbol}  , SL : {StopLoss} , TP : {TP_val} ,Lotsize : {LotSize} , OrderPrice : {Price}, comment : {order.comment}  {flag}')
                        df_entry.loc[len(df_entry)] = [i,order_id,order.volume,Price,TP_val,StopLoss,0,flag]
                    
                else:
                
                    logger.debug(f"No entry for {signal}  close : {df.iloc[index]['close']} {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}")  
            
                    
                    
                    
                    
                    
                    
                    
                    
                    
        
    # -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------
    # Logic to Exit the Short Trades if hits SL and also the trailing Part
    # -------------------------x-----------------------x---------------------------x---------------------------x---------------------------x---------------------------
    if not df_entry.empty:
        rows_to_delete = []
        logger.debug(f'Entry happened for {symbol} , Checking for Exit.....')
                        
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
                        
                    Price = mt5.symbol_info_tick(symbol).ask
                    Price1 = mt5.symbol_info_tick(symbol).ask
                            # SL Hit
                    for index, row in df_entry.iterrows():  
                        try:
                            if index not in rows_to_delete:
                                
                                    if Price >= row['SL']:
                                            time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                            print(f'SL Hit at{time_s} ')
                                            close = close_order(row['orderid'])
                                            logger.info(f"SL hit Short BrokerTime : {time_s} SL : {row['SL']} TP : {row['TP']} ,{row['signals']},{close.comment}  ")
                                            if close.comment == 'Request executed':
                                                rows_to_delete.append(index)
                                    elif (Price <= row['TP']) and (row['flag'] == 0):
                                        time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                        row['SL'] = row['price_open'] - 1*(SL_TpRatio)
                                        row['TP'] = row['TP'] - 1*(SL_TpRatio)
                                        row['flag'] = 1
                                        logger.debug(f"Trail 1  hit Short {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']}  ")
                                    elif (Price <= row['TP']) and (row['flag'] == 1):
                                        time_s = (datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))
                                        row['SL'] = row['SL'] - 1*(SL_TpRatio)
                                        row['TP'] = row['TP'] - 1*(SL_TpRatio)
                                        logger.debug(f"Trail next  hit Short {time_s} SL at {row['SL']} PT {row['TP']},{row['signals']} ")

                                        
                                    

                        except:
                                continue

                                
            else:
                df_entry = df_entry.drop(rows_to_delete)
                df_entry.reset_index(inplace= True)
                df_entry.drop('index', axis=1, inplace=True)
                df_entry.to_csv(f'{script_name}_entry_signals.csv',index = False)
                logger.debug(f'Function Out after the Exit trade of {symbol} NextSignalCheckTime : {dd_time} at BrokerTime : {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
                return
    else:
        df_entry.to_csv(f'{script_name}_entry_signals.csv',index = False)
        logger.debug(f'Function Out of {symbol} NextSignalCheckTime {(datetime.fromtimestamp(mt5.symbol_info_tick(symbol).time) - timedelta(hours=3))}') 
        time.sleep(1300)
        return
                        
                                        
                                        






if __name__ == '__main__':
    Execution()







