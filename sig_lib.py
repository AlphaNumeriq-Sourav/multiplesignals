import pandas_ta as ta
from numpy import log, polyfit, sqrt, std, subtract
import pandas as pd
import numpy as np
import math
def SMA(data, window, column='close'):
    """Genrate simple moving average of given 'window' on given 'column'.

    Args:
        data (Pandas.DataFrame): Pandas Dataframe of trades
        window (int): window to calculate sma
        column (str, optional): name of the column which has to be calculated for. Defaults to 'close'.

    Returns:
        Pandas.Series : Genrated SMA
    """
    return data[column].rolling(window=window).mean()

def EMA(data, window, column='close'):
    """Genrate exponential moving average of given 'window' on given 'column'.

    Args:
        data (Pandas.DataFrame): Pandas Dataframe of trades
        window (int): window to calculate ema
        column (str, optional): name of the column. Defaults to 'close'.

    Returns:
        Pandas.Series : Genrated EMA
    """
    return data[column].ewm(span=window, adjust=False).mean()
    #return ta.ema(data[column],window)
def rsi(data, window, column='close'):
    """Genrate RSI of given 'window' on given 'column'.

    Args:
        data (Pandas.DataFrame): Pandas Dataframe of trades
        window (int): window to calculate ema
        column (str, optional): name of the column. Defaults to 'close'.

    Returns:
        Pandas.Series : Genrated RSI
    """
    
    return ta.rsi(data[column],window)
def Stochastic(data, window,column1 ='high',column2 ='low', column3 ='close'):
    """Genrate stochastic of given 'window' on given 'column'.

    Args:
        data (Pandas.DataFrame): Pandas Dataframe of trades
        window (int): window to calculate stoch
        column1 (str, optional): name of the column. Defaults to 'high'.
        column2 (str, optional): name of the column. Defaults to 'low'.
        column3 (str, optional): name of the column. Defaults to 'close'.

    Returns:
        Pandas.Series : Genrated stochastic k ,d
    """
    column_index = 0 
    return ta.stoch(data[column1],data[column2],data[column3],window).iloc[:, column_index]
    
def momentum(data,window,column = 'close'):
    """
        momentum = close - close (lookback)  
    """
    return (data[column] - data[column].shift(window))
def Close(data,column = 'close'):
    "  returns close prices"
    return data[column]
import calendar
import numpy as np  
def week_no(date):
    year, month, day = date.year,date.month,date.day
    cal = calendar.monthcalendar(year, month)
    
    # Get the day number (0-6) for the given date
    day_number = calendar.weekday(year, month, day)
    # print(day_number)
    
    # Check if the day is in the which week
    for i in range(len(cal)):

        if np.isin(day,cal[i])   :
            # print('yes') 
            return i
def parbolsar(data, window, window1, column1="high", column2="low", column3="close"):
    PSAR = ta.psar(data[column1], data[column2], data[column3], window, window, window1)
    # PSAR.fillna(0)
    data["psar"] = np.where(
        PSAR.iloc[:, 0] > 0, 1, (np.where(PSAR.iloc[:, 1] > 0, -1, 0))
    )
    return data.psar

def WeekNumber(data ):
    """Genrate weeknumber of given time of the particular no.

    Args:
        data (Pandas.DataFrame): Pandas Dataframe of trades
        
        

    Returns:
        Pandas.Series : Genrated weekno
    """
    return pd.Series(data.time.map(week_no),index = data.index)
def  CCI(data, window,column1 ='high',column2 ='low', column3 ='close'):
    """Genrate commodity chanel index of given 'window' on given 'column'.

    Args:
        data (Pandas.DataFrame): Pandas Dataframe of trades
        window (int): window to calculate stoch
        column1 (str, optional): name of the column. Defaults to 'high'.
        column2 (str, optional): name of the column. Defaults to 'low'.
        column3 (str, optional): name of the column. Defaults to 'close'.

    Returns:
        Pandas.Series : Genrated cci
    """
    return ta.cci(data[column1],data[column2],data[column3],window)
