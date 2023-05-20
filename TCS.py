import yfinance as yf
import pandas_datareader as pdr
import pandas_ta as ta

# from kiteconnect import KiteConnect
import time

tokenList = ["TCS.NS"]
interval = "1m"

api_key = "api_key"
access_token = "access_token"
# kite = KiteConnect(api_key=api_key)
# kite.set_access_token(access_token)


def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = "{:02d}:{:02d}".format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


def getCurrentPrice(token):
    tickerData = yf.Ticker(token)
    todayData = tickerData.history(period="1d")
    currentPrice = todayData["Close"][0]
    return currentPrice


def getRSI(history):  # Relative Strength Index
    delta = history["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(15).mean()
    avg_loss = loss.rolling(15).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    last_rsi = rsi.tail(1)[0]
    return last_rsi


def getEMA(history):  # Exponential Moving Average
    history["EMA"] = history["Close"].ewm(span=50).mean()

    last_ema = history["EMA"].tail(1)[0]
    return last_ema


def getSMA(history):  # Simple Moving Average
    sma_50 = history["Close"].rolling(window=50).mean()
    return sma_50[-1]


def getMACD(history):  # Moving Average Convergence Divergence
    df = history[["Close"]].copy()

    macd, macd_signal, macd_hist = ta.macd(df["Close"], fast=12, slow=26)

    df.loc[:, "macd"] = macd
    df.loc[:, "macd_signal"] = macd_signal
    df.loc[:, "macd_hist"] = macd_hist

    df.loc[:, "buy"] = df["macd"] > df["macd_signal"]
    df.loc[:, "sell"] = df["macd"] < df["macd_signal"]

    print("BUY: ", df["buy"][-1])
    print("SELL: ", df["sell"][-1])

    if df["buy"][-1]:
        return "BUY"
    elif df["sell"][-1]:
        return "SELL"

    return None


def placeBuyOrder(token, price):
    print("BUY: ", token, " at ", str(price))
    # order = kite.place_order(tradingsymbol=token[:-3],
    #                          exchange=kite.EXCHANGE_NSE,
    #                          transaction_type=kite.TRANSACTION_TYPE_BUY,
    #                          quantity=1,
    #                          variety=kite.VARIETY_AMO,
    #                          order_type=kite.ORDER_TYPE_MARKET,
    #                          product=kite.PRODUCT_CNC,
    #                          validity=kite.VALIDITY_DAY)


def placeSellOrder(token, price):
    print("SELL: ", token, " at ", str(price))
    # order = kite.place_order(tradingsymbol=token[:-3],
    #                          exchange=kite.EXCHANGE_NSE,
    #                          transaction_type=kite.TRANSACTION_TYPE_SELL,
    #                          quantity=1,
    #                          variety=kite.VARIETY_AMO,
    #                          order_type=kite.ORDER_TYPE_MARKET,
    #                          product=kite.PRODUCT_CNC,
    #                          validity=kite.VALIDITY_DAY)


def run():
    balance = 0  # Initialize balance with 0
    owned_stocks = {}  # Dictionary to store currently owned stocks and their buy prices
    while True:
        # Get the balance only once
        if balance == 0:
            balance = 10000
            print("Balance: ", balance)

        owned_stock_info = (
            []
        )  # List to store stock information for currently owned stocks

        for token in tokenList:
            ticker = yf.Ticker(token)
            history = ticker.history(interval=interval)

            currentPrice = getCurrentPrice(token)
            RSI = getRSI(history)
            EMA = getEMA(history)
            SMA = getSMA(history)
            MACD = getMACD(history)

            # Check if the stock is currently owned
            if token in owned_stocks:
                owned_price = owned_stocks[token]
                profit_loss = currentPrice - owned_price  # Calculate profit/loss
                owned_stock_info.append((token, currentPrice, profit_loss))

            print("Current Price: {:.2f}".format(currentPrice))
            print("RSI: {:.2f}".format(RSI))
            print("SMA: {:.2f}".format(SMA))
            print("EMA: {:.2f}".format(EMA))
            print("MACD: ", MACD)
            print("***************************************")

            if (currentPrice > EMA) and (currentPrice > SMA) and (RSI <= 30):
                if balance >= currentPrice:  # Check if sufficient balance is available
                    placeBuyOrder(token, currentPrice)
                    balance -= currentPrice  # Deduct the current price from the balance
                    owned_stocks[
                        token
                    ] = currentPrice  # Add the currently owned stock and its buy price to the dictionary

            if (currentPrice < EMA) and (currentPrice < SMA) and (RSI >= 70):
                if token in owned_stocks:  # Check if the stock is currently owned
                    placeSellOrder(token, currentPrice)
                    balance += currentPrice  # Add the current price to the balance
                    del owned_stocks[
                        token
                    ]  # Remove the stock from the owned_stocks dictionary

        # Print the stock information for currently owned stocks
        for stock_info in owned_stock_info:
            print("Owned Stock: ", stock_info[0])
            print("Quantity: 1")
            print("Current Price: {:.2f}".format(stock_info[1]))
            print("Profit/Loss: {:.2f}".format(stock_info[2]))
            print("***************************************")

        countdown(60)


run()
