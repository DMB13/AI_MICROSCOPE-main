import os
import sys
import json
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List
from PIL import Image

if getattr(sys,'frozen', False):
    basedir = Path(sys._MEIPASS) if hasattr(sys.'_MEIPASS') else 
Path(sys.executable.parent
else:
    basedir = Path(__file__).resolve().parent

sys.path.insert(0, basedir)

# Global Cache
_MODEL = None
_CLASS_INDICES = None

def _ensure_tf():
    try:
        import tensorflow as tf
        # Optimization for Ubuntu: reduce log noise
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0' 
        return tf
    except ImportError:
        raise RuntimeError("TensorFlow not found. Install it via: pip install tensorflow")

def load_model(model_path: Optional[str] = None):
    """Lazy loads the Fusion Keras model."""
    global _MODEL
    tf = _ensure_tf()
    
    if _MODEL is None:
        # Default Ubuntu pathing
        p = model_path or str(basedir /"model" /"brst_microscope_fusion.keras")
        if not os.path.exists(p):
            raise FileNotFoundError(f"Brain file not found at {p}")
        
        # We use compile=False to avoid issues with custom fusion loss functions
        _MODEL = tf.keras.models.load_model(p, compile=False)
        print(f"--- Fusion Brain Loaded Successfully ---")
    return _MODEL

def load_class_indices():
    """Loads the species mapping with Ubuntu pathing."""
    global _CLASS_INDICES
    if _CLASS_INDICES is None:
        path = basedir /"model/class_indices.json"
        if path.exists():
            with open(path, 'r') as f:
                _CLASS_INDICES = json.load(f)
        else:
            _CLASS_INDICES = {str(i): f"Species_{i}" for i in range(39)}
    return _CLASS_INDICES

def preprocess_image(image_path: str, target_size=(224, 224)):
    """Prepares image for the Fusion model."""
    img = Image.open(image_path).convert('RGB')
    img = img.resize(target_size)
    x = np.array(img).astype('float32')
    # Use standard ImageNet scaling (or whatever was used in training)
    x = x / 255.0 
    return np.expand_dims(x, axis=0)

def predict(image_path: str, model=None) -> Dict[str, Any]:
    """Handles Fusion model output to extract the correct species name with confidence guardrail."""
    tf = _ensure_tf()
    if model is None:
        model = load_model()
    
    # Preprocess image
    x = preprocess_image(image_path, target_size=(224, 224))
    
    # RUN PREDICTION
    raw_output = model.predict(x, verbose=0)

    # BRAIN FIX: If Fusion model returns a list [head1, head2], take head 0
    if isinstance(raw_output, list):
        preds = raw_output[0]
    else:
        preds = raw_output

    # Get the index of the highest probability
    probabilities = tf.nn.softmax(preds[0]).numpy()
    idx = int(np.argmax(probabilities))
    conf = float(probabilities[idx])

    # CONFIDENCE GUARDRAIL: Apply hard mathematical cutoff
    CONFIDENCE_THRESHOLD = 0.65  # 65% threshold
    
    if conf < CONFIDENCE_THRESHOLD:
        # REJECTED: Low confidence - override with inconclusive result
        return {
            "species": "Inconclusive / Non-Bacterial",
            "confidence": conf,
            "class_index": idx,
            "status": "REJECTED"
        }
    else:
        # CONFIRMED: High confidence - proceed with normal lookup
        class_map = load_class_indices()
        # Try string key first, then integer key
        species = class_map.get(str(idx), class_map.get(idx, f"Pathogen_ID_{idx}"))
        
        return {
            "species": str(species).replace("_", " "),  # Clean up underscores
            "confidence": conf,
            "class_index": idx,
            "status": "CONFIRMED"
        }

def grad_cam(image_path: str, model=None, last_conv_name: str = "top_activation") -> Image.Image:
    """Generates the heatmap for the Fusion architecture."""
    tf = _ensure_tf()
    if model is None:
        model = load_model()

    img_array = preprocess_image(image_path)
    
    # Create a model that maps input to the activations of the last conv layer
    # and the final output head.
    try:
        grad_model = tf.keras.models.Model(
            inputs=[model.inputs],
            outputs=[model.get_layer(last_conv_name).output, model.output]
        )
    except Exception as e:
        print(f"Layer lookup failed: {e}")
        return None

    with tf.GradientTape() as tape:
        last_conv_output, predictions = grad_model(img_array)
        # Handle Fusion output list
        if isinstance(predictions, list):
            predictions = predictions[0]
        
        # Target the specific class found in prediction
        top_idx = tf.argmax(predictions[0])
        loss = predictions[:, top_idx]

    # Calculate gradients
    grads = tape.gradient(loss, last_conv_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Calculate Heatmap
    last_conv_output = last_conv_output[0]
    heatmap = last_conv_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # Normalize heatmap
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-10)
    heatmap = heatmap.numpy()

    # Colorize with OpenCV (Standard on Ubuntu)
    import cv2
    orig_img = cv2.imread(image_path)
    if orig_img is None:
        print(f"Error: Could not read image {image_path}")
        return None
    
    # Ensure heatmap is valid
    if heatmap.size == 0 or np.isnan(heatmap).all():
        print("Error: Invalid heatmap generated")
        return None
    
    # Resize heatmap to match original image size
    try:
        # Convert heatmap to uint8 for OpenCV processing
        heatmap_uint8 = np.uint8(255 * heatmap)
        heatmap_resized = cv2.resize(heatmap_uint8, (orig_img.shape[1], orig_img.shape[0]))
    except Exception as e:
        print(f"Error resizing heatmap: {e}")
        return None
        
    # Apply color map
    heatmap_colored = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
    
    # Superimpose
    superimposed = cv2.addWeighted(orig_img, 0.6, heatmap_colored, 0.4, 0)
    
    # Convert back to PIL Image
    result = Image.fromarray(cv2.cvtColor(superimposed, cv2.COLOR_BGR2RGB))
    return result
