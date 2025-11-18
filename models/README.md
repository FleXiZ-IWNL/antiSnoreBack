# TensorFlow Models Directory

Place your trained TensorFlow models in this directory.

## Expected Model File

- `snoring_detector.h5` - Main snoring detection model

## Model Requirements

The model should:
- Accept audio features (mel spectrograms) as input
- Output a binary classification (snoring vs non-snoring)
- Input shape: (None, 128, 128, 1)
- Output: Single probability value [0-1]

## Training Your Own Model

If you don't have a pre-trained model, you can:

1. Collect snoring audio samples
2. Extract mel spectrogram features
3. Train a CNN classifier using TensorFlow/Keras
4. Save the model as `snoring_detector.h5`

## Mock Mode

If no model is found, the backend will operate in "mock mode" with random predictions for testing purposes.

