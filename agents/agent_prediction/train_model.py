# pyright: reportUnknownMemberType=false
from pathlib import Path
from typing import TYPE_CHECKING, cast

import numpy as np
import tensorflow as tf

if TYPE_CHECKING:
    from numpy.typing import NDArray


def train_model() -> None:
    """Train and save a simple placeholder symbol prediction model."""
    # Load training data
    data_dir: Path = (
        Path(__file__).parent.parent.parent / "prediction_data" / "training"
    )
    x_train: NDArray[np.uint8] = cast(
        "NDArray[np.uint8]", np.load(data_dir / "x_train_symbols.npy")
    )
    y_train: NDArray[np.int32] = cast(
        "NDArray[np.int32]", np.load(data_dir / "y_train_symbols.npy")
    )
    print(type(x_train))
    print(type(y_train))
    print(x_train.shape)
    print(y_train.shape)
    print(x_train.dtype)
    print(y_train.dtype)

    # Normalize the data
    x_train_normalized: NDArray[np.float32] = x_train.astype(np.float32) / 255.0

    # Convert labels to categorical
    num_classes: int = len(np.unique(y_train))
    y_train_categorical: NDArray[np.float32] = tf.keras.utils.to_categorical(
        y_train, num_classes
    )

    # Create model
    model: tf.keras.Sequential = tf.keras.Sequential(
        [
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(num_classes, activation="softmax"),
        ]
    )

    # Compile model
    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )

    # Train model
    model.fit(
        x_train_normalized,
        y_train_categorical,
        epochs=10,
        batch_size=32,
        validation_split=0.2,
    )

    # Save model
    model.save("trained_net.keras")


if __name__ == "__main__":
    train_model()
