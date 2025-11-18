import numpy as np
import os
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

# Try to import TensorFlow
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow not available. Using mock predictions.")

# Try to import audio processing libraries
try:
    import librosa
    import soundfile as sf
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logger.warning("Audio libraries (librosa, soundfile) not available.")


class SnoringDetector:
    """Snoring detection model wrapper"""
    
    def __init__(self, model_path: str = "models/snoring_detector.h5"):
        self.model_path = model_path
        self.model = None
        self.is_mock = False
        
        self._load_model()
    
    def _load_model(self):
        """Load the TensorFlow model"""
        if not TENSORFLOW_AVAILABLE:
            logger.warning("TensorFlow not available. Using mock model.")
            self.is_mock = True
            return
        
        if os.path.exists(self.model_path):
            try:
                self.model = tf.keras.models.load_model(self.model_path)
                logger.info(f"Model loaded successfully from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                logger.warning("Using mock model instead.")
                self.is_mock = True
        else:
            logger.warning(f"Model file not found at {self.model_path}. Using mock model.")
            self.is_mock = True
    
    def preprocess_audio(self, audio_data: bytes) -> np.ndarray:
        """
        Preprocess audio data for model input
        
        Args:
            audio_data: Raw audio bytes (WAV format)
        
        Returns:
            Preprocessed numpy array
        """
        if not AUDIO_LIBS_AVAILABLE:
            # Mock preprocessing
            return np.random.randn(1, 128, 128, 1)
        
        try:
            # Load audio from bytes
            import io
            audio_io = io.BytesIO(audio_data)
            y, sr = sf.read(audio_io)
            
            # Extract mel spectrogram features
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Normalize
            mel_spec_db = (mel_spec_db - mel_spec_db.mean()) / mel_spec_db.std()
            
            # Reshape for model input (batch_size, height, width, channels)
            # Assuming model expects (None, 128, 128, 1)
            if mel_spec_db.shape[1] < 128:
                # Pad if too short
                pad_width = 128 - mel_spec_db.shape[1]
                mel_spec_db = np.pad(mel_spec_db, ((0, 0), (0, pad_width)), mode='constant')
            else:
                # Crop if too long
                mel_spec_db = mel_spec_db[:, :128]
            
            # Add batch and channel dimensions
            mel_spec_db = mel_spec_db.reshape(1, 128, 128, 1)
            
            return mel_spec_db
        
        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}")
            # Return mock data on error
            return np.random.randn(1, 128, 128, 1)
    
    def predict(self, audio_data: bytes) -> Tuple[bool, float]:
        """
        Predict if audio contains snoring
        
        Args:
            audio_data: Raw audio bytes
        
        Returns:
            Tuple of (is_snoring, confidence)
        """
        if self.is_mock or self.model is None:
            # Mock prediction for testing
            # Generate random prediction with bias towards detecting snoring sometimes
            confidence = np.random.uniform(0.3, 0.95)
            is_snoring = confidence > 0.6
            logger.info(f"Mock prediction: snoring={is_snoring}, confidence={confidence:.2f}")
            return is_snoring, float(confidence)
        
        try:
            # Preprocess audio
            processed_audio = self.preprocess_audio(audio_data)
            
            # Make prediction
            prediction = self.model.predict(processed_audio, verbose=0)
            
            # Extract confidence (assuming binary classification)
            confidence = float(prediction[0][0])
            is_snoring = confidence > 0.5
            
            logger.info(f"Model prediction: snoring={is_snoring}, confidence={confidence:.2f}")
            
            return is_snoring, confidence
        
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            # Return safe default on error
            return False, 0.0
    
    def predict_from_file(self, audio_path: str) -> Tuple[bool, float]:
        """
        Predict from audio file path
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Tuple of (is_snoring, confidence)
        """
        try:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            return self.predict(audio_data)
        except Exception as e:
            logger.error(f"Error reading audio file: {e}")
            return False, 0.0


# Global model instance
_detector_instance = None


def get_detector() -> SnoringDetector:
    """Get or create the global detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = SnoringDetector()
    return _detector_instance

