from typing import TypedDict

import numpy as np
from numpy.typing import NDArray

from _aegis_game.team import Team


# Type for pending predictions
class PendingPrediction(TypedDict):
    image_to_predict: NDArray[np.uint8]
    correct_label: np.int32


# Type for completed predictions
class CompletedPrediction(TypedDict):
    team: Team
    surv_id: int
    is_correct: bool
