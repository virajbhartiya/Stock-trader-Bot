import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
import time

symbol = "SBIN.NS"


def placeBuyOrder(symbol, price):
    print("BUY:", symbol, "at", str(price))
    # Place buy order logic


def placeSellOrder(symbol, price):
    print("SELL:", symbol, "at", str(price))
    # Place sell order logic


def trainModel(symbol):
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
        return None, None, None

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

    return model, scaler


def makeDummyTrades(symbol):
    model, scaler = trainModel(symbol)

    # Fetch historical data
    history = yf.download(symbol, period="7d", interval="1m")
    history["Close"] = history["Close"].astype(float)  # Convert Close column to float
    balance = 5000
    stockOwned = 0
    while True:
        try:
            # Fetch the current price
            current_price = yf.Ticker(symbol).history(period="1d")["Close"][-1]

            # Prepare data for prediction
            last_100_prices = history["Close"].iloc[-100:].values
            scaled_prices = scaler.transform(last_100_prices.reshape(-1, 1))
            X = np.reshape(scaled_prices, (1, 100, 1))

            # Make a prediction based on the current price
            prediction = model.predict(X)
            predicted_price = scaler.inverse_transform(prediction)[0][0]
            print("Current Price:", current_price, "Predicted Price:", predicted_price)
            # Execute the trade based on the prediction and current price
            if current_price < predicted_price:
                stockQty = int(balance // current_price)
                if balance > stockQty * current_price:
                    balance -= stockQty * current_price
                    stockOwned += stockQty
                    for i in range(stockQty):
                        placeBuyOrder(symbol, current_price)
            elif current_price > predicted_price and stockOwned > 0:
                balance += stockOwned * current_price
                stockOwned = 0
                for i in range(stockOwned):
                    placeSellOrder(symbol, current_price)

        except Exception as e:
            print("Error occurred:", str(e))
        print("Balance:", balance, "Stock Owned:", stockOwned)
        # Sleep for 1 minute
        time.sleep(60)


makeDummyTrades(symbol)
