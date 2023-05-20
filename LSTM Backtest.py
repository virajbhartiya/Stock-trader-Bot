import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
import matplotlib.pyplot as plt

symbol = "SBIN.NS"


def placeBuyOrder(symbol, price):
    print("BUY:", symbol, "at", str(price))
    # Place buy order logic


def placeSellOrder(symbol, price):
    print("SELL:", symbol, "at", str(price))
    # Place sell order logic


def backtest(symbol):
    df = yf.download(symbol, period="7d", interval="1m")
    df["Close"] = df["Close"].astype(float)  # Convert Close column to float
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df["Close"].values.reshape(-1, 1))

    # Prepare training data
    window_size = 100  # Number of previous data points to consider
    X = []
    y = []
    for i in range(window_size, len(df)):
        X.append(scaled_data[i - window_size : i, 0])
        y.append(scaled_data[i, 0])
    X, y = np.array(X), np.array(y)

    # Check if X has sufficient data points
    if X.shape[0] < 1:
        print("Insufficient data points for LSTM")
        return

    # Reshape input data for LSTM (number of samples, number of timesteps, number of features)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))

    # Create the LSTM model
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(LSTM(units=50))
    model.add(Dense(units=1))
    model.compile(optimizer="adam", loss="mean_squared_error")

    # Train the LSTM model
    model.fit(X, y, epochs=10, batch_size=32)

    # Generate predictions
    predictions = model.predict(X)
    predictions = scaler.inverse_transform(predictions)

    # Add predictions to the dataframe
    df["Prediction"] = np.nan
    df.iloc[window_size : len(df), df.columns.get_loc("Prediction")] = predictions[:, 0]

    # Perform backtesting
    balance = 5000
    owned_stocks = {}
    df["Action"] = None
    finalCurrnetPrice = 0
    numStock = 0
    for index, row in df.iterrows():
        current_price = row["Close"]
        prediction_price = row["Prediction"]
        print("Balance: ", balance)
        if current_price < prediction_price:
            if balance > current_price:
                num_shares = int(
                    balance // current_price
                )  # Calculate the number of whole shares
                total_cost = (
                    num_shares * current_price
                )  # Calculate the total cost of buying whole shares
                placeBuyOrder(symbol, total_cost)  # Place the buy order
                owned_stocks[symbol] = num_shares
                balance -= total_cost
                numStock += num_shares
                df.at[index, "Action"] = "BUY"
        elif current_price > prediction_price:
            if symbol in owned_stocks:
                num_shares = owned_stocks[symbol]
                total_sell_price = (
                    num_shares * current_price
                )  # Calculate the total sell price of selling whole shares
                numStock -= num_shares
                placeSellOrder(symbol, total_sell_price)  # Place the sell order
                balance += total_sell_price
                del owned_stocks[symbol]
                df.at[index, "Action"] = "SELL"
        finalCurrnetPrice = current_price * numStock
    balance += finalCurrnetPrice
    print("Final Balance: ", balance)
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
    plt.plot(df.index, df["Prediction"], color="blue", label="Prediction")
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