def  AvgTrueRange(data, window,column1 ='high',column2 ='low', column3 ='close'):
    """Genrate oatr f given 'window' on given 'column'.

    Args:
        data (Pandas.DataFrame): Pandas Dataframe of trades
        window (int): window to calculate stoch
        column1 (str, optional): name of the column. Defaults to 'high'.
        column2 (str, optional): name of the column. Defaults to 'low'.
        column3 (str, optional): name of the column. Defaults to 'close'.

    Returns:
        Pandas.Series : Genrated atr
    """
    return ta.atr(data[column1],data[column2],data[column3],window)
def YTD(data,column1 = 'close',column2 = 'open'):
    """  calculating the performance yearly basis for each candle
        cuurent day performance from the beginning of the year
    """
    return ((data[column1] - data[column2].groupby(data.index.year).transform('first')) / data[column2].groupby(data.index.year).transform('first')) * 100
def MTD(data,column1 = 'close',column2 = 'open'):
    """  calculating the performance yearly basis for each candle
        cuurent day performance from the beginning of the year
    """
    return ((data[column1] - data[column2].groupby([data.index.year,data.index.month]).transform('first')) / data[column2].groupby([data.index.year,data.index.month]).transform('first')) * 100
def QTD(data,column1 = 'close',column2 = 'open'):
    """  calculating the performance yearly basis for each candle
        cuurent day performance from the beginning of the year
    """
    return ((data[column1] - data[column2].groupby([data.index.year,data.index.quarter]).transform('first')) / data[column2].groupby([data.index.year,data.index.quarter]).transform('first')) * 100
def KaufmanEfficiencyRatio(data,window,mult,column = 'close'):
    """
    by default calculated over column close
    math:
    
    input: len ( numericSimple );
    var: sum ( 0 );
    sum = 0;
    For value1 = 0 to len - 1 begin
        sum += absValue(close[value1] - close[value1+1]);
    end;
    KaufmanEfficiencyRatio = iff( sum <> 0, absvalue(c-c[len])/sum, 0);
        
    
    """
    data['sum'] = (data[column] - data[column].shift(1)).abs().cumsum()
    data['kauf'] = np.where(data['sum'] != 0, (data[column] - data[column].shift(window)).abs() / data['sum'], 0) * 100

    return data['kauf']*(mult)

def OHLC(data,column1 = 'open',column2 = 'high',column3 = 'low',column4 = 'close'):
    """average price of OHLC
    """
    return (data[column1] + data[column2] + data[column3] + data[column4] )/4
def HLC(data,column2 = 'high',column3 = 'low',column4 = 'close'):
    """average price of OLC
    """
    return ( data[column2] + data[column3] + data[column4] )/3
def BollingerBand(data,window,window1,column = 'close'):
    """
    bollinger band for close price over length = window and window1 = std   
    window1 is positive means upper band 
    window1 is negative means lower band 

    """
    if window1 > 0:
        column_index = 2
        return ta.bbands(data[column],window,abs(window1)).iloc[:, column_index]
    elif window1 < 0:
        column_index = 0
        return ta.bbands(data[column],window,abs(window1)).iloc[:, column_index]
    else:
        return ta.sma(data[column],window)
def KeltnerChannel(data,window,window1,column = 'close',column2 = 'low',column1 = 'high'):
    """
    Keltner channel for close price over length = window and window1 = std   
    window1 is positive means upper band 
    window1 is negative means lower band 

    """
    
    if window1 > 0:
        column_index = 2
        return ta.kc(data[column1],data[column2],data[column],window,abs(window1)).iloc[:, column_index]
    elif window1 < 0:
        column_index = 0
        return ta.kc(data[column1],data[column2],data[column],window,abs(window1)).iloc[:, column_index]
    else:
        return ta.ema(data[column],window)
def ADX(data,window,column = 'close',column2 = 'low',column1 = 'high'):
    """
      directional movement index - returns ADX, +ve, -ve index
      here only adx required
    
    """
    column_index = 0
    return ta.adx(data[column1],data[column2],data[column],window).iloc[:, column_index]
def macdhist(data,window,window1,window2,column = 'close'):

    """
    macd histogram 
    macd indicator return macd line , histogram , signal
    
    """

    column_index = 1
    return ta.macd(data[column],window,window1,window2).iloc[:, column_index]
def macd(data,window,window1,window2,column = 'close'):

    """
    macd histogram 
    macd indicator return macd line , histogram , signal
    
    """

    column_index = 0
    return ta.macd(data[column],window,window1,window2).iloc[:, column_index]

