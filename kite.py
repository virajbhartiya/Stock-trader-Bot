import yfinance as yf
import pandas_datareader as pdr
import pandas_ta as ta
from kiteconnect import KiteConnect
import time

tokenList = ['TCS.NS', 'TATASTEEL.NS', 'BHARTIARTL.NS']
interval = '15m'


api_key = "api_key"
access_token = "access_token"
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


def getCurrentPrice(token):
    tickerData = yf.Ticker(token)
    todayData = tickerData.history(period='1d')
    currentPrice = todayData['Close'][0]
    return currentPrice


def getRSI(history):  # Relative Strength Index
    delta = history['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(15).mean()
    avg_loss = loss.rolling(15).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    last_rsi = rsi.tail(1)[0]
    return last_rsi


def getEMA(history):  # Exponential Moving Average
    history['EMA'] = history['Close'].ewm(span=50).mean()

    last_ema = history['EMA'].tail(1)[0]
    return last_ema


def getSMA(history):  # Simple Moving Average
    sma_50 = history["Close"].rolling(window=50).mean()
    return sma_50[-1]


def getMACD(history):  # Moving Average Convergence Divergence
    df = history[['Close']]

    df["macd"], df["macd_signal"], df["macd_hist"] = ta.macd(
        df["Close"], fast=12, slow=26)

    # Generate the buy and sell signals
    df['buy'] = df['macd'] > df['macd_signal']
    df['sell'] = df['macd'] < df['macd_signal']
    print("BUY: ", df['buy'][-1])
    print("SELL: ", df['sell'][-1])
    if df['buy'][-1]:
        return 'BUY'
    elif df['sell'][-1]:
        return 'SELL'
    return None


def placeBuyOrder(token, price):
    print("BUY: ", token, " at ",  str(price))
    order = kite.place_order(tradingsymbol=token[:-3],
                             exchange=kite.EXCHANGE_NSE,
                             transaction_type=kite.TRANSACTION_TYPE_BUY,
                             quantity=1,
                             variety=kite.VARIETY_AMO,
                             order_type=kite.ORDER_TYPE_MARKET,
                             product=kite.PRODUCT_CNC,
                             validity=kite.VALIDITY_DAY)


def placeSellOrder(token, price):
    print("SELL: ", token, " at ", str(price))
    order = kite.place_order(tradingsymbol=token[:-3],
                             exchange=kite.EXCHANGE_NSE,
                             transaction_type=kite.TRANSACTION_TYPE_SELL,
                             quantity=1,
                             variety=kite.VARIETY_AMO,
                             order_type=kite.ORDER_TYPE_MARKET,
                             product=kite.PRODUCT_CNC,
                             validity=kite.VALIDITY_DAY)


def run():
    balance = 10000
    while True:
        countdown(60)
        print('Balance: ', balance)
        for token in tokenList:
            ticker = yf.Ticker(token)
            history = ticker.history(interval=interval)

            currentPrice = getCurrentPrice(token)

            RSI = getRSI(history)
            EMA = getEMA(history)
            SMA = getSMA(history)
            MACD = getMACD(history)

            print("Current Price: ", currentPrice)
            print("RSI: ", RSI)
            print("SMA: ", SMA)
            print("EMA: ", EMA)
            print("MACD: ", MACD)

            print('***************************************')

            # if MACD == 'BUY':
            if (currentPrice > EMA) and (currentPrice > SMA) and (RSI <= 30):
                placeBuyOrder(token, currentPrice)
                balance = balance - currentPrice
            # if MACD == 'SELL':
            if (currentPrice < EMA) and (currentPrice < SMA) and (RSI >= 70):
                placeSellOrder(token, currentPrice)
                balance = balance + currentPrice


run()
