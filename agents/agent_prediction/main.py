from pathlib import Path
from typing import TYPE_CHECKING, cast

import numpy as np
import tensorflow as tf

from aegis_game.stub import *

if TYPE_CHECKING:
    from numpy.typing import NDArray


def think() -> None:
    """Do not remove this function, it must always be defined."""
    log("Thinking")

    # On the first round, send a request for surrounding information
    # by moving to the center (not moving). This will help initiate pathfinding.
    if get_round_number() == 1:
        move(Direction.CENTER)
        return

    # Fetch the cell at the agent's current location.
    # If you want to check a different location, use `on_map(loc)` first
    # to ensure it's within the world bounds. The agent's own location is always valid.
    cell: CellInfo = get_cell_info_at(get_location())

    # If there is a pending prediction from a save survivor for our team, predict!
    prediction_info = read_pending_predictions()
    if prediction_info:
        # grab just the first pending prediction
        surv_saved_id, image_to_predict, _ = prediction_info[0]

        # Get the path to the model file in the agent's directory
        model_path = Path("agents/agent_prediction/trained_net.keras")
        if not model_path.exists():
            log("Model not found, skipping prediction")
            return

        # Load the model and make prediction like in the example
        model = tf.keras.models.load_model(str(model_path))
        # Reshape the image for the model (similar to the example)
        image = np.reshape(image_to_predict, (28, 28))
        image = np.reshape(image, (1, 28, 28))

        # Make prediction
        predictions = model(image)
        predicted_label = cast(np.int32, np.argmax(predictions[0]))
        confidence = float(np.max(predictions[0]))

        log(f"Predicted symbol: {predicted_label} with confidence: {confidence:.4f}")

        # Send the prediction using the survivor ID from the save result
        predict(surv_saved_id, predicted_label)
    else:
        log("No pending predictions")

    # Get the top layer at the agent's current location.
    # If a survivor is present, save it and make a prediction.
    if isinstance(cell.top_layer, Survivor):
        # Save the survivor
        save()

        # After saving, we'll get a SaveResult with the image to predict
        # The prediction will be handled in the handle_save function
        return

    # Default action: Move the agent north if no other specific conditions are met.
    move(Direction.NORTH)
