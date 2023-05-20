import yfinance as yf
import matplotlib.pyplot as plt

symbol = "TCS.NS"


def calculateMomentum(history, period):
    momentum = (history["Close"] / history["Close"].shift(period)) - 1
    return momentum


def placeBuyOrder(symbol, price):
    print("BUY:", symbol, "at", str(price))
    # Add your logic to execute a buy order


def placeSellOrder(symbol, price):
    print("SELL:", symbol, "at", str(price))
    # Add your logic to execute a sell order


def backtest(symbol, momentum_period, threshold):
    df = yf.download(symbol, period="1w", interval="1m")
    df["Momentum"] = calculateMomentum(df, momentum_period)
    balance = 0
    owned_stocks = {}
    df["Action"] = None

    for index, row in df.iterrows():
        current_price = row["Close"]
        momentum = row["Momentum"]

        if momentum > threshold:
            if symbol not in owned_stocks:
                placeBuyOrder(symbol, current_price)
                balance -= current_price
                owned_stocks[symbol] = current_price
                df.at[index, "Action"] = "BUY"
        elif momentum < -threshold:
            if symbol in owned_stocks:
                placeSellOrder(symbol, current_price)
                balance += current_price
                del owned_stocks[symbol]
                df.at[index, "Action"] = "SELL"

    plotStockPerformance(df, balance)


def plotStockPerformance(df, balance):
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["Close"], label="Stock Price")
    plt.scatter(
        df[df["Action"] == "BUY"].index,
        df[df["Action"] == "BUY"]["Close"],
        color="green",
        label="Buy",
        marker="^",
        s=100,
    )
    plt.scatter(
        df[df["Action"] == "SELL"].index,
        df[df["Action"] == "SELL"]["Close"],
        color="red",
        label="Sell",
        marker="v",
        s=100,
    )
    plt.xlabel("Date")
    plt.ylabel("Stock Price")
    plt.title("Stock Performance")
    plt.legend()

    # Plot profit/loss
    if balance != 0:
        plt.annotate(
            f"Profit/Loss: {balance:.2f}",
            (df.index[-1], df["Close"].iloc[-1]),
            xytext=(df.index[-1], df["Close"].iloc[-1] + 100),
            arrowprops=dict(facecolor="black", arrowstyle="->"),
        )

    plt.show()


backtest(symbol, momentum_period=2, threshold=0.02)
