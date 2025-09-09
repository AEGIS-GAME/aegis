import random
from typing import cast

import numpy as np
from numpy.typing import NDArray

from _aegis_game.args_parser import LaunchArgs
from _aegis_game.logger import LOGGER
from _aegis_game.team import Team
from _aegis_game.types.prediction import (
    CompletedPrediction,
    PendingPrediction,
)

from .data_loader import PredictionDataLoader

PendingPredictions = dict[tuple[Team, int], PendingPrediction]
CompletedPredictions = dict[tuple[Team, int], CompletedPrediction]


class PredictionHandler:
    def __init__(self, args: LaunchArgs) -> None:
        self._pending_predictions: PendingPredictions = {}
        self._completed_predictions: CompletedPredictions = {}
        self._data_loader: PredictionDataLoader = PredictionDataLoader(args)
        self._args: LaunchArgs = args

    def get_image_from_index(self, index: int) -> NDArray[np.uint8]:
        return cast("NDArray[np.uint8]", self._data_loader.x_test[index])

    def get_label_from_index(self, index: int) -> np.int32:
        return cast("np.int32", self._data_loader.y_test[index])

    def create_pending_prediction(self, team: Team, surv_id: int) -> None:
        """
        Create a pending prediction for a team-survivor combination.

        If one already exists, this method does nothing.
        """
        key: tuple[Team, int] = (team, surv_id)

        # Only create if no pending prediction exists
        if key not in self._pending_predictions:
            random_index = random.randint(0, len(self._data_loader.x_test) - 1)
            pending_prediction: PendingPrediction = {
                "image_to_predict": self.get_image_from_index(random_index),
                "correct_label": self.get_label_from_index(random_index),
            }
            self._pending_predictions[key] = pending_prediction

    def read_pending_predictions(
        self, team: Team
    ) -> list[tuple[int, NDArray[np.uint8], NDArray[np.int32]]]:
        """
        Agents call this to get all pending predictions for their team. Gives them the data of the pending prediction, without the correct label.

        Returns list of tuples: (surv_id, image_to_predict, all_unique_labels)
        """
        pending_list: list[tuple[int, NDArray[np.uint8], NDArray[np.int32]]] = []
        for (
            team_key,
            surv_id,
        ), pending_prediction in self._pending_predictions.items():
            if team_key == team:
                pending_list.append(
                    (
                        surv_id,
                        pending_prediction["image_to_predict"],
                        self._data_loader.unique_labels,
                    )
                )
        return pending_list

    def predict(self, team: Team, surv_id: int, prediction: np.int32) -> bool | None:
        """
        Process a prediction for a specific team-survivor combination.

        Returns:
            - bool: True if prediction was correct, False if incorrect
            - None: If no valid pending prediction exists (already predicted or never created)

        """
        key: tuple[Team, int] = (team, surv_id)

        # Check if there's a valid pending prediction
        if key not in self._pending_predictions:
            LOGGER.warning(
                f"Agent attempted to predict surv_id {surv_id} for team {team.name}, but no valid pending prediction exists. Did another agent on your team predict this survivor before you?"
            )
            return None

        pending_prediction = self._pending_predictions[key]
        is_correct: bool = pending_prediction["correct_label"] == prediction

        completed_prediction: CompletedPrediction = {
            "team": team,
            "surv_id": surv_id,
            "is_correct": is_correct,
        }

        self._completed_predictions[key] = completed_prediction
        del self._pending_predictions[key]

        return is_correct
