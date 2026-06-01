#!/usr/bin/env python3
"""
Confidence Calibration for AI Microscope Application
Calibrates model confidence scores for better reliability
"""

import numpy as np
from typing import List, Dict, Any, Optional
from scipy.optimize import minimize
from sklearn.isotonic import IsotonicRegression

from utils.logger import log_info, log_warning


class ConfidenceCalibrator:
    """Calibrates model confidence scores using temperature scaling."""
    
    def __init__(self, method: str = "temperature"):
        """Initialize confidence calibrator.
        
        Args:
            method: Calibration method ('temperature' or 'isotonic')
        """
        self.method = method
        self.temperature: Optional[float] = None
        self.isotonic_regressor: Optional[IsotonicRegression] = None
        self.is_fitted = False
    
    def _negative_log_likelihood(self, temp: float, logits: np.ndarray, labels: np.ndarray) -> float:
        """Calculate negative log-likelihood for temperature scaling.
        
        Args:
            temp: Temperature parameter
            logits: Model logits
            labels: True labels
            
        Returns:
            Negative log-likelihood
        """
        scaled_logits = logits / temp
        predictions = self._softmax(scaled_logits)
        nll = -np.sum(labels * np.log(predictions + 1e-10))
        return nll
    
    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        """Apply softmax to logits.
        
        Args:
            logits: Logits array
            
        Returns:
            Softmax probabilities
        """
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        return exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
    
    def fit(self, logits: np.ndarray, labels: np.ndarray) -> None:
        """Fit calibrator using validation data.
        
        Args:
            logits: Model logits from validation set
            labels: True labels (one-hot encoded)
        """
        if self.method == "temperature":
            log_info("Fitting temperature scaling calibrator")
            # Initialize temperature
            self.temperature = 1.0
            
            # Optimize temperature
            result = minimize(
                self._negative_log_likelihood,
                x0=np.array([1.0]),
                args=(logits, labels),
                bounds=[(0.01, 10.0)],
                method='L-BFGS-B'
            )
            
            self.temperature = result.x[0]
            log_info(f"Temperature scaling fitted: T={self.temperature:.4f}")
        
        elif self.method == "isotonic":
            log_info("Fitting isotonic regression calibrator")
            # Flatten for isotonic regression
            max_probs = np.max(self._softmax(logits), axis=1)
            correct_labels = np.argmax(labels, axis=1)
            
            self.isotonic_regressor = IsotonicRegression(out_of_bounds='clip')
            self.isotonic_regressor.fit(max_probs, correct_labels)
            log_info("Isotonic regression fitted")
        
        self.is_fitted = True
    
    def calibrate(self, logits: np.ndarray) -> np.ndarray:
        """Calibrate confidence scores.
        
        Args:
            logits: Model logits
            
        Returns:
            Calibrated probabilities
        """
        if not self.is_fitted:
            log_warning("Calibrator not fitted, returning uncalibrated probabilities")
            return self._softmax(logits)
        
        if self.method == "temperature":
            if self.temperature is None:
                return self._softmax(logits)
            scaled_logits = logits / self.temperature
            return self._softmax(scaled_logits)
        
        elif self.method == "isotonic":
            if self.isotonic_regressor is None:
                return self._softmax(logits)
            probs = self._softmax(logits)
            max_probs = np.max(probs, axis=1, keepdims=True)
            calibrated_max = self.isotonic_regressor.predict(max_probs.flatten())
            # Scale all probabilities proportionally
            calibrated = probs * (calibrated_max.reshape(-1, 1) / max_probs)
            return calibrated / np.sum(calibrated, axis=1, keepdims=True)
        
        return self._softmax(logits)
    
    def calibrate_single(self, confidence: float, class_index: int, num_classes: int) -> float:
        """Calibrate single confidence score.
        
        Args:
            confidence: Original confidence score
            class_index: Predicted class index
            num_classes: Total number of classes
            
        Returns:
            Calibrated confidence score
        """
        if not self.is_fitted:
            return confidence
        
        if self.method == "temperature" and self.temperature:
            # Simple approximation for single score
            return min(confidence ** (1.0 / self.temperature), 1.0)
        
        return confidence


class ExpectedCalibrationError:
    """Calculates Expected Calibration Error (ECE) for model evaluation."""
    
    def __init__(self, n_bins: int = 10):
        """Initialize ECE calculator.
        
        Args:
            n_bins: Number of bins for ECE calculation
        """
        self.n_bins = n_bins
    
    def calculate(self, confidences: np.ndarray, predictions: np.ndarray, labels: np.ndarray) -> float:
        """Calculate Expected Calibration Error.
        
        Args:
            confidences: Confidence scores
            predictions: Predicted class indices
            labels: True class indices
            
        Returns:
            ECE value
        """
        bin_boundaries = np.linspace(0, 1, self.n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        ece = 0.0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                accuracy_in_bin = predictions[in_bin] == labels[in_bin]
                avg_confidence_in_bin = confidences[in_bin].mean()
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin.mean()) * prop_in_bin
        
        return ece
    
    def get_calibration_curve(self, confidences: np.ndarray, predictions: np.ndarray, labels: np.ndarray) -> tuple:
        """Get calibration curve data.
        
        Args:
            confidences: Confidence scores
            predictions: Predicted class indices
            labels: True class indices
            
        Returns:
            Tuple of (bin_centers, accuracies, counts)
        """
        bin_boundaries = np.linspace(0, 1, self.n_bins + 1)
        bin_centers = (bin_boundaries[:-1] + bin_boundaries[1:]) / 2
        accuracies = []
        counts = []
        
        for i in range(self.n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            
            if in_bin.sum() > 0:
                accuracy = (predictions[in_bin] == labels[in_bin]).mean()
                accuracies.append(accuracy)
                counts.append(in_bin.sum())
            else:
                accuracies.append(0.0)
                counts.append(0)
        
        return bin_centers, np.array(accuracies), np.array(counts)
