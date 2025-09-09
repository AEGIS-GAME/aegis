from pathlib import Path
from typing import TYPE_CHECKING, cast

import numpy as np

from _aegis_game.args_parser import LaunchArgs

if TYPE_CHECKING:
    from numpy.typing import NDArray


class PredictionDataLoader:
    """Handles loading prediction data from external directories."""

    def __init__(self, args: LaunchArgs) -> None:
        """
        Initialize the data loader.

        Args:
            args: The arguments object

        """
        self.args: LaunchArgs = args
        self.x_test: NDArray[np.uint8] = np.array([])
        self.y_test: NDArray[np.int32] = np.array([])
        self.unique_labels: NDArray[np.int32] = np.array([])
        self.load_testing_data()

    def load_testing_data(self) -> None:
        """Load testing data from the testing directory."""
        data_dir = Path.cwd() / "prediction_data" / "testing"

        x_path = data_dir / "x_test_symbols.npy"
        y_path = data_dir / "y_test_symbols.npy"

        if not x_path.exists() or not y_path.exists():
            msg = (
                f"Prediction data not found in {data_dir}. "
                f"Expected files: x_test_symbols.npy, y_test_symbols.npy"
            )
            raise FileNotFoundError(msg)

        self.x_test = cast("NDArray[np.uint8]", np.load(x_path))
        self.y_test = cast("NDArray[np.int32]", np.load(y_path))
        self.unique_labels = np.unique(self.y_test)

    @property
    def num_testing_images(self) -> int:
        """Get the number of testing images available."""
        return len(self.x_test)
