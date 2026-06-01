#!/usr/bin/env python3
"""
Device Manager for AI Microscope Application
Handles GPU/CPU device selection with automatic fallback
"""

import os
from typing import Optional, List

import tensorflow as tf

from utils.logger import log_info, log_error, log_warning


class DeviceManager:
    """Manages computation device (GPU/CPU) with fallback."""
    
    def __init__(self):
        """Initialize device manager."""
        self.gpu_available = self._check_gpu_available()
        self.current_device = self._select_device()
    
    def _check_gpu_available(self) -> bool:
        """Check if GPU is available.
        
        Returns:
            True if GPU available, False otherwise
        """
        try:
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                # Configure GPU memory growth to avoid allocation issues
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                log_info(f"GPU detected: {len(gpus)} device(s)")
                return True
            else:
                log_info("No GPU detected, will use CPU")
                return False
        except Exception as e:
            log_warning(f"GPU detection failed: {str(e)}")
            return False
    
    def _select_device(self) -> str:
        """Select appropriate computation device.
        
        Returns:
            Device name ('GPU' or 'CPU')
        """
        if self.gpu_available:
            log_info("Using GPU for inference")
            return "GPU"
        else:
            log_info("Using CPU for inference")
            return "CPU"
    
    def get_device(self) -> str:
        """Get current device.
        
        Returns:
            Device name
        """
        return self.current_device
    
    def force_cpu(self) -> None:
        """Force CPU usage regardless of GPU availability."""
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        self.current_device = "CPU"
        log_info("Forced CPU mode")
    
    def get_device_info(self) -> dict:
        """Get device information.
        
        Returns:
            Dictionary with device details
        """
        info = {
            "current_device": self.current_device,
            "gpu_available": self.gpu_available
        }
        
        if self.gpu_available:
            gpus = tf.config.list_physical_devices('GPU')
            info["gpu_count"] = len(gpus)
            info["gpu_names"] = [gpu.name for gpu in gpus]
        
        return info
    
    def configure_for_inference(self) -> None:
        """Configure TensorFlow for optimal inference performance."""
        # Suppress TensorFlow warnings
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        
        # Set thread pool size for CPU
        if not self.gpu_available:
            tf.config.threading.set_intra_op_parallelism_threads(4)
            tf.config.threading.set_inter_op_parallelism_threads(4)
            log_info("Configured CPU thread pool for optimal performance")
