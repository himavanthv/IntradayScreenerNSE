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

def volume_indication(data,candleInterval,backtesting_flag,tradeType):
    data['Candle_Interval']=candleInterval
    data['Model']='VolumeBased'
## ------------------ Configuration Based on Different Candle Intervals -----------------##
    if candleInterval =='15m':
        exit_after_candles = 125
        value_of_candle = 50000000
        enter_after_candles = 1
        candle_change=1.5
        rsi_high=80
        rsi_low=20

    capital = 10000
    gap_today = 1
    intraday_capital = capital*5
    if tradeType =='intraday':
        total_taxes = (intraday_capital*2)*0.00032
        total_brokerage = 20 # Algo flat charges # manual 40 Rs
    else:
        # Swing Trade 0
        total_taxes = 0
        total_brokerage = 0 # Algo flat charges # manual 40 Rs
    ticker_trade_rows = pd.DataFrame()
    bullish_indices = np.where((data['Volume']>data['AverageVolume']) & (data['CandleChange']>=1) & (data['Low_Wick'].abs()<=0.05) & (data['High_Wick'].abs()<=0.05) & (data['Gap_Open']>0) & (data['Gap_Open']<1))[0].tolist() 
    bearish_indices = np.where((data['Volume']>data['AverageVolume']) & (data['CandleChange']<=-1) & (data['Low_Wick'].abs()<=0.05) & (data['High_Wick'].abs()<=0.05) & (data['Gap_Open']<0) & (data['Gap_Open']>-1))[0].tolist()
    bullish_found_rows = data.iloc[bullish_indices]
    bearish_found_rows = data.iloc[bearish_indices]    
    bullish_found_rows['Type'] = 'Buy'
    bearish_found_rows['Type'] = 'Sell'
    trading_rows = pd.concat([bullish_found_rows,bearish_found_rows], ignore_index=True)
    if backtesting_flag and tradeType=='swing':
        for item in bullish_indices:
            bullish_entry_index = item - enter_after_candles
            bullish_rows = data.iloc[[bullish_entry_index]]
            bullish_exit_index = bullish_entry_index - exit_after_candles
            if bullish_exit_index<0:
                bullish_exit_index=0
            bull_exit_rows = data.iloc[[bullish_exit_index]]
            bull_exit2 = bull_exit_rows.rename(columns={'Time': 'ExitTime', 'Close': 'Exit_Price','DateStr': 'Exit_Date'})
            bullish_rows = pd.concat([bullish_rows.reset_index(drop=True), bull_exit2[['ExitTime', 'Exit_Price', 'Exit_Date']].reset_index(drop=True)], axis=1)
            bullish_rows['EntryPrice'] = (bullish_rows['Open']+bullish_rows['High']+bullish_rows['Low']+bullish_rows['Close'])/4          
            bullish_rows['Quantity'] = capital/bullish_rows['EntryPrice']
            bullish_rows['Change'] = bullish_rows['Exit_Price']-bullish_rows['EntryPrice']
            bullish_rows['Profit'] = bullish_rows['Change']*bullish_rows['Quantity']
            bullish_rows['Type'] ='Buy'
            swing_trade_rows = bullish_rows
            ticker_trade_rows=pd.concat([swing_trade_rows,ticker_trade_rows], ignore_index=True)
        for item in bearish_indices:
            bearish_entry_index = item - enter_after_candles
            bearish_rows = data.iloc[[bearish_entry_index]]
            bearish_exit_index = bearish_entry_index - exit_after_candles
            if bearish_exit_index<0:
                bearish_exit_index=0
            bear_exit_rows = data.iloc[[bearish_exit_index]]
            bear_exit2 = bear_exit_rows.rename(columns={'Time': 'ExitTime', 'Close': 'Exit_Price','DateStr': 'Exit_Date'})
            bearish_rows = pd.concat([bearish_rows.reset_index(drop=True), bear_exit2[['ExitTime', 'Exit_Price', 'Exit_Date']].reset_index(drop=True)], axis=1)
            bearish_rows['EntryPrice'] = (bearish_rows['Open']+bearish_rows['High']+bearish_rows['Low']+bearish_rows['Close'])/4          
            bearish_rows['Quantity'] = capital/bearish_rows['EntryPrice']
            bearish_rows['Change'] = bearish_rows['EntryPrice']-bearish_rows['Exit_Price']
            bearish_rows['Profit'] = bearish_rows['Change']*bearish_rows['Quantity']
            bearish_rows['Type'] ='Sell'
            swing_trade_rows = bearish_rows
            ticker_trade_rows=pd.concat([swing_trade_rows,ticker_trade_rows], ignore_index=True)
        return ticker_trade_rows                
    elif backtesting_flag and tradeType=='intraday':
        for row in trading_rows.itertuples():
            od_data = data[(data['DateStr'] == row.DateStr)]
            if row.Type == 'Buy':
                bullish_entry_index = np.where((od_data['Time']==row.Time))[0].tolist()[0]
                bullish_entry_index = bullish_entry_index - enter_after_candles
                bullish_exit_index = bullish_entry_index - exit_after_candles
                if bullish_exit_index<0:
                    bullish_exit_index=0
                bullish_rows = od_data.iloc[[bullish_entry_index]]
                bull_exit = od_data.iloc[[bullish_exit_index]]
                bull_exit2 = bull_exit.rename(columns={'Time': 'ExitTime', 'Close': 'Exit_Price'})
                bullish_rows = pd.concat([bullish_rows.reset_index(drop=True), bull_exit2[['ExitTime', 'Exit_Price']].reset_index(drop=True)], axis=1)
                bullish_rows['EntryPrice'] = bullish_rows['Open']          
                bullish_rows['Quantity'] = intraday_capital/bullish_rows['EntryPrice']
                bullish_rows['Change'] = bullish_rows['Exit_Price']-bullish_rows['EntryPrice']
                bullish_rows['Profit'] = bullish_rows['Change']*bullish_rows['Quantity']-40
                bullish_rows['Type'] ='Buy'
                one_day_rows = bullish_rows
                ticker_trade_rows=pd.concat([one_day_rows,ticker_trade_rows], ignore_index=True)
            elif row.Type =='Sell':
                bearish_entry_index = np.where((od_data['Time']==row.Time))[0].tolist()[0]
                bearish_entry_index = bearish_entry_index - enter_after_candles
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
                bearish_rows['Profit'] = bearish_rows['Change']*bearish_rows['Quantity']-40
                bearish_rows['Type'] ='Sell'
                one_day_rows = bearish_rows
                ticker_trade_rows=pd.concat([one_day_rows,ticker_trade_rows], ignore_index=True)
        return ticker_trade_rows
    else:
        return trading_rows
