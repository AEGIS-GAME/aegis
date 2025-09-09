# Prediction Data Structure

This directory contains the prediction data for the AEGIS symbol prediction system.

## Directory Structure

```
prediction_data/
├── training/          # Training data (provided by course website/comp website)
│   ├── x_train_symbols.npy
│   └── y_train_symbols.npy
└── testing/           # Testing data (provided by course website/comp website)
    ├── x_test_symbols.npy
    └── y_test_symbols.npy
```

## Data Format

Each directory contains:

- `x_test_symbols.npy` or `x_train_symbols.npy`: Image data as numpy arrays
- `y_test_symbols.npy` or `y_train_symbols.npy`: Label data as numpy arrays

## Setup Instructions

1. **Testing Data**: Place testing data in the `testing/` directory
2. **Training Data**: Place training data in the `training/` directory

## Notes

- The `training/` directory is for model development and is not used during normal AEGIS simulations
- All data files must follow the naming convention: `x_{type}_symbols.npy` and `y_{type}_symbols.npy`
