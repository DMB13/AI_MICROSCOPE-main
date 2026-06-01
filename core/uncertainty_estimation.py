#!/usr/bin/env python3
"""
Uncertainty Estimation for AI Microscope Application
Implements Monte Carlo Dropout for uncertainty quantification
"""

import numpy as np
from typing import Dict, Any, List, Optional
import tensorflow as tf

from utils.logger import log_info, log_warning


class UncertaintyEstimator:
    """Estimates prediction uncertainty using Monte Carlo Dropout."""
    
    def __init__(self, model, n_samples: int = 30):
        """Initialize uncertainty estimator.
        
        Args:
            model: TensorFlow model with dropout layers
            n_samples: Number of Monte Carlo samples
        """
        self.model = model
        self.n_samples = n_samples
        log_info(f"Uncertainty estimator initialized with {n_samples} MC samples")
    
    def enable_mc_dropout(self) -> None:
        """Enable dropout during inference for MC sampling."""
        for layer in self.model.layers:
            if hasattr(layer, 'training'):
                layer.training = True
    
    def disable_mc_dropout(self) -> None:
        """Disable dropout after MC sampling."""
        for layer in self.model.layers:
            if hasattr(layer, 'training'):
                layer.training = False
    
    def predict_with_uncertainty(self, image: np.ndarray) -> Dict[str, Any]:
        """Predict with uncertainty estimation.
        
        Args:
            image: Input image array
            
        Returns:
            Dictionary with predictions and uncertainty metrics
        """
        self.enable_mc_dropout()
        
        # Run multiple forward passes with dropout
        predictions = []
        for _ in range(self.n_samples):
            pred = self.model.predict(image, verbose=0)
            predictions.append(pred)
        
        self.disable_mc_dropout()
        
        predictions = np.array(predictions)
        
        # Calculate statistics
        mean_pred = np.mean(predictions, axis=0)
        std_pred = np.std(predictions, axis=0)
        
        # Get top prediction
        top_class = np.argmax(mean_pred[0])
        confidence = mean_pred[0][top_class]
        uncertainty = std_pred[0][top_class]
        
        # Calculate predictive entropy
        entropy = -np.sum(mean_pred[0] * np.log(mean_pred[0] + 1e-10))
        
        # Calculate mutual information
        mutual_info = entropy - np.mean([
            -np.sum(pred[0] * np.log(pred[0] + 1e-10))
            for pred in predictions
        ])
        
        return {
            "prediction": top_class,
            "confidence": float(confidence),
            "uncertainty": float(uncertainty),
            "entropy": float(entropy),
            "mutual_information": float(mutual_info),
            "mean_predictions": mean_pred[0],
            "std_predictions": std_pred[0]
        }
    
    def is_prediction_reliable(self, uncertainty: float, threshold: float = 0.1) -> bool:
        """Check if prediction is reliable based on uncertainty.
        
        Args:
            uncertainty: Uncertainty score
            threshold: Uncertainty threshold
            
        Returns:
            True if reliable, False otherwise
        """
        return uncertainty < threshold
