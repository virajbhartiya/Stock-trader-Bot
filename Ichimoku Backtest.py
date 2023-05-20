import yfinance as yf
import matplotlib.pyplot as plt

symbol = "TCS.NS"


def getIchimokuCloud(history):
    conversion_line = (
        history["High"].rolling(9).max() + history["Low"].rolling(9).min()
    ) / 2
    base_line = (
        history["High"].rolling(26).max() + history["Low"].rolling(26).min()
    ) / 2
    lead_span_A = (conversion_line + base_line) / 2
    lead_span_B = (
        history["High"].rolling(52).max() + history["Low"].rolling(52).min()
    ) / 2
    lagging_span = history["Close"].shift(-26)  # Shifted 26 periods back

    return conversion_line, base_line, lead_span_A, lead_span_B, lagging_span


def placeBuyOrder(symbol, price):
    print("BUY:", symbol, "at", str(price))
    # Place buy order logic


def placeSellOrder(symbol, price):
    print("SELL:", symbol, "at", str(price))
    # Place sell order logic


def backtest(symbol):
    df = yf.download(symbol, period="1w", interval="15m")
    (
        df["Conversion_Line"],
        df["Base_Line"],
        df["Lead_Span_A"],
        df["Lead_Span_B"],
        df["Lagging_Span"],
    ) = getIchimokuCloud(df)
    balance = 0
    owned_stocks = {}
    df["Action"] = None

    for index, row in df.iterrows():
        current_price = row["Close"]
        if (
            (current_price > row["Conversion_Line"])
            and (current_price > row["Base_Line"])
            and (row["Conversion_Line"] > row["Base_Line"])
            and (current_price > row["Lead_Span_A"])
            and (current_price > row["Lead_Span_B"])
            and (row["Lagging_Span"] > current_price)
        ):
            if symbol not in owned_stocks:
                placeBuyOrder(symbol, current_price)
                balance -= current_price
                owned_stocks[symbol] = current_price
                df.at[index, "Action"] = "BUY"
        elif (
            (current_price < row["Conversion_Line"])
            and (current_price < row["Base_Line"])
            and (row["Conversion_Line"] < row["Base_Line"])
            and (current_price < row["Lead_Span_A"])
            and (current_price < row["Lead_Span_B"])
            and (row["Lagging_Span"] < current_price)
        ):
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


backtest(symbol)