def  SqrtHL(data,column1 = 'high',column2 = 'low'):
    """ 
       returns the series of square root of the product high and low
    """
    return np.sqrt(data[column1] * data[column2])
def  CubeHLC(data,column1 = 'high',column2 = 'low',column3 = 'close'):
    """ 
       returns the series of square root of the product high and low
    """
    return np.cbrt(data[column1] * data[column2]* data[column3])
def rateOfChange(data, window,mult,column = 'close'):
    """
        Rate of Change is calculated as (close – close of lookback)/close of lookback.

    """
    return (data[column] - data[column].shift(window))/data[column].shift(window) *mult
def DayOfWeek(data):

    """
        returns the day of the week as numbers 0 - Mon 
    """
    return pd.Series(data.index.weekday, index=data.index)
def Quarter(data):

    """
        returns the day of the week as numbers 0 - Mon 
    """
    return pd.Series(data.index.quarter, index=data.index)
def Month(data):

    """
        returns the day of the week as numbers 0 - Mon 
    """
    return pd.Series(data.index.month, index=data.index)

def HLMedian(data,column1 = 'high',column2 = 'low'):
    """
      returns high low median
    """

    return (data[column1] + data[column2])/2
def BodyMedian(data,column1 = 'open',column2 = 'close'):
    """
      returns open close median
    """

    return (data[column1] + data[column2])/2

def SuperSmoother(data,column = 'close'):
    closes = data[column]
    if len(closes) > 6:
        value1 = math.exp(-1.414 * 3.14159 / 10)
        value2 = 2 * value1 * math.cos(1.414 * 180 / 10)
        value3 = value2
        value4 = -value1 * value1
        value5 = (1 - value3 - value4)
        value6 = [0] * len(closes)
        
        value6[0] = value5 * (closes[0] + closes[1]) / 2 + value3 * value6[0] + value4 * value6[1] if (2 + value3 * value6[0] + value4 * value6[1]) != 0 else 0
        
        for i in range(1, len(closes)):
            value6[i] = value5 * (closes[i] + closes[i-1]) / 2 + value3 * value6[i-1] + value4 * value6[i-2] if (2 + value3 * value6[i-1] + value4 * value6[i-2]) != 0 else 0
        
        return pd.Series(value6,index= closes.index)
    
    return pd.Series(closes)
def  IBR(data,column1 = 'high',column2 = 'low',column = 'close'):

    """(close – low) / range
        range = high - low
    """
    return (data[column] - data[column2])/(data[column1] - data[column2])*100
def WinsLast(data,window,column = 'close'):
    """
            the number of up closes in the last no of  bars = window 
    """
    return data[column].diff().rolling(window).apply(lambda x: (x > 0).sum())
def  highest(data,window,column = 'high'):
    """
    calculated the highest of high for the lookback = window
    """
    # return data[column].rolling(window).max()
    return data[column].shift(1).rolling(window).max()

def  lowest(data,window,column = 'low'):
    """
    calculated the lowest of low for the lookback = window
    """
    return data[column].rolling(window).min()
    # return data[column].shift(1).rolling(window).min()
    # return data[column].shift(window)
def has_consecutive_lower(rolling_series):
    # if len(rolling_series) < 3:
    #     return False
    

    # Check if the last three elements in the rolling window are in descending order
    return all(rolling_series == sorted(rolling_series, reverse=True))
    
def has_consecutive_higher(rolling_series):
    # if len(rolling_series) < 3:
    #     return False
    

    # Check if the last three elements in the rolling window are in descending order
        
    return all(rolling_series == sorted(rolling_series, reverse=False))


# Apply the rolling function to the 'Low' column with a window size of 3
def consecutive(data,column,window,choice):
    """
    consecutive  choice = 1 implies higher ie column is descending
    consecutive  choice = 0 implies higher ie column is ascending
    
    """
    if choice == 0:

        return data[column].rolling(window).apply(has_consecutive_lower)
    else:
        return data[column].rolling(window).apply(has_consecutive_higher)
        

def pivotpoint(data,column1 = 'high',column2 = 'low',column3 = 'close'):
    """ 
        p = (h + l +c)/3 
        Support 1 (S1) = (P x 2) - High

        Support 2 (S2) = P  -  (High  -  Low)

        Resistance 1 (R1) = (P x 2) - Low

        Resistance 2 (R2) = P + (High  -  Low)
    """

    return (data[column1] + data[column2] + data[column3])/3
