import numpy as np
import pandas as pd
from datetime import datetime , timedelta, date
from datetime import datetime, date, timedelta
from ModelBuilder import volume_indication, calculate_rsi, calculate_vwap
import time
import pytz
import talib as ta
from pathlib import Path



candleInterval='15m'
dir_path=Path('/home/osboxes/Documents/Intraday-API/Data/Minute15C')
#dir_path=Path('/home/osboxes/Documents/Intraday-API/Data/Minute15C')
backtesting_result=pd.DataFrame()
print(f'Start Time {str(datetime.now())}')
for item in dir_path.iterdir():
    # Check if the item is a file (skips folders)
    if item.is_file():
        df = pd.read_csv(item)
        #print(df.head())
        symbol = item.name.split('_')[0]
        df.columns = ['Date','Open','High','Low','Close','Volume']
        df["SMA_9"] = df['Close'].rolling(window=9,min_periods=9).mean()
        df["SMA_26"] = df['Close'].rolling(window=26,min_periods=26).mean()
        df["SMA_5"] = df['Close'].rolling(window=5,min_periods=5).mean()
        df["SMA_15"] = df['Close'].rolling(window=15,min_periods=15).mean()
        df["SMA_50"] = df['Close'].rolling(window=50,min_periods=50).mean()
        df['RSI']=calculate_rsi(df['Close'],14)
        df['RSI_Change'] = (df['RSI'].shift(1).rolling(window=5).sum())/5
        df['Average_Price']=(df['Open']+df['Close'])/2
        df['SumOfVolume'] = df['Volume'].shift(1).rolling(window=5).sum()
        df['DistanceFromMA9_Close']=((df['Close']- df['SMA_9'])/df['SMA_9'])*100
        df['DistanceFromMA9_Open']=((df['Open']- df['SMA_9'])/df['SMA_9'])*100
        df['MaVariance'] = ((df['SMA_9'] - df['SMA_26'])/df['SMA_26'])*100
        df['CandleChange'] = ((df['Close'] - df['Open'])/df['Open'])*100
        df['Sum_CandleChange'] = (df['CandleChange'].shift(1).rolling(window=20).sum())/20
        df['RSI_Small'] = calculate_rsi(df['Close'],3)
        if candleInterval != '1d' and candleInterval!='60m':
            #df["SMA_125"] = df['Close'].rolling(window=375,min_periods=375).mean()
            #df["SMA_2500"] = df['Close'].rolling(window=7500,min_periods=7500).mean()
            df["SMA_225"] = df['Close'].rolling(window=225,min_periods=225).mean()
            ####### All below items untill DistanceBetweenClose_650 is valid for 15 Minute only
            df["SMA_650"] = df['Close'].rolling(window=650,min_periods=650).mean()
            df["RSI_25"] = calculate_rsi(df['Close'],25)
            df['MaVariance_Month15'] = ((df['SMA_225']-df['SMA_650'])/df['SMA_225'])*100
            df["DistanceBetweenClose_SMA650"] = ((df['Close']-df['SMA_650'])/df['SMA_650'])*100
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
        df['DateStr'] = df['Date'].str[:10]
        df['Time']=df['Date'].str[10:]
        df['Symbol'] = symbol
        df['Average_Price']=(df['Open']+df['Close'])/2
        unique_dates = df['DateStr'].unique()
        reversed_dates = unique_dates[::-1]
        #print(df)
        mapping = dict(zip(reversed_dates, reversed_dates[1:]))
        pattern = f"({'|'.join(mapping.keys())})"
        extracted_keys = df["DateStr"].str.extract(pattern, expand=False)
        df["PrevDate"] = extracted_keys.map(mapping)
        lookup_df = df[['DateStr', 'Close']].sort_index(ascending=False).drop_duplicates(subset=['DateStr'])
        try:
            df = df.merge(
            lookup_df, 
            left_on='PrevDate',
            right_on='DateStr', 
            how='left', 
            suffixes=('', '_Prev')
            )
        except Exception as er:
            print(f"Error {er}")
            continue
        df = df.rename(columns={'Close_Prev': 'PrevClose'}).drop(columns=['DateStr_Prev'])
        df["Date_Temp"] = pd.to_datetime(df["DateStr"])
        dates = df["Date_Temp"].dt.date
        first_opens = df.groupby(dates)["Open"].first()
        df["TodayOpen"] = dates.map(first_opens)
        df = df.drop(columns=["Date_Temp"])
        df['Gap_Open']=((df['TodayOpen']-df['PrevClose'])/df['PrevClose'])*100
        df['Gap_Open'] = df['Gap_Open'].abs()
        df = df.sort_index(ascending=False)
        df =df.dropna()
        try:
            backtesting_result = pd.concat([backtesting_result, volume_indication(df,candleInterval,True).drop_duplicates(subset=['DateStr'], keep='first')], ignore_index=True)
        except Exception as e:
            print(f"Backtesting failed for {symbol}")
            print(f"Error {e}")
            continue
backtesting_result.to_csv(f'BackTesting_result_10Year_{candleInterval}.csv')
print('Completed and saved to BackTesting_result')
print(f'End Time {str(datetime.now())}')