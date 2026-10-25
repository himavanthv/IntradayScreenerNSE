import nse_data_fetcher as nse
import numpy as np
import pandas as pd
import time
import pytz
from datetime import datetime, date, timedelta



def calculate_vwap(df):
    df.index = pd.to_datetime(df.index)
    df['Typical_Price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['Price_Vol'] = df['Typical_Price'] * df['Volume']
    df['Cum_Price_Vol'] = df.groupby(df.index.date)['Price_Vol'].cumsum()
    df['Cum_Volume'] = df.groupby(df.index.date)['Volume'].cumsum()
    df['VWAP'] = df['Cum_Price_Vol'] / df['Cum_Volume']    
    return df['VWAP']

def calculate_rsi(data, window):
    # Get the price differences
    delta = data.diff()
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    # Calculate Wilder's Exponential Moving Average (EMA)
    avg_gain = gain.ewm(alpha=1 / window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False).mean()
    # Calculate Relative Strength (RS)
    rs = avg_gain / avg_loss
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    return rsi


def live_filter(data, interval):
    print('TBD')




def volume_indication(data,candleInterval,backtesting_flag,tradeType):
    data['Candle_Interval']=candleInterval
    data['Model']='VolumeBased'
## ------------------ Configuration Based on Different Candle Intervals -----------------##
    if candleInterval =='15m':
        exit_after_candles = 18
        value_of_candle = 50000000
        enter_after_candles = 1
    capital = 10000
    gap_today = 1
    intraday_capital = capital*5


    if tradeType =='intraday':
        total_taxes = (intraday_capital*2)*0.00032
        total_brokerage = 20 # Algo flat charges # manual 40 Rs
        square_off_charges = 0
    trade_rows = pd.DataFrame()
    trading_rows = pd.DataFrame()
    ticker_trade_rows = pd.DataFrame()
    
    ## Buy and Sell with out S_L
    #bullish_indices = np.where((data['Volume'].shift(-2)>2*data['AverageVolume'].shift(-2)) & (data['CandleChange'].shift(-2)>0) & (data['CandleChange'].shift(-4)<=1) & (data['Volume'].shift(-1)>data['Volume'].shift(-2)) & (data['CandleChange'].shift(-1)>0.25) & (data['CandleChange']>0) & (data['SMA_9'].shift(-1)>data['SMA_9'].shift(-2)) & (data['SMA_9']>data['SMA_9'].shift(-1)) & (data['High'].shift(-1)>data['High'].shift(-2)) & (data['High']>data['High'].shift(-1)) & (data['ChangeSinceYesterday'].shift(-2)>0) & (data['ChangeSinceYesterday'].shift(-1)>0) & (data['ChangeSinceYesterday']>0) & (data['RSI']<70) & (data['RSI'].shift(-2)<70) & (data['RSI'].shift(-1)<70))[0].tolist()
    #bearish_indices = np.where((data['Volume'].shift(-2)>2*data['AverageVolume'].shift(-2)) & (data['CandleChange'].shift(-2)<0) & (data['CandleChange'].shift(-4)>=-1) & (data['Volume'].shift(-1)>data['Volume'].shift(-2)) & (data['CandleChange'].shift(-1)<-0.25) & (data['CandleChange']<0) & (data['SMA_9'].shift(-1)<data['SMA_9'].shift(-2)) & (data['SMA_9']<data['SMA_9'].shift(-1)) & (data['Low'].shift(-1)<data['Low'].shift(-2)) & (data['Low']<data['Low'].shift(-1)) & (data['ChangeSinceYesterday'].shift(-2)<0) & (data['ChangeSinceYesterday'].shift(-1)<0) & (data['ChangeSinceYesterday']<0) & (data['RSI']>30) & (data['RSI'].shift(-1)>30)  & (data['RSI'].shift(-2)>30))[0].tolist()
    #bullish_indices = np.where((data['Volume']>2*data['AverageVolume']) & (data['CandleChange']>0))[0].tolist()
    #bearish_indices = np.where((data['Volume']>2*data['AverageVolume']) & (data['CandleChange']<0))[0].tolist()
    #bullish_indices = np.where((data['CandleChange'].shift(-5)<0) & (data['CandleChange'].shift(-4)<0) & (data['CandleChange'].shift(-3)<0) & (data['CandleChange'].shift(-2)<0) & (data['CandleChange'].shift(-1)<0) & (data['RSI']<30) & (data['DistanceBetweenPrevClose_650']<=-5) & (data['CrossOver']==1) & (data['DistanceFromMA9_Close']>0))[0].tolist()
    #bearish_indices = np.where((data['CandleChange'].shift(-5)>0) & (data['CandleChange'].shift(-4)>0) & (data['CandleChange'].shift(-3)>0) & (data['CandleChange'].shift(-2)>0) & (data['CandleChange'].shift(-1)>0) & (data['RSI']>70) & (data['DistanceBetweenPrevClose_650']>=5) & (data['CrossOver']==-1) & (data['DistanceFromMA9_Close']<0))[0].tolist()
    
    bullish_indices = np.where((data['ChangeSinceYesterday']>1) & (data['MaVariance_Month15']<0) & (data['SMA_650'].shift(-1)>data['SMA_650'].shift(-2)) & (data['SMA_650'].shift(-2)>data['SMA_650'].shift(-3)) & (data['SMA_650'].shift(-3)>data['SMA_650'].shift(-4)) & (data['SMA_650'].shift(-4)>data['SMA_650'].shift(-5)) & (data['SMA_650'].shift(-5)>data['SMA_650'].shift(-6)) & (data['SMA_650'].shift(-6)>data['SMA_650'].shift(-7)) & (data['SMA_650'].shift(-7)>data['SMA_650'].shift(-8)) & (data['SMA_225'].shift(-1)>data['SMA_225'].shift(-2)) & (data['SMA_225'].shift(-2)>data['SMA_225'].shift(-3)) & (data['SMA_225'].shift(-3)>data['SMA_225'].shift(-4)) & (data['SMA_225'].shift(-4)>data['SMA_225'].shift(-5)) & (data['SMA_225'].shift(-5)>data['SMA_225'].shift(-6)) & (data['SMA_225'].shift(-6)>data['SMA_225'].shift(-7)) & (data['SMA_225'].shift(-7)>data['SMA_225'].shift(-8)) & (data['CrossOver9_650']==1))[0].tolist()
    bearish_indices = np.where((data['ChangeSinceYesterday']<1) & (data['MaVariance_Month15']>0) & (data['SMA_650'].shift(-1)<data['SMA_650'].shift(-2)) & (data['SMA_650'].shift(-2)<data['SMA_650'].shift(-3)) & (data['SMA_650'].shift(-3)<data['SMA_650'].shift(-4)) & (data['SMA_650'].shift(-4)<data['SMA_650'].shift(-5)) & (data['SMA_650'].shift(-5)<data['SMA_650'].shift(-6)) & (data['SMA_650'].shift(-6)<data['SMA_650'].shift(-7)) & (data['SMA_650'].shift(-7)<data['SMA_650'].shift(-8)) & (data['SMA_225'].shift(-1)<data['SMA_225'].shift(-2)) & (data['SMA_225'].shift(-2)<data['SMA_225'].shift(-3)) & (data['SMA_225'].shift(-3)<data['SMA_225'].shift(-4)) & (data['SMA_225'].shift(-4)<data['SMA_225'].shift(-5)) & (data['SMA_225'].shift(-5)<data['SMA_225'].shift(-6)) & (data['SMA_225'].shift(-6)<data['SMA_225'].shift(-7)) & (data['SMA_225'].shift(-7)<data['SMA_225'].shift(-8)) & (data['CrossOver9_650']==-1))[0].tolist()


    #CrossOver9_650



    bullish_entry_indices = [index-enter_after_candles for index in bullish_indices]
    bearish_entry_indices = [index-enter_after_candles for index in bearish_indices]   
    bullish_found_rows = data.iloc[bullish_entry_indices]
    bearish_found_rows = data.iloc[bearish_entry_indices]
    bullish_found_rows['Type'] = 'Buy'
    bearish_found_rows['Type'] = 'Sell'
    trading_rows = pd.concat([bullish_found_rows,bearish_found_rows], ignore_index=True)
    if backtesting_flag == True:
        for row in trading_rows.itertuples():
            od_data = data[(data['DateStr'] == row.DateStr)]
            od_data = od_data.reset_index()
            #print(type(row.Gap_Open))
            if (row.Type == 'Buy'):
                bullish_entry_index = np.where((od_data['Time']==row.Time))[0].tolist()[0]
                bullish_exit_index = bullish_entry_index - exit_after_candles
                if bullish_exit_index<0:
                    bullish_exit_index=0
                bullish_rows = od_data.iloc[[bullish_entry_index]]
                bull_exit = od_data.iloc[[bullish_exit_index]]
                bull_exit2 = bull_exit.rename(columns={'Time': 'ExitTime', 'Close': 'Exit_Price'})
                bullish_rows = pd.concat([bullish_rows.reset_index(drop=True), bull_exit2[['ExitTime', 'Exit_Price']].reset_index(drop=True)], axis=1)
                bullish_rows['EntryPrice'] = bullish_rows['Close']          
                bullish_rows['Quantity'] = intraday_capital/bullish_rows['EntryPrice']
                bullish_rows['Change'] = bullish_rows['Exit_Price']-bullish_rows['EntryPrice']
                bullish_rows['Profit'] = bullish_rows['Change']*bullish_rows['Quantity']-40-square_off_charges
                bullish_rows['Type'] ='Buy'
                one_day_rows = bullish_rows
                ticker_trade_rows=pd.concat([one_day_rows,ticker_trade_rows], ignore_index=True)
            elif (row.Type =='Sell'):
                bearish_entry_index = np.where((od_data['Time']==row.Time))[0].tolist()[0]
                bearish_exit_index = bearish_entry_index - exit_after_candles
                if bearish_exit_index < 0:
                    bearish_exit_index = 0
                bearish_rows = od_data.iloc[[bearish_entry_index]]
                bear_exit = od_data.iloc[[bearish_exit_index]]
                bear_exit2 = bear_exit.rename(columns={'Time': 'ExitTime', 'Close': 'Exit_Price'})
                bearish_rows = pd.concat([bearish_rows.reset_index(drop=True), bear_exit2[['ExitTime', 'Exit_Price']].reset_index(drop=True)], axis=1)
                bearish_rows['EntryPrice']=bearish_rows['Close']
                bearish_rows['Quantity'] = intraday_capital/bearish_rows['EntryPrice']
                bearish_rows['Change'] = bearish_rows['EntryPrice']-bearish_rows['Exit_Price']
                bearish_rows['Profit'] = bearish_rows['Change']*bearish_rows['Quantity']-40-square_off_charges
                bearish_rows['Type'] ='Sell'
                one_day_rows = bearish_rows
                ticker_trade_rows=pd.concat([one_day_rows,ticker_trade_rows], ignore_index=True)
        return ticker_trade_rows
    else:
        return trading_rows