def s2(data,column1 = 'high',column2 = 'low',column3 = 'close'):
        Pivotpoint = (data[column1] + data[column2] + data[column3])/3
        """ 
        p = (h + l +c)/3 
        Support 1 (S1) = (P x 2) - High

        Support 2 (S2) = P  -  (High  -  Low)

        Resistance 1 (R1) = (P x 2) - Low

        Resistance 2 (R2) = P + (High  -  Low)
        """
        return Pivotpoint - (data[column1] - data[column2])
def s1(data,column1 = 'high',column2 = 'low',column3 = 'close'):
    Pivotpoint = (data[column1] + data[column2] + data[column3])/3
    """ 
        p = (h + l +c)/3 
        Support 1 (S1) = (P x 2) - High

        Support 2 (S2) = P  -  (High  -  Low)

        Resistance 1 (R1) = (P x 2) - Low

        Resistance 2 (R2) = P + (High  -  Low)
    """
    return Pivotpoint * 2 - (data[column1] )
def r2(data,column1 = 'high',column2 = 'low',column3 = 'close'):
        Pivotpoint = (data[column1] + data[column2] + data[column3])/3
        """ 
        p = (h + l +c)/3 
        Support 1 (S1) = (P x 2) - High

        Support 2 (S2) = P  -  (High  -  Low)

        Resistance 1 (R1) = (P x 2) - Low

        Resistance 2 (R2) = P + (High  -  Low)
        """
        return Pivotpoint + (data[column1] - data[column2])
def r1(data,column1 = 'high',column2 = 'low',column3 = 'close'):
    Pivotpoint = (data[column1] + data[column2] + data[column3])/3
    """ 
        p = (h + l +c)/3 
        Support 1 (S1) = (P x 2) - High

        Support 2 (S2) = P  -  (High  -  Low)

        Resistance 1 (R1) = (P x 2) - Low

        Resistance 2 (R2) = P + (High  -  Low)
    """
    return Pivotpoint * 2 - (data[column2] )
def ValueCharts(data,window,mult,columm = 'open',column1 = 'high',column2 = 'low'):

    """
        Open – average((h+l)/2,length) / (1/length * average(range,length)) 
    """
    average1 = ((data[column1] + data[column2])/2).rolling(window).mean()
    # average2 = ((data[column1] - data[column2])*mult).rolling(window).mean()
    average2 = ((data[column1] - data[column2])).rolling(window).mean()
    return (data[columm] - (average1))/(1/(window)*average2)



def Hurst(data, window, column1 ='high', column2 = 'low'):

    """
    column1 high used to calculate the highest vaue over the period window
    column2 low used to calculate the lowest value over the period window
    Functions highest, lowest, AvgTrueRange are used

    math :

    input: len (numericsimple);

    //Hurst = 2 - fractalDim(c,len);
    Hurst = .5;
    If (highest(h,len) - lowest(l,len) > 0 and avgTrueRange(len) > 0 ) then begin
    Hurst = iff(log(len) <> 0,(log(highest(h,len) - lowest(l,len)) - log(avgTrueRange(len)))/log(len), 0);
    end;

    """

    data['hurst'] = 0.5
    condition = (((highest(data,window,column1) - lowest(data,window,column2) ) > 0 ) & ((AvgTrueRange(data,window)) > 0))
    hurst = np.where(condition,
        np.where(np.log(window) != 0 ,
            (np.log(highest(data,window,column1) - lowest(data,window,column2) ) - np.log(AvgTrueRange(data,window)))/np.log(window),
            0 ),0.5)
    data['hurst'] = hurst
     
    return data.hurst*100

def compositeHurst(data,window,window1):
    composite_hurst = pd.DataFrame()
    for lookback in range(window, window1+1):
        composite_hurst[f'hurst_{lookback}'] = Hurst(data,lookback)
    return composite_hurst.mean(axis=1)

def CompositeRSI(data,window,window1):
    """
      mean of rsi from window to window1
    """
    composite_rsi = pd.DataFrame()
    for lookback in range(window, window1+1):
        composite_rsi[f'rsi_{lookback}'] = rsi(data,lookback)
    return composite_rsi.mean(axis=1)
