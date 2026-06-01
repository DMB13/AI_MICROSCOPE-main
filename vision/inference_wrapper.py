                                        #!/usr/bin/env python3
"""
Inference Wrapper for AI Microscope Application
Wraps the inference module for use by the application layer
"""

from typing import Dict, Any, Optional
from pathlib import Path
from PIL import Image
import numpy as np
import tensorflow as tf

from utils.logger import log_info, log_error
from config.constants import MODEL_PATH, IMG_SIZE
from core.device_manager import DeviceManager


class InferenceWrapper:
    """Wrapper for AI model inference operations."""
 
    def __init__(self):
        """Initialize inference wrapper and load model."""
        self.model = None
        self.model_name = None
        self.img_size = IMG_SIZE
        
        # Initialize device manager for GPU/CPU selection
        self.device_manager = DeviceManager()
        self.device_manager.configure_for_inference()
        
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the AI model."""
        try:
            import inference as inference_module
            self.model = inference_module.load_model()
            log_info(f"Model loaded: {self.model.name}")
        except Exception as e:
            log_error(f"Failed to load model: {str(e)}")
            raise
    
    def get_model(self):
        """Get the loaded model."""
        return self.model
    
    def run_inference(self, image_path: str) -> Dict[str, Any]:
        """Run inference on an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with inference results
        """
        try:
            if self.model is None:
                log_error("Model not loaded")
                return self._error_result("Model not loaded")
            
            import inference as inference_module
            result = inference_module.predict(image_path, self.model)
            
            log_info(f"Inference completed: {result.get('species', 'Unknown')}")
            return result
            
        except Exception as e:
            log_error(f"Inference failed: {str(e)}", exc_info=True)
            return {
                "species": "Error",
                "confidence": 0.0,
                "class_index": -1,
                "all_predictions": [],
                "error": str(e)
            }
    def generate_gradcam(self, image_path: str, class_index: int) -> Optional[str]:
        """Generate Grad-CAM heatmap for an image.
        
        Args:
            image_path: Path to image file
            class_index: Class index to visualize
            
        Returns:
            Path to generated heatmap or None if failed
        """
        try:
            if self.model is None:
                log_error("Model not loaded")
                return None
            
            # Load original image to get its size
            original_img = Image.open(image_path)
            original_img = original_img.convert('RGB')
            original_size = original_img.size
            
            # Preprocess image for model
            img = original_img.resize(self.img_size)
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            img_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)
            
            # Use integrated gradients approach for better visualization
            # Compute gradients with respect to input
            with tf.GradientTape() as tape:
                tape.watch(img_tensor)
                predictions = self.model(img_tensor, training=False)
                loss = predictions[:, class_index]
            
            # Get gradients with respect to input
            grads = tape.gradient(loss, img_tensor)
            
            # Compute integrated gradients (simplified version)
            # Take absolute values and aggregate
            grads_abs = tf.abs(grads)
            saliency_map = tf.reduce_max(grads_abs, axis=-1)  # Max across channels
            saliency_map = tf.squeeze(saliency_map)  # Remove batch dimension
            
            # Normalize saliency map
            saliency_map = saliency_map.numpy()
            saliency_min = saliency_map.min()
            saliency_max = saliency_map.max()
            if saliency_max > saliency_min:
                saliency_map = (saliency_map - saliency_min) / (saliency_max - saliency_min)
            
            # Apply colormap (jet) for visualization
            import matplotlib.pyplot as plt
            import matplotlib.cm as cm
            
            # Use jet colormap
            colormap = cm.get_cmap('jet')
            heatmap_colored = colormap(saliency_map)
            heatmap_colored = (heatmap_colored[:, :, :3] * 255).astype(np.uint8)
            
            # Resize heatmap to original image size for better visual comparison
            heatmap_img = Image.fromarray(heatmap_colored).resize(original_size)
            heatmap_img = heatmap_img.convert('RGB')
            
            # Save heatmap
            output_path = str(Path(image_path).parent / f"gradcam_{Path(image_path).name}")
            heatmap_img.save(output_path)
            
            log_info(f"Grad-CAM generated: {output_path}")
            return output_path
            
        except Exception as e:
            log_error(f"Grad-CAM generation failed: {str(e)}", exc_info=True)
            return None