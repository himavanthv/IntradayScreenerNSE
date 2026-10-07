import nse_data_fetcher as nse
import numpy as np
import pandas as pd
from datetime import datetime , timedelta, date
import yfinance as yf
from datetime import datetime, date, timedelta
from ModelBuilder import calculate_rsi, calculate_vwap
import time
import pytz
import talib as ta




def download_data(candleInterval,df_excel,backtesting_flag):
    tickers_list = df_excel["Symbol"].dropna().tolist()
    if backtesting_flag:
        if candleInterval=='1m':
            period_interval = '8d'
        elif candleInterval =='60m' or candleInterval =='1d':
            period_interval = '10y'
        else:
            period_interval ='60d'
    else:
        if candleInterval=='1m':
            period_interval = '8d'
        else:
            period_interval = '60d'
        if candleInterval=='1d':
            period_interval = '1y'
    data = yf.download(tickers_list, interval=candleInterval, period=period_interval, progress=False, auto_adjust=True, group_by = 'ticker')
    print(f'End of Download-{str(datetime.now())} for time interval {candleInterval}')
    return data

def single_data(data,ticker,candleInterval,calling_from):
    if calling_from == 'main':
        try:                                  
            data.index = data.index.tz_convert('Asia/Kolkata')
        except TypeError:
            data.index = data.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
        ist_timezone = pytz.timezone('Asia/Kolkata')
        # df=pd.DataFrame()
    else:
        df = data
    if calling_from == 'main':
        if ticker in data.columns.levels[0]:
            # Extract a clean, single stock DataFrame
            df = data[ticker].dropna(how="all").copy()
            symbol = ticker.split('.')[0]
    df["SMA_9"] = df['Close'].rolling(window=9).mean()
    df["SMA_26"] = df['Close'].rolling(window=26).mean()
    df["SMA_5"] = df['Close'].rolling(window=5).mean()
    df["SMA_15"] = df['Close'].rolling(window=10).mean()
    df["SMA_50"] = df['Close'].rolling(window=50).mean()
    df['RSI']=calculate_rsi(df['Close'],14)
    df['RSI_Change'] = (df['RSI'].shift(1).rolling(window=5).sum())/5
    df['Average_Price']=(df['Open']+df['Close'])/2
    df['SumOfVolume'] = df['Volume'].shift(1).rolling(window=650).sum()
    df['AverageVolume'] = df['SumOfVolume']/650
    df['DistanceFromMA9_Close']=((df['Close']- df['SMA_9'])/df['SMA_9'])*100
    df['DistanceFromMA9_Open']=((df['Open']- df['SMA_9'])/df['SMA_9'])*100
    df['MaVariance'] = ((df['SMA_9'] - df['SMA_26'])/df['SMA_26'])*100
    df['CandleChange'] = ((df['Close'] - df['Open'])/df['Open'])*100
    df['ABS_CandleChange'] = df['CandleChange'].abs()
    df['Sum_CandleChange'] = (df['CandleChange'].shift(1).rolling(window=20).sum())/20
    df['Low_Wick'] = (((df['Open']-df['Low'])/df['Open'])*100).abs()
    df['High_Wick'] = (((df['High']-df['Close'])/df['Close'])*100).abs()
    if candleInterval != '1d' and candleInterval!='60m':
        df["SMA_225"] = df['Close'].rolling(window=225,min_periods=1).mean()
        ####### All below items untill DistanceBetweenClose_650 is valid for 15 Minute only
        df["SMA_650"] = df['Close'].rolling(window=650,min_periods=1).mean()
        df["RSI_25"] = calculate_rsi(df['Close'],25)
        df['RSI25_Change'] = (df['RSI_25'].shift(1).rolling(window=5).sum())/5
        df['MaVariance_Month15'] = ((df['SMA_225']-df['SMA_650'])/df['SMA_225'])*100
        df["DistanceBetweenClose_SMA650"] = ((df['Close']-df['SMA_650'])/df['SMA_650'])*100
        df["DistanceBetweenOpen_SMA225"] = ((df['Open']-df['SMA_225'])/df['SMA_225'])*100
        #df['DistanceFromMA9_Bear']=((df['SMA_9']- df['Open'])/df['SMA_9'])*100
        #df['DistanceBetween_Close_SMA125'] = ((df['Close']-df['SMA_125'])/df['SMA_125'])*100
        #df['MaVariance_Month'] = ((df['SMA_125']-df['SMA_2500'])/df['SMA_2500'])*100
        #df['RSI_50']=calculate_rsi(df['Close'],50)
        #df['RSI50_Change'] = (df['RSI_50'].shift(1).rolling(window=10).sum())/10
    
    bullish_condition = (df['SMA_9'].shift(1) < df['SMA_26'].shift(1)) & (df['SMA_9'] > df['SMA_26'])
    bearish_condition = (df['SMA_9'].shift(1) > df['SMA_26'].shift(1)) & (df['SMA_9'] < df['SMA_26'])
    bullish_condition1 = (df['SMA_5'].shift(1) < df['SMA_15'].shift(1)) & (df['SMA_5'] > df['SMA_15'])
    bearish_condition1 = (df['SMA_5'].shift(1) > df['SMA_15'].shift(1)) & (df['SMA_5'] < df['SMA_15'])
    df['CrossOver_Small'] = bullish_condition1.astype(int) - bearish_condition1.astype(int)
    df['CrossOver'] = bullish_condition.astype(int) - bearish_condition.astype(int)
    df['CrossOver1'] = bullish_condition1.astype(int) - bearish_condition1.astype(int)
    if calling_from == 'main':
        df['DateStr'] = df.index.astype(str).str[:10]
        df['Date_Time']=df.index.astype(str)
        df['Time']=df.index.astype(str).str[10:]
    else:
        df['DateStr'] = df['Date'].astype(str).str[:10]
        df['Date_Time'] = df['Date'].astype(str)
        df['Time'] = df['Date'].astype(str).str[10:]
    #df['Year_Month']= f'{df['DateStr'].str[4:]}-{df['DateStr'].str[-5:-3]}'
    df['Symbol'] = ticker
    unique_dates = df['DateStr'].unique()
    reversed_dates = unique_dates[::-1]
    prev_date_map = {
        reversed_dates[i]: reversed_dates[i + 1] for i in range(len(reversed_dates) - 1)
    }
    df["PrevDate"] = df["DateStr"].map(prev_date_map)
    #mapping = dict(zip(reversed_dates, reversed_dates[1:]))
    #pattern = f"({'|'.join(mapping.keys())})"
    #extracted_keys = df["DateStr"].str.extract(pattern, expand=False)
    #df["PrevDate"] = extracted_keys.map(mapping)
    lookup_df = df[['DateStr', 'Close']].sort_index(ascending=False).drop_duplicates(subset=['DateStr'])
    try:
        df = df.merge(
        lookup_df, 
        left_on='PrevDate',
        right_on='DateStr', 
        how='left', 
        suffixes=('', '_Prev')
        )
        df = df.rename(columns={'Close_Prev': 'PrevClose'}).drop(columns=['DateStr_Prev'])
        df['DistanceBetweenPrevClose_225']= ((df['PrevClose']-df['SMA_225'])/df['SMA_225'])*100
        df['DistanceBetweenPrevClose_650']= ((df['PrevClose']-df['SMA_650'])/df['SMA_650'])*100
        df["Date_Temp"] = pd.to_datetime(df["DateStr"])
        dates = df["Date_Temp"].dt.date
        first_opens = df.groupby(dates)["Open"].first()
        df["TodayOpen"] = dates.map(first_opens)
        df['ChangeSinceYesterday'] = ((df['Close']-df['PrevClose'])/df['PrevClose'])*100
        df['ChangeSinceMrng'] = ((df['Close']-df['TodayOpen'])/df['TodayOpen'])*100
        df = df.drop(columns=["Date_Temp"])
        df['Gap_Open']=((df['TodayOpen']-df['PrevClose'])/df['PrevClose'])*100
        # df['Gap_Open'] = df['Gap_Open'].abs()
        df = df.sort_index(ascending=False)
        df = df.dropna()
        #df.to_csv('Bajahdl.csv')
    except Exception as er:
        print(f'Error {er}')
    return df