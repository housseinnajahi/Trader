import os
from datetime import datetime

import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Model
from typing import Tuple


def create_lstm_model(input_shape: Tuple[int, int]) -> Model:
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


def prepare_data(df: np.ndarray, window_size: int = 60) -> Tuple[np.ndarray, np.ndarray, MinMaxScaler]:
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df)

    x, y = [], []
    for i in range(window_size, len(scaled_data)):
        x.append(scaled_data[i - window_size:i, 0])
        y.append(scaled_data[i, 0])
    x, y = np.array(x), np.array(y)
    x = np.reshape(x, (x.shape[0], x.shape[1], 1))
    return x, y, scaler


def predict_prices(model: Model, data: np.ndarray, scaler: MinMaxScaler, number_of_predictions: int = 96) -> np.ndarray:
    predictions = []
    current_batch = data[-60:]
    for _ in range(number_of_predictions):
        current_pred = model.predict(current_batch[np.newaxis, :, :])[0]
        current_pred = current_pred.reshape(-1, 1)  # Ensure the prediction has the correct shape
        predictions.append(current_pred[0])
        current_batch = np.append(current_batch[1:], current_pred, axis=0)
    predictions = np.array(predictions)
    if predictions.size == 0:
        raise ValueError("Predictions array is empty. Check your input data and model.")
    return scaler.inverse_transform(predictions)


def generate_prediction(data: dict):
    result = {
        "close_price": [],
        "highest_price": [],
        "lowest_price": [],
    }
    dataframe = pd.read_csv(f"{os.getenv('AGGREGATION_FOLDER')}/{data['file_name']}")
    open_prices = [dataframe["open_price"][0]]
    dataframe = dataframe.iloc[::-1]
    dataframe.reset_index(drop=True, inplace=True)
    for key in result:
        prices = dataframe[key].values.reshape(-1, 1)
        x, y, scaler = prepare_data(prices)
        model = create_lstm_model((x.shape[1], 1))
        model.fit(x, y, batch_size=1, epochs=1)
        predictions = predict_prices(model, prices, scaler)
        prices = [price[0] for price in predictions.tolist()]
        result[key] = prices
        if key == "close_price":
            open_prices.extend(prices[:-1])
    result.update({"open_price": open_prices})
    df = pd.DataFrame.from_dict(result)
    date = datetime.today().strftime('%Y-%m-%d')
    csv_file_path = f"{os.getenv('AGGREGATION_FOLDER')}/predictions_of_{data['ticker']}_for_{date}_{data['file_name']}"
    print(f"Prediction file is generated successfully of {data['ticker']} for {date}")
    df.to_csv(csv_file_path, index=False)
