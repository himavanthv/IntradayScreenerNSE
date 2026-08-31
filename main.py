from prepare_data import download_data, single_data
import pandas as pd
import numpy
from datetime import datetime, date, timedelta
import sys
from ModelBuilder import volume_indication, crossover









def volume_momentum():
    #time_intervals=['5m','15m','30m','60m']
    time_intervals=['15m']
    #df_excel = pd.read_csv("AllOptionsStocks-Test.csv")
    df_excel = pd.read_csv("AllOptionsStocks.csv")
    #df_excel = pd.read_csv("AllOptionsStocks-All.csv")
    #df_excel = pd.read_csv('Nifty100.csv')
    backtesting_flag= False
    backtesting_result=pd.DataFrame()
    for item in time_intervals:
        data = download_data(item,df_excel,backtesting_flag)
        tickers_list = df_excel["Symbol"].dropna().tolist()
        for ticker in tickers_list:
            df=pd.DataFrame()
            try:
                df = single_data(data,ticker, item)
                if len(df) ==0:
                    continue
            except Exception as e: 
                print(f'Error {e} occurred for ticker {ticker}')
                continue
            try:
                backtesting_result = pd.concat([backtesting_result, volume_indication(df,item,backtesting_flag).drop_duplicates(subset=['DateStr'], keep='first')], ignore_index=True)
            except Exception as e:
                print(f"Backtesting failed for {ticker}")
                print(f"Error {e}")
                continue
    if backtesting_flag:
        backtesting_result.to_csv(f'BackTesting_result_{item}.csv')
        print('Completed and saved to BackTesting_result')
    else:
        markdown_msg = backtesting_result[backtesting_result['DateStr'] == str(datetime.now())[:10]]
        markdown_msg = markdown_msg.sort_values(by='Symbol')
        trade_data = markdown_msg[['Symbol','Type','Time','Average_Price','Candle_Interval','Model']].to_markdown(index=False)
        formatted_payload = f"```\n{trade_data}\n```"
        print(formatted_payload)
        #current_time_ist = datetime.now(ist_timezone)
        #send_telegram_notification("Analysis report at Time:"+ current_time_ist.strftime("%H:%M:%S") +" for interval "+candleInterval +"\n"+formatted_payload)
def ma_crossover():
    time_intervals=['60m','1d']
    #df_excel = pd.read_csv("AllOptionsStocks-Test.csv")
    #df_excel = pd.read_csv("AllOptionsStocks.csv")
    #df_excel = pd.read_csv("AllOptionsStocks-All.csv")
    df_excel = pd.read_csv('Nifty100.csv')
    backtesting_flag= False
    backtesting_result=pd.DataFrame()
    for item in time_intervals:
        data = download_data(item,df_excel,backtesting_flag)
        tickers_list = df_excel["Symbol"].dropna().tolist()
        for ticker in tickers_list:
            df=pd.DataFrame()
            df = single_data(data,ticker)
            try:
                backtesting_result = pd.concat([backtesting_result, crossover(df,item,backtesting_flag)], ignore_index=True)
            except Exception as e:
                print(f"Backtesting failed for {ticker}")
                print(f"Error {e}")
                continue
    if backtesting_flag:
        backtesting_result.to_csv(f'BackTesting_result_MACross_{candleInterval}.csv')
        print('Completed and saved to BackTesting_result')
    else:
        print(backtesting_result)
        markdown_msg = backtesting_result[backtesting_result['DateStr'] == str(datetime.now())[:10]]
        trade_data = markdown_msg[['Symbol','Type','Time','Average_Price','Candle_Interval','Model']].to_markdown(index=False)
        formatted_payload = f"```\n{trade_data}\n```"
        #current_time_ist = datetime.now(ist_timezone)
        #send_telegram_notification("Analysis report at Time:"+ current_time_ist.strftime("%H:%M:%S") +" for interval "+candleInterval +"\n"+formatted_payload)


methods = {
    "volume": volume_momentum,
    "macrossover": ma_crossover,
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_intraday.py [volume|macrossover]")
        sys.exit(1)
    argument = sys.argv[1].lower()
    func = methods.get(argument)
    if func:
        func()
    else:
        print(f"Error: Method '{argument}' not found.")



