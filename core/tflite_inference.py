#!/usr/bin/env python3
"""
TFLite Inference for AI Microscope Application
Supports quantized models for edge deployment
"""

import numpy as np
from typing import Dict, Any, Optional
import tensorflow as tf

from utils.logger import log_info, log_error


class TFLiteInferenceEngine:
    """TFLite inference engine for quantized models."""
    
    def __init__(self, model_path: str):
        """Initialize TFLite inference engine.
        
        Args:
            model_path: Path to TFLite model file
        """
        self.model_path = model_path
        self.interpreter: Optional[tf.lite.Interpreter] = None
        self.input_details: Optional[list] = None
        self.output_details: Optional[list] = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load TFLite model."""
        try:
            self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            log_info(f"TFLite model loaded: {self.model_path}")
        except Exception as e:
            log_error(f"Failed to load TFLite model: {str(e)}")
            raise
    
    def predict(self, image: np.ndarray) -> Dict[str, Any]:
        """Run inference on image.
        
        Args:
            image: Preprocessed image array
            
        Returns:
            Dictionary with prediction results
        """
        if self.interpreter is None:
            raise RuntimeError("Model not loaded")
        
        # Set input tensor
        input_index = self.input_details[0]['index']
        self.interpreter.set_tensor(input_index, image)
        
        # Run inference
        self.interpreter.invoke()
        
        # Get output
        output_index = self.output_details[0]['index']
        predictions = self.interpreter.get_tensor(output_index)
        
        # Process predictions
        top_class = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][top_class])
        
        return {
            "prediction": top_class,
            "confidence": confidence,
            "probabilities": predictions[0].tolist()
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information.
        
        Returns:
            Dictionary with model details
        """
        if self.interpreter is None:
            return {}
        
        return {
            "input_shape": self.input_details[0]['shape'],
            "input_type": self.input_details[0]['dtype'],
            "output_shape": self.output_details[0]['shape'],
            "output_type": self.output_details[0]['dtype']
        }