def crossover(data,candleInterval,backtesting_flag):
    ticker_trade_rows = pd.DataFrame()
    capital = 10000
    total_taxes = (capital*2)*0.00032
    total_brokerage = 40 # Algo flat charges # manual 40 Rs
    data['Model']='CrossOver'
    data['Candle_Interval']=candleInterval
    if candleInterval=='1d':
        exit_after_candles = 5
        enter_after_candles = 0
        value_of_candle = 300000000
    if candleInterval=='60m':
        exit_after_candles = 30
        enter_after_candles = 0
        value_of_candle = 500000000
    bullish_indices = np.where((data['CrossOver'] == 1) & (data['RSI'] >= data['RSI_Change']) & (data['Volume']*data['Open'] > value_of_candle))[0].tolist()
    bearish_indices = np.where((data['CrossOver'] == -1) & (data['RSI'] <= data['RSI_Change']) & (data['Volume']*data['Open'] > value_of_candle))[0].tolist()
    bullish_found_rows = data.iloc[bullish_indices]
    bearish_found_rows = data.iloc[bearish_indices]
    bullish_found_rows['Type'] = 'Buy'
    bearish_found_rows['Type'] = 'Sell'
    trading_rows = pd.concat([bullish_found_rows,bearish_found_rows], ignore_index=True)
    if backtesting_flag:
        for row in trading_rows.itertuples():
            if row.Type == 'Buy':
                bullish_entry_index = np.where((data['DateStr']==row.DateStr) & (data['Time']==row.Time))[0].tolist()[0]
                bullish_entry_index = bullish_entry_index - enter_after_candles
                bullish_exit_index = bullish_entry_index - exit_after_candles
                if bullish_exit_index < 0:
                    bullish_exit_index = 0
                bullish_rows = data.iloc[[bullish_entry_index]]
                bull_exit = data.iloc[[bullish_exit_index]]
                bull_exit2 = bull_exit.rename(columns={'Time': 'ExitTime', 'Close': 'Exit_Price'})
                bullish_rows = pd.concat([bullish_rows.reset_index(drop=True), bull_exit2[['ExitTime', 'Exit_Price']].reset_index(drop=True)], axis=1)
                bullish_rows['EntryPrice']=(bullish_rows['Open']+bullish_rows['Close'])/2          
                bullish_rows['Quantity'] = capital/bullish_rows['EntryPrice']
                bullish_rows['Change'] = bullish_rows['Exit_Price']-bullish_rows['EntryPrice']
                bullish_rows['Profit'] = bullish_rows['Change']*bullish_rows['Quantity']
                bullish_rows['Type'] ='Buy'
                ticker_trade_rows=pd.concat([bullish_rows,ticker_trade_rows], ignore_index=True)
            elif row.Type =='Sell':
                bearish_entry_index = np.where((data['DateStr']==row.DateStr) & (data['Time']==row.Time))[0].tolist()[0]
                bearish_entry_index = bearish_entry_index - enter_after_candles
                bearish_exit_index = bearish_entry_index - exit_after_candles
                if bearish_exit_index<0:
                    bearish_exit_index=0
                bearish_rows = data.iloc[[bearish_entry_index]]
                bear_exit = data.iloc[[bearish_exit_index]]
                bear_exit2 = bear_exit.rename(columns={'Time': 'ExitTime', 'Close': 'Exit_Price'})
                bearish_rows = pd.concat([bearish_rows.reset_index(drop=True), bear_exit2[['ExitTime', 'Exit_Price']].reset_index(drop=True)], axis=1)
                bearish_rows['EntryPrice']=(bearish_rows['Open']+bearish_rows['Close'])/2
                bearish_rows['Quantity'] = capital/bearish_rows['EntryPrice']
                bearish_rows['Change'] = bearish_rows['EntryPrice']-bearish_rows['Exit_Price']
                bearish_rows['Profit'] = bearish_rows['Change']*bearish_rows['Quantity']
                bearish_rows['Type'] ='Sell'
                ticker_trade_rows=pd.concat([bearish_rows,ticker_trade_rows], ignore_index=True)
        return ticker_trade_rows
    else:
        return trading_rows