import tensorflow as tf
from tensorflow import keras
from keras_tuner.tuners import Hyperband
from lstm_utils import fetch_sales_data, preprocess

def build_model(hp):
    model = keras.Sequential([
        keras.layers.LSTM(
            hp.Int('units', min_value=32, max_value=128, step=32),
            input_shape=(5, 8)  # window_size=5, num features=8
        ),
        keras.layers.Dense(1)
    ])
    model.compile(
        optimizer=keras.optimizers.Adam(
            hp.Choice('learning_rate', [1e-2, 1e-3, 1e-4])
        ),
        loss='mse'
    )
    return model

if __name__ == "__main__":
    df = fetch_sales_data(2021, 2024)
    X, y, _ = preprocess(df, window_size=5)

    tuner = Hyperband(
        build_model,
        objective='val_loss',
        max_epochs=10,
        factor=3,
        directory='hyperband_dir',
        project_name='base_lstm'
    )

    tuner.search(X, y, epochs=10, validation_split=0.2)
    best_model = tuner.get_best_models(num_models=1)[0]
    best_model.save('base_lstm_model.h5')
    print("✅ Base LSTM model saved as base_lstm_model.h5")
