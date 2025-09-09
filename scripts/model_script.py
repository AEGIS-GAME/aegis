import os
import sys

from src.agents.better_agent.model import Model

sys.path.insert(0, os.getcwd())
import random

import numpy as np

curr_dir = os.path.dirname(os.path.realpath(__file__))
os.environ["PYTHONPATH"] = os.path.join(curr_dir, "src")


def main():
    random.seed(12345)
    np.random.seed(12345)

    model = Model()
    trained_model = model.get_model()  # load and train a model

    _, _, x_test, y_test = model._load_data()

    num_samples_to_test = 10
    correct_predictions = 0

    for _ in range(num_samples_to_test):
        index = random.randint(0, len(x_test) - 1)

        image = x_test[index]
        label = y_test[index]
        image = np.expand_dims(image, axis=0)

        print(f"Image shape: {image.shape}")
        print(f"Image dtype: {image.dtype}")

        predictions = trained_model.predict(image, verbose=0)
        predicted_label = np.argmax(predictions[0])

        is_correct = label == predicted_label
        correct_predictions += is_correct

        print(
            f"True Label: {label}, Predicted Label: {predicted_label}, Correct: {is_correct}"
        )

        # plt.imshow(x_test[index], cmap="gray")
        # plt.title(f"Label: {y_test[index]}")
        # plt.show()

    accuracy = correct_predictions / num_samples_to_test
    print(f"Accuracy for {num_samples_to_test} samples: {accuracy * 100:.2f}%")


if __name__ == "__main__":
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    os.environ["PYTHONPATH"] = os.path.join(curr_dir, "src")
    main()
