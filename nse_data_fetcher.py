import yfinance as yf
import pandas as pd
import numpy as np
import talib as ta



def fetch_data(ticker_symbol,candleinterval,timeperiod):
    custom_names = ['Close','High','Low','Open','Volume','SMA_9','SMA_26','SMA_50','RSI_14']
    data = yf.download(ticker_symbol, interval=candleinterval, period=timeperiod, progress=False, auto_adjust=True)
    data['SMA_9'] = data['Close'].rolling(window=9,min_periods=1).mean()
    data['SMA_26'] = data['Close'].rolling(window=26,min_periods=1).mean()
    data['SMA_50'] = data['Close'].rolling(window=50,min_periods=1).mean()
    data["RSI"] = ta.RSI(data["Close"], length=14)
    data.dropna(inplace=True)
    data.columns = custom_names
    try:
        data.index = data.index.tz_convert('Asia/Kolkata')
    except TypeError:
        data.index = data.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
    data_newest_first = data.sort_index(ascending=False)
    
    # data_newest_first.to_csv('SBIN_60days.csv')
    return data_newest_first