def CompositeSMA(data,window,window1,window2,window3):
    """
      mean of sma for all window,window1,window2,window3
    """
    composite_sma = pd.DataFrame()
    
    composite_sma[f'sma_{window}'] = SMA(data,window)
    composite_sma[f'sma_{window1}'] = SMA(data,window1)
    composite_sma[f'sma_{window2}'] = SMA(data,window2)
    composite_sma[f'sma_{window3}'] = SMA(data,window3)
    return composite_sma.mean(axis=1)

def CompositeEMA(data,window,window1,window2,window3):
    """
      mean of ema for all window,window1,window2,window3
    """
    composite_ema = pd.DataFrame()
    
    composite_ema[f'sma_{window}'] = EMA(data,window)
    composite_ema[f'sma_{window1}'] = EMA(data,window1)
    composite_ema[f'sma_{window2}'] = EMA(data,window2)
    composite_ema[f'sma_{window3}'] = EMA(data,window3)
    return composite_ema.mean(axis=1)

def CompositeATR(data, window, window1):
    """
    mean of atr from window to window1
    """
    composite_atr = pd.DataFrame()
    for lookback in range(window, window1 + 1):
        composite_atr[f"atr_{lookback}"] = AvgTrueRange(data, lookback)
    return composite_atr.mean(axis=1)



def barPath(data , column = 'close'):
    # data['val'] = np.where(
    # (data[column] < data[column].shift(1)) & (data[column].shift(1) < data[column].shift(2)) & (data[column].shift(2) < data[column].shift(3)), 1,np.where(
    # (data[column] < data[column].shift(1)) & (data[column].shift(1) < data[column].shift(2)) & (data[column].shift(2) > data[column].shift(3))),2,np.where(
    # (data[column] < data[column].shift(1)) & (data[column].shift(1) > data[column].shift(2)) & (data[column].shift(2) < data[column].shift(3))),3,np.where(
    # (data[column] < data[column].shift(1)) & (data[column].shift(1) > data[column].shift(2)) & (data[column].shift(2) > data[column].shift(3))),4,np.where(
    # (data[column] > data[column].shift(1)) & (data[column].shift(1) < data[column].shift(2)) & (data[column].shift(2) < data[column].shift(3))),5,np.where(
    # (data[column] > data[column].shift(1)) & (data[column].shift(1) < data[column].shift(2)) & (data[column].shift(2) > data[column].shift(3))),6,np.where(
    # (data[column] > data[column].shift(1)) & (data[column].shift(1) > data[column].shift(2)) & (data[column].shift(2) < data[column].shift(3))),7,np.where(
    # (data[column] > data[column].shift(1)) & (data[column].shift(1) > data[column].shift(2)) & (data[column].shift(2) > data[column].shift(3))),8,np.nan)
    data['val'] = np.where(
    (data[column] < data[column].shift(1)) & (data[column].shift(1) < data[column].shift(2)) & (data[column].shift(2) < data[column].shift(3)), 1,
    np.where(
        (data[column] < data[column].shift(1)) & (data[column].shift(1) < data[column].shift(2)) & (data[column].shift(2) > data[column].shift(3)), 2,
        np.where(
            (data[column] < data[column].shift(1)) & (data[column].shift(1) > data[column].shift(2)) & (data[column].shift(2) < data[column].shift(3)), 3,
            np.where(
                (data[column] < data[column].shift(1)) & (data[column].shift(1) > data[column].shift(2)) & (data[column].shift(2) > data[column].shift(3)), 4,
                np.where(
                    (data[column] > data[column].shift(1)) & (data[column].shift(1) < data[column].shift(2)) & (data[column].shift(2) < data[column].shift(3)), 5,
                    np.where(
                        (data[column] > data[column].shift(1)) & (data[column].shift(1) < data[column].shift(2)) & (data[column].shift(2) > data[column].shift(3)), 6,
                        np.where(
                            (data[column] > data[column].shift(1)) & (data[column].shift(1) > data[column].shift(2)) & (data[column].shift(2) < data[column].shift(3)), 7,
                            np.where(
                                (data[column] > data[column].shift(1)) & (data[column].shift(1) > data[column].shift(2)) & (data[column].shift(2) > data[column].shift(3)), 8,
                                np.nan
                            ))
                    )
                )
            )
        )
    ))
    
    return data['val']

