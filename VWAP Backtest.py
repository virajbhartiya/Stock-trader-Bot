import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, time, timedelta

tokenList = ["TCS.NS"]
interval = "1m"
initial_balance = 5000
trading_hours_start = time(9, 15)  # Trading hours start at 9:15 AM
trading_hours_end = time(15, 45)  # Trading hours end at 3:45 PM
quantity = 0
net_balances = []  # List to store net balances
buy_points = []  # List to store buy points
sell_points = []  # List to store sell points
quantities = []  # List to store quantities of stocks owned


def getHistoricalData(token):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    data = yf.download(token, start=start_date, end=end_date, interval=interval)
    return data


def calculateVWAP(df):
    df["TP"] = (df["High"] + df["Low"] + df["Close"]) / 3
    df["VWAP"] = (df["TP"] * df["Volume"]).cumsum() / df["Volume"].cumsum()
    return df


def placeBuyOrder(token, price, balance):
    global quantity  # Declare quantity as a global variable
    if balance >= price:
        print("BUY:", token, "at", str(price))
        # num_stocks = 1
        num_stocks = (
            balance // price
        )  # Calculate the maximum number of stocks that can be bought
        balance -= num_stocks * price  # Deduct the cost from the balance
        quantity += num_stocks  # Increase the quantity by the number of stocks bought
        return True, balance
    else:
        print("Insufficient balance to buy:", token)
        return False, balance


def placeSellOrder(token, price, balance):
    global quantity  # Declare quantity as a global variable
    if quantity > 0:
        print("SELL:", token, "at", str(price))
        balance += price
        quantity -= 1
        return True, balance
    else:
        print("No stocks owned to sell:", token)
        return False, balance


def backtest(token):
    df = getHistoricalData(token)
    df = calculateVWAP(df)
    balance = initial_balance
    net_profit_loss = []  # List to store the net profit/loss

    for index, row in df.iterrows():
        current_time = index.time()
        current_price = row["Close"]

        if trading_hours_start <= current_time <= trading_hours_end:
            if current_price > row["VWAP"] and balance > current_price:
                placed_order, balance = placeBuyOrder(token, current_price, balance)
                if placed_order:
                    buy_points.append((index, current_price))

            elif current_price < row["VWAP"] and quantity > 0:
                placed_order, balance = placeSellOrder(token, current_price, balance)
                if placed_order:
                    sell_points.append((index, current_price))

        net_balance = balance + (quantity * current_price) if quantity > 0 else balance
        net_balances.append(net_balance)
        quantities.append(quantity)
        net_profit_loss.append(
            net_balance - initial_balance
        )  # Calculate the net profit/loss
        print("Net Balance at", index, ":", net_balance)

    # Plotting the graph with buy/sell indicators, stock price, quantity of stocks owned, and profit/loss
    fig, ax1 = plt.subplots(figsize=(12, 8))
    ax2 = ax1.twinx()

    ax1.plot(df.index, df["Close"], color="blue", label="Stock Price")
    ax1.scatter(*zip(*buy_points), color="green", label="Buy")
    ax1.scatter(*zip(*sell_points), color="red", label="Sell")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Price")
    ax1.grid(True)

    ax2.plot(df.index, quantities, color="orange", label="Quantity Owned")
    ax2.plot(df.index, net_profit_loss, color="purple", label="Profit/Loss")
    ax2.set_ylabel("Quantity/Profit-Loss")
    ax2.grid(True)

    plt.title("VWAP Backtest")
    plt.legend()
    plt.show()


backtest(tokenList[0])
