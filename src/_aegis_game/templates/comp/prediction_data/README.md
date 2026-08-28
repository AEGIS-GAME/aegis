# Prediction Data Structure

This directory contains the prediction data for the AEGIS symbol prediction system.

## Directory Structure

```
prediction_data/
├── x_train_symbols.npy   # Training images (provided by course/comp website)
├── y_train_symbols.npy   # Training labels
├── x_test_symbols.npy    # Testing images (provided by course/comp website)
└── y_test_symbols.npy    # Testing labels
```

## Data Format

- `x_test_<dataset>.npy` / `x_train_<dataset>.npy`: image data as numpy arrays,
  shaped `(N, 28, 28)` with dtype `uint8`
- `y_test_<dataset>.npy` / `y_train_<dataset>.npy`: label data as numpy arrays,
  shaped `(N,)` with an integer dtype

## Selecting a Dataset

Files are named by dataset rather than split into directories, so several
datasets can sit side by side. Pick one at launch:

```bash
aegis launch --world example --agent agent_prediction --prediction-data symbols
```

`--prediction-data` defaults to `symbols`, which loads `x_test_symbols.npy` and
`y_test_symbols.npy`. A dataset named `demo` would load `x_test_demo.npy` and
`y_test_demo.npy`. Dataset names may only contain letters, digits, underscores
and hyphens.

## Setup Instructions

1. **Testing Data**: place `x_test_<dataset>.npy` and `y_test_<dataset>.npy` here
2. **Training Data**: place `x_train_<dataset>.npy` and `y_train_<dataset>.npy` here

## Notes

- Training files are for model development and are not used during normal AEGIS
  simulations
- All data files must follow the naming convention `x_{type}_{dataset}.npy` and
  `y_{type}_{dataset}.npy`
- Testing data is validated on load; a dataset with the wrong shape, dtype, or
  mismatched image and label counts is rejected with an error