def InsideRange(data,window,window1):
    """
       window is for lookback
       window1 = 1 means close above mandatory
       window1 = 1 means close below mandatory

       fn checks for the range < the previous lookbacks range
    
    """
    data['range'] = data['high'] - data['low']
    if window1 == 1:

        data['val'] =    np.where((data.range < data.range.shift(window)) & (data.close > data.close.shift(4)),1,0)
    else:
       data['val'] = np.where((data.range < data.range.shift(window)) & (data.close < data.close.shift(4)),1,0)
    return data['val']
def OutsideRange(data,window,window1):
    """
       window is for lookback
       window1 = 1 means close above mandatory
       window1 = 1 means close below mandatory

       fn checks for the range > the previous lookbacks range

    
    """
    data['range'] = data['high'] - data['low']
    if window1 == 1:

        data['val'] = np.where((data.range > data.range.shift(window)) & (data.close >= data.close.shift(4)),1,0)
    else:
        data['val'] = np.where((data.range > data.range.shift(window)) & (data.close <= data.close.shift(4)),1,0)
    return data['val']
    
    
def DownRange(data,window,window1):
    """
       window is for lookback
       window1 = 1 means close above mandatory
       window1 = 1 means close below mandatory

        fn checks for the high and low < the previous lookbacks high, low

    
    """
    
    if window1 == 1:

        data['val'] = np.where((data.high < data.high.shift(window)) & (data.low < data.low.shift(window)) & (data.close > data.close.shift(4)),1,0)
    else:
        data['val'] = np.where((data.high < data.high.shift(window)) & (data.low < data.low.shift(window)) & (data.close < data.close.shift(4)),1,0)
    return data['val']
    
    
def UpRange(data,window,window1):
    """
       window is for lookback
       window1 = 1 means close above mandatory
       window1 = 1 means close below mandatory

       fn checks for the high and low < the previous lookbacks high, low

    
    """
    if window1 == 1:

        data['val'] = np.where((data.high > data.high.shift(window)) & (data.low > data.low.shift(window)) & (data.close > data.close.shift(4)),1,0)
    else:
        data['val'] = np.where((data.high > data.high.shift(window)) & (data.low > data.low.shift(window)) & (data.close < data.close.shift(4)),1,0)
    
    return data['val']
def SuperSmoother(data,column = 'close'):
    closes = data[column]
    if len(closes) > 6:
        value1 = math.exp(-1.414 * 3.14159 / 10)
        value2 = 2 * value1 * math.cos(1.414 * 180 / 10)
        value3 = value2
        value4 = -value1 * value1
        value5 = (1 - value3 - value4)
        value6 = [0] * len(closes)
        
        value6[0] = value5 * (closes[0] + closes[1]) / 2 + value3 * value6[0] + value4 * value6[1] if (2 + value3 * value6[0] + value4 * value6[1]) != 0 else 0
        
        for i in range(1, len(closes)):
            value6[i] = value5 * (closes[i] + closes[i-1]) / 2 + value3 * value6[i-1] + value4 * value6[i-2] if (2 + value3 * value6[i-1] + value4 * value6[i-2]) != 0 else 0
        
        return pd.Series(value6,index= closes.index)
    
    return pd.Series(closes)

def hammer(data,column = 'open' ,column1 = 'high', column2 = 'low', column3 = 'close'):

    """
     retuns true for open and close > midpoint of the candle
    """

    data['val'] = np.where(((data[column] > ((data[column1] + data[column2])/2)) & (data[column3] > ((data[column1] + data[column2])/2))),1,0)
    return data['val']

def invertedhammer(data,column = 'open' ,column1 = 'high', column2 = 'low', column3 = 'close'):
    """
     retuns true for open and close > midpoint of the candle
    """

    data['val'] = np.where(((data[column] < ((data[column1] + data[column2])/2)) & (data[column3] < ((data[column1] + data[column2])/2))),1,0)



