import re
from pathlib import Path
from typing import TYPE_CHECKING, cast

import numpy as np

from _aegis_game.args_parser import LaunchArgs

if TYPE_CHECKING:
    from numpy.typing import NDArray


class PredictionDataLoader:
    """Handles loading prediction data from external directories."""

    IMAGE_SHAPE = (28, 28)
    IMAGE_DIMENSIONS = 3

    def __init__(self, args: LaunchArgs) -> None:
        """
        Initialize the data loader.

        Args:
            args: The arguments object

        """
        self.args: LaunchArgs = args
        self.x_test: NDArray[np.uint8] = np.array([], dtype=np.uint8)
        self.y_test: NDArray[np.int32] = np.array([], dtype=np.int32)
        self.unique_labels: NDArray[np.int32] = np.array([], dtype=np.int32)
        self.load_testing_data()

    def load_testing_data(self) -> None:
        """Load the testing data for the selected prediction dataset."""
        dataset_name = self.args.prediction_data

        if re.fullmatch(r"[A-Za-z0-9_-]+", dataset_name) is None:
            msg = f"Invalid prediction dataset name: {dataset_name}"
            raise ValueError(msg)

        data_dir = Path.cwd() / "prediction_data"
        x_path = data_dir / f"x_test_{dataset_name}.npy"
        y_path = data_dir / f"y_test_{dataset_name}.npy"

        if not x_path.exists() or not y_path.exists():
            msg = (
                f"Prediction dataset '{dataset_name}' not found. "
                f"Expected files: {x_path.name}, {y_path.name}"
            )
            raise FileNotFoundError(msg)

        self.x_test = cast("NDArray[np.uint8]", np.load(x_path, allow_pickle=False))
        self.y_test = cast("NDArray[np.int32]", np.load(y_path, allow_pickle=False))

        self._validate_testing_data(dataset_name)
        self.unique_labels = np.unique(self.y_test)

    def _validate_testing_data(self, dataset_name: str) -> None:
        if (
            self.x_test.ndim != self.IMAGE_DIMENSIONS
            or self.x_test.shape[1:] != self.IMAGE_SHAPE
        ):
            msg = f"Dataset '{dataset_name}' images must have shape (N, 28, 28)"
            raise ValueError(msg)

        if self.y_test.ndim != 1:
            msg = f"Dataset '{dataset_name}' labels must have shape (N,)"
            raise ValueError(msg)

        if len(self.x_test) == 0:
            msg = f"Dataset '{dataset_name}' must not be empty"
            raise ValueError(msg)

        if len(self.x_test) != len(self.y_test):
            msg = f"Dataset '{dataset_name}' image and label counts do not match"
            raise ValueError(msg)

        if self.x_test.dtype != np.uint8:
            msg = f"Dataset '{dataset_name}' images must use dtype uint8"
            raise ValueError(msg)

        if not np.issubdtype(self.y_test.dtype, np.integer):
            msg = f"Dataset '{dataset_name}' labels must use an integer dtype"
            raise ValueError(msg)

    @property
    def num_testing_images(self) -> int:
        """Get the number of testing images available."""
        return len(self.x_test)
