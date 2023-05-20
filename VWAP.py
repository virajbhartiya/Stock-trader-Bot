import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time


tokenList = ["TCS.NS"]
interval = "1m"
initial_balance = 10000
trading_hours = datetime.strptime("15:30", "%H:%M").time()


def getHistoricalData(token):
    data = yf.download(token, period="1d", interval=interval)
    data.reset_index(inplace=True)
    return data


def calculateVWAP(df):
    df["Typical Price"] = (df["High"] + df["Low"] + df["Close"]) / 3
    df["Volume x Typical Price"] = df["Volume"] * df["Typical Price"]
    df["Cumulative Volume"] = df["Volume"].cumsum()
    df["Cumulative VWAP"] = (
        df["Volume x Typical Price"].cumsum() / df["Cumulative Volume"]
    )
    return df


def placeBuyOrder(token, price, balance):
    if balance >= price:
        print("BUY:", token, "at", str(price))
        balance -= price
        return True, balance
    else:
        print("Insufficient balance to buy:", token)
        return False, balance


def placeSellOrder(token, price):
    if initial_balance < 0:
        print("SELL:", token, "at", str(price))
        initial_balance += price
        return True
    else:
        print("Cannot sell", token, "as it was not bought.")
        return False


def runSandbox(token, balance):
    df = getHistoricalData(token)

    while datetime.now().time() < trading_hours:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_data = yf.download(token, period="1d", interval=interval)
        current_price = current_data["Close"].iloc[-1]

        df = calculateVWAP(df)
        current_vwap = df["Cumulative VWAP"].iloc[-1]

        if current_price > current_vwap:
            if token not in owned_stocks:
                placed_order, balance = placeBuyOrder(token, current_price, balance)
                if placed_order:
                    owned_stocks[token] = current_price
        elif current_price < current_vwap:
            if token in owned_stocks:
                placed_order, balance = placeSellOrder(token, current_price, balance)
                if placed_order:
                    del owned_stocks[token]

        net_balance = balance + sum(owned_stocks.values()) if owned_stocks else balance
        print("Net Balance at", current_time, ":", net_balance)

        time.sleep(60)  # Wait for 1 minute


owned_stocks = {}
runSandbox(tokenList[0], initial_balance)