def entry_signal_1(data, current_index, close_column='close', low_column='low', high_column='high', sma_20_column = 'sma_20', ema_9_column = 'ema_9', ema_18_column = 'ema_18'):
    """Genrate entry signal based on following coditions
        1. high[0]>low[-2]
        2. high[-2]>close[-7]
        3. sma(20, close)[0] < sma(20, close)[-3]
        4. ema(9, close)[0] crosses above ema(18, close)[0]

    Args:
        data (Pandas.DataFrame): Pandas Dataframe of trades
        current_index (int): Current trade info in trade dataframe.
        close_column (str, optional): Name of close column. Defaults to 'close'.
        low_column (str, optional): Name of low column. Defaults to 'low'.
        high_column (str, optional): Name of high column. Defaults to 'high'.
        sma_20_column (str, optional): Name of SMA 20 column, Needs to be genrated and joined to DataFrame. Defaults to 'sma_20'.
        ema_9_column (str, optional): Name of EMA 9 column, Needs to be genrated and joined to DataFrame. Defaults to 'ema_9'.
        ema_18_column (str, optional): Name of EMA 18 column, Needs to be genrated and joined to DataFrame. Defaults to 'ema_18'.

    Returns:
        bool: Signal True(Entry)/False(No Entry)
    """
    if current_index < 20:
        return 0
       
    condition_1 = data[high_column][current_index] > data[low_column][current_index-2]
    condition_2 = data[high_column][current_index-2] > data[close_column][current_index-7]
    condition_3 = data[sma_20_column][current_index] < data[sma_20_column][current_index-3]
    condition_4 = data[ema_9_column][current_index] > data[ema_18_column][current_index] and data[ema_9_column][current_index-1] < data[ema_18_column][current_index-1]
    
    if condition_1 and condition_2 and condition_3 and condition_4:
        return -1
    else:
        return 0
    
def entry_signal_2(data, current_index, close_column='close', low_column='low', high_column='high', ema_9_column = 'ema_9', ema_18_column = 'ema_18'):
    """Genrate entry signal based on following coditions
        1. high[-2]>close[-6]
        2. high[-6]>close[-7]
        3. low[-6]<=low[-7]
        4. ema(9, close)[0] crosses above ema(18, close)[0]
        
    Args:
        data (Pandas.DataFrame): Pandas Dataframe of trades
        current_index (int): Current trade info in trade dataframe.
        close_column (str, optional): Name of close column. Defaults to 'close'.
        low_column (str, optional): Name of low column. Defaults to 'low'.
        high_column (str, optional): Name of high column. Defaults to 'high'.
        ema_9_column (str, optional): Name of EMA 9 column, Needs to be genrated and joined to DataFrame. Defaults to 'ema_9'.
        ema_18_column (str, optional): Name of EMA 18 column, Needs to be genrated and joined to DataFrame. Defaults to 'ema_18'.
        
    Returns:
        bool: Signal True(Entry)/False(No Entry)"""
        
    # if current_index < 20:
    #     return 0
    
    condition_1 = data[high_column][current_index-2] > data[close_column][current_index-6]
    condition_2 = data[high_column][current_index-6] > data[close_column][current_index-7]
    condition_3 = data[low_column][current_index-6] <= data[low_column][current_index-7]
    condition_4 = data[ema_9_column][current_index] > data[ema_18_column][current_index] and data[ema_9_column][current_index-1] < data[ema_18_column][current_index-1]
    
    if condition_1 and condition_2 and condition_3 and condition_4:
        
        return -1
    else:
        return 0

def entry_signal_3(data, current_index, close_column='close', low_column='low', high_column='high', ema_9_column = 'ema_9', ema_18_column = 'ema_18',super_smoother_col = 'CCI'):
    """_summary_
    """
    # condition_1 = data[high_column][current_index-1] > data[high_column][current_index-4]
    # condition_2 = data[low_column][current_index-4] <= data[high_column][current_index-6]
    # condition_3 = data[high_column][current_index] >= data[super_smoother_col][current_index]
    # condition_4 = data[ema_9_column][current_index] > data[ema_18_column][current_index] and data[ema_9_column][current_index-1] < data[ema_18_column][current_index-1]
    condition_1 = data[high_column][current_index-3] > data[high_column][current_index-6]
    condition_2 = data[low_column][current_index-4] <= data[high_column][current_index-6]
    condition_3 = data[super_smoother_col][current_index] > data[super_smoother_col][current_index-4]
    condition_4 = data[ema_9_column][current_index] > data[ema_18_column][current_index] and data[ema_9_column][current_index-1] < data[ema_18_column][current_index-1]
    
    if condition_1 and condition_2 and condition_3 and condition_4:
        
        return -1
    else:
        return 0

    return False