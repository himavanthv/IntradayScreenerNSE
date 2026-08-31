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

def volume_indication(data,candleInterval,backtesting_flag):
    data['Candle_Interval']=candleInterval
    data['Model']='VolumeBased'
## ------------------ Configuration Based on Different Candle Intervals -----------------##
    if candleInterval=='1m':
        exit_after_candles=120
        value_of_candle = 20000000
        enter_after_candles = 1
        candle_change=1
        rsi_high=90
        rsi_low=10
    if candleInterval=='5m':
        exit_after_candles = 300
        candle_change=1
        value_of_candle = 100000000
        enter_after_candles = 2
        rsi_high=80
        rsi_low=20
    if candleInterval =='15m':
        exit_after_candles = 15
        value_of_candle = 50000000
        enter_after_candles = 2
        candle_change=1.5
        rsi_high=80
        rsi_low=20
    if candleInterval =='30m':
        candle_change=1.5
        exit_after_candles = 20
        value_of_candle = 100000000
        enter_after_candles = 1
        rsi_high=80
        rsi_low=20
    if candleInterval=='60m':
        candle_change=3
        exit_after_candles = 2
        value_of_candle = 100000000
        enter_after_candles = 1
        rsi_high=80
        rsi_low=20
    if candleInterval=='1d':
        value_of_candle = 500000000
        exit_after_candles = 1
        enter_after_candles = 1
        rsi_high=70
        rsi_low=30
    capital = 10000
    gap_today = 1
    intraday_capital = capital*5
    if candleInterval !='1d':
        total_taxes = (intraday_capital*2)*0.00032
        total_brokerage = 20 # Algo flat charges # manual 40 Rs
    else:
        # Swing Trade 0
        total_taxes = 0
        total_brokerage = 0 # Algo flat charges # manual 40 Rs
    ticker_trade_rows = pd.DataFrame()
    if candleInterval =='1d':
        ##### 1 day interval is for Positional/Swing for Momentum
        #bullish_indices = np.where((data['DistanceFromMA9_Open']<=1) & (data['RSI']>60) & (data['MaVariance']<=1) & (data['MaVariance']>=0) & (data['MaVariance']<=10) & (data['Gap_Open']<3) & (data['RSI']>data['RSI_Change']) & ((data['CrossOver']==1) | (data['CrossOver'].shift(-1)==1) | (data['CrossOver'].shift(-2)==1)| (data['CrossOver'].shift(-3)==0)| (data['CrossOver'].shift(-4)==0)| (data['CrossOver'].shift(-5)==0)| (data['CrossOver'].shift(-6)==0)| (data['CrossOver'].shift(-7)==0)| (data['CrossOver'].shift(-8)==0)| (data['CrossOver'].shift(-9)==0)))[0].tolist()
        #bearish_indices = np.where((data['DistanceFromMA9_Open']>=-1) & (data['RSI']<40) & (data['MaVariance']>=-1) & (data['MaVariance']<=0) & (data['MaVariance']>=-10) & (data['Gap_Open']<3) & (data['RSI']<data['RSI_Change']) & ((data['CrossOver']==-1) | (data['CrossOver'].shift(-1)==-1) | (data['CrossOver'].shift(-2)==-1)| (data['CrossOver'].shift(-3)==0)| (data['CrossOver'].shift(-4)==0)| (data['CrossOver'].shift(-5)==0)| (data['CrossOver'].shift(-6)==0)| (data['CrossOver'].shift(-7)==0)| (data['CrossOver'].shift(-8)==0)| (data['CrossOver'].shift(-9)==0)))[0].tolist()
        ##### Over Bought and Over Sold
        #bullish_indices = np.where((data['DistanceFromMA9_Close'] <-5) & (data['RSI']<30) & (data['MaVariance']<=-7) & (data['RSI']<=30) & ((data['CrossOver']==1) | (data['CrossOver'].shift(-1)==1) | (data['CrossOver'].shift(-2)==1)| (data['CrossOver'].shift(-3)==1)| (data['CrossOver'].shift(-4)==1)| (data['CrossOver'].shift(-5)==1)| (data['CrossOver'].shift(-6)==1)| (data['CrossOver'].shift(-7)==1)| (data['CrossOver'].shift(-8)==1)| (data['CrossOver'].shift(-9)==1)))[0].tolist()
        #bearish_indices = np.where((data['DistanceFromMA9_Close'] >5) & (data['RSI']>70) & (data['MaVariance']>=7) & (data['RSI']>=70) & ((data['CrossOver']==-1) | (data['CrossOver'].shift(-1)==-1) | (data['CrossOver'].shift(-2)==-1)| (data['CrossOver'].shift(-3)==-1)| (data['CrossOver'].shift(-4)==-1)| (data['CrossOver'].shift(-5)==-1)| (data['CrossOver'].shift(-6)==-1)| (data['CrossOver'].shift(-7)==-1)| (data['CrossOver'].shift(-8)==-1)| (data['CrossOver'].shift(-9)==-1)))[0].tolist()
        bullish_indices = np.where((data['DistanceFromMA9_Close'] <-5) & (data['MaVariance']<=-5) & (data['RSI']<=30) & ((data['CrossOver']==1) | (data['CrossOver'].shift(-1)==0) | (data['CrossOver'].shift(-2)==0)| (data['CrossOver'].shift(-3)==0)| (data['CrossOver'].shift(-4)==0)| (data['CrossOver'].shift(-5)==0)| (data['CrossOver'].shift(-6)==0)))[0].tolist()
        bearish_indices = np.where((data['DistanceFromMA9_Close'] >5) & (data['MaVariance']>=5) & (data['RSI']>=70) & ((data['CrossOver']==-1) | (data['CrossOver'].shift(-1)==0) | (data['CrossOver'].shift(-2)==0)| (data['CrossOver'].shift(-3)==0)| (data['CrossOver'].shift(-4)==0)| (data['CrossOver'].shift(-5)==0)| (data['CrossOver'].shift(-6)==0)))[0].tolist()
        ### For checking only Indexes
        #bullish_indices = np.where((data['RSI']<=30) & ((data['CrossOver']==0) | (data['CrossOver'].shift(-1)==0) | (data['CrossOver'].shift(-2)==0)| (data['CrossOver'].shift(-3)==0)| (data['CrossOver'].shift(-4)==0)| (data['CrossOver'].shift(-5)==0)))[0].tolist()
        #bearish_indices = np.where((data['RSI']>=70) & ((data['CrossOver']==0) | (data['CrossOver'].shift(-1)==0) | (data['CrossOver'].shift(-2)==0)| (data['CrossOver'].shift(-3)==0)| (data['CrossOver'].shift(-4)==0)| (data['CrossOver'].shift(-5)==0)))[0].tolist()
    else:
        ############## - All below are for Intraday   
        ############## - OverBought and OverSold - ###############
        #bullish_indices = np.where((data['DistanceBetween_Close_SMA125'] < -3) & (data['RSI_50']<=30) & (data['MaVariance_Month']<=-5) & ((data['CrossOver']==1) | (data['CrossOver'].shift(-1)==1) | (data['CrossOver'].shift(-2)==1)| (data['CrossOver'].shift(-3)==1)| (data['CrossOver'].shift(-4)==1)| (data['CrossOver'].shift(-5)==1)| (data['CrossOver'].shift(-6)==1)| (data['CrossOver'].shift(-7)==1)| (data['CrossOver'].shift(-8)==1)| (data['CrossOver'].shift(-9)==1)| (data['CrossOver'].shift(-10)==1)| (data['CrossOver'].shift(-11)==1)| (data['CrossOver'].shift(-12)==1)| (data['CrossOver'].shift(-13)==1)))[0].tolist()
        #bearish_indices = np.where((data['DistanceBetween_Close_SMA125'] > 3) & (data['RSI_50']>=70) & (data['MaVariance_Month']>=5) & ((data['CrossOver']==1) | (data['CrossOver'].shift(-1)==-1) | (data['CrossOver'].shift(-2)==-1)| (data['CrossOver'].shift(-3)==-1)| (data['CrossOver'].shift(-4)==-1)| (data['CrossOver'].shift(-5)==-1)| (data['CrossOver'].shift(-6)==-1)| (data['CrossOver'].shift(-7)==-1)| (data['CrossOver'].shift(-8)==-1)| (data['CrossOver'].shift(-9)==-1)| (data['CrossOver'].shift(-10)==-1)| (data['CrossOver'].shift(-11)==-1)| (data['CrossOver'].shift(-12)==-1)| (data['CrossOver'].shift(-13)==-1)))[0].tolist()
        ########### - Volume Momentum based on High Sell or High Buy and Candle Value - #########
        #bullish_indices = np.where((data['CandleChange'] >= 0.5) & (data['MaVariance'] >= 0) & (data['CandleChange'] <= 0.8) & (data['CandleChange'] > data['Sum_CandleChange']) & (data['DistanceFromMA9_Bull']>0) & (data['DistanceFromMA9_Bull']<=0.3) & (data['Volume']>=data['SumOfVolume']) & (data['Volume']*data['Open'] >= value_of_candle) & (((data['Close']-data['PrevClose'])/data['PrevClose'])*100 >= 0.5) & (data['Gap_Open'] <= gap_today) & (((data['Close'] - data['PrevClose'])/data['PrevClose'])*100 <= 1))[0].tolist()
        #bearish_indices = np.where((data['CandleChange'] <= -0.5) & (data['MaVariance'] <= 0) & (data['CandleChange'] >= -0.8) & (data['CandleChange'] < data['Sum_CandleChange']) & (data['DistanceFromMA9_Bear']>0) & (data['DistanceFromMA9_Bear']<=0.3) & (data['Volume']>=data['SumOfVolume']) & (data['Volume']*data['Open'] >= value_of_candle) & (((data['Close']-data['PrevClose'])/data['PrevClose'])*100 <= -0.5) & (data['Gap_Open'] <= gap_today) & (((data['Close'] - data['PrevClose'])/data['PrevClose'])*100 >= -1))[0].tolist()
        #bullish_indices = np.where((data['CandleChange'] >= 0.25) &  (data['Volume'] > data['SumOfVolume']) & (data['DistanceBetween_Close_SMA125'] > -0.25 ) & (data['DistanceBetween_Close_SMA125'] < 0.5 ) & (data['Volume']*data['Open'] >= value_of_candle) & (data['Open'] > data['Close']))[0].tolist()
        #bearish_indices = np.where((data['CandleChange'] <= -0.25) & (data['Volume'] > data['SumOfVolume']) & (data['DistanceBetween_Close_SMA125'] < 0.25 ) & (data['DistanceBetween_Close_SMA125'] > -0.5 ) & (data['Volume']*data['Open'] >= value_of_candle) & (data['Close'] > data['Open']))[0].tolist()
        #bullish_indices = np.where((data['DistanceBetween_Close_SMA125'] < -2) & (data['DistanceBetween_Close_SMA125'] > -4) & (data['MaVariance'] <= -0.25) & (data['RSI_50']<=25) & (data['SMA_2500']<data['Close']))[0].tolist()
        #bearish_indices = np.where((data['DistanceBetween_Close_SMA125'] > 2) & (data['DistanceBetween_Close_SMA125'] < 4) & (data['MaVariance'] >= 0.25) & (data['RSI_50']>=75) & (data['SMA_2500']>data['Close']))[0].tolist()
        # Momentum
        #bullish_indices = np.where((data['DistanceBetween_Close_SMA125']>=1) & (data['DistanceFromMA9_Open']<=1) & (data['DistanceBetween_Close_SMA125']<=5) &  (data['MaVariance_Month']>1) & (data['RSI_50']>65) & ((data['CrossOver']==1) | (data['CrossOver'].shift(-1)==1) | (data['CrossOver'].shift(-2)==1)| (data['CrossOver'].shift(-3)==1)| (data['CrossOver'].shift(-4)==1)| (data['CrossOver'].shift(-5)==1)| (data['CrossOver'].shift(-6)==1)| (data['CrossOver'].shift(-7)==1)| (data['CrossOver'].shift(-8)==1)| (data['CrossOver'].shift(-9)==1)| (data['CrossOver'].shift(-10)==1)| (data['CrossOver'].shift(-11)==1)| (data['CrossOver'].shift(-12)==1)| (data['CrossOver'].shift(-13)==1)))[0].tolist()
        #bearish_indices = np.where((data['DistanceBetween_Close_SMA125']<=-1) & (data['DistanceFromMA9_Open']>=-1) & (data['DistanceBetween_Close_SMA125']>=-5) & (data['MaVariance_Month']<-1) & (data['RSI_50']<35) & ((data['CrossOver']==-1) | (data['CrossOver'].shift(-1)==-1) | (data['CrossOver'].shift(-2)==-1)| (data['CrossOver'].shift(-3)==-1)| (data['CrossOver'].shift(-4)==-1)| (data['CrossOver'].shift(-5)==-1)| (data['CrossOver'].shift(-6)==-1)| (data['CrossOver'].shift(-7)==-1)| (data['CrossOver'].shift(-8)==-1)| (data['CrossOver'].shift(-9)==-1)| (data['CrossOver'].shift(-10)==-1)| (data['CrossOver'].shift(-11)==-1)| (data['CrossOver'].shift(-12)==-1)| (data['CrossOver'].shift(-13)==-1)))[0].tolist()    
        ######### Currently Over Sold and Over Bought will work only on 15 M due to candle limits in YahooFinance for lower candles
        ############ Below logic is valid only for 15 Minute Candles #########
        bullish_indices = np.where((data['DistanceBetweenClose_SMA650'] < -10) & (data['RSI_25']<=30) & (data['MaVariance_Month15']<=-2) & ((data['CrossOver']==1) | (data['CrossOver'].shift(-1)==1) | (data['CrossOver'].shift(-2)==1) | (data['CrossOver'].shift(-3)==1) | (data['CrossOver'].shift(-4)==1) | (data['CrossOver'].shift(-5)==1)))[0].tolist()
        bearish_indices = np.where((data['DistanceBetweenClose_SMA650'] > 10) & (data['RSI_25']>=70) & (data['MaVariance_Month15']>=2) & ((data['CrossOver']==-1) | (data['CrossOver'].shift(-1)==-1) | (data['CrossOver'].shift(-2)==-1) | (data['CrossOver'].shift(-3)==-1) | (data['CrossOver'].shift(-4)==-1) | (data['CrossOver'].shift(-5)==-1)))[0].tolist()

    
    bullish_found_rows = data.iloc[bullish_indices]
    bearish_found_rows = data.iloc[bearish_indices]
    bullish_found_rows['Type'] = 'Buy'
    bearish_found_rows['Type'] = 'Sell'
    trading_rows = pd.concat([bullish_found_rows,bearish_found_rows], ignore_index=True)
    if backtesting_flag and candleInterval=='1d':
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
        #if len(ticker_trade_rows) >=1:
            #ticker_trade_rows.loc[ticker_trade_rows['Profit'] < -500, 'Profit'] = -500
        return ticker_trade_rows                
    elif backtesting_flag and (candleInterval=='5m'or candleInterval=='15m' or candleInterval=='30m' or candleInterval=='60m'):
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
                bullish_rows['EntryPrice']= bullish_rows['Open']          
                bullish_rows['Quantity'] = intraday_capital/bullish_rows['EntryPrice']
                bullish_rows['Change'] = bullish_rows['Exit_Price']-bullish_rows['EntryPrice']
                bullish_rows['Profit'] = bullish_rows['Change']*bullish_rows['Quantity']
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
                bearish_rows['EntryPrice']=bearish_rows['Open']
                bearish_rows['Quantity'] = intraday_capital/bearish_rows['EntryPrice']
                bearish_rows['Change'] = bearish_rows['EntryPrice']-bearish_rows['Exit_Price']
                bearish_rows['Profit'] = bearish_rows['Change']*bearish_rows['Quantity']
                bearish_rows['Type'] ='Sell'
                one_day_rows = bearish_rows
                ticker_trade_rows=pd.concat([one_day_rows,ticker_trade_rows], ignore_index=True)
        if len(ticker_trade_rows) >=1:
            ticker_trade_rows.loc[ticker_trade_rows['Profit'] < -500, 'Profit'] = -500
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