import os
import sys
import json
import numpy as np
import cv2
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from PIL import Image

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress all TensorFlow logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN custom operations

# Suppress Python warnings
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Import keras separately for TensorFlow 2.15+ compatibility
try:
    import keras
    # Create custom DTypePolicy class to handle model compatibility
    try:
        # Try to register for newer Keras versions (3.x)
        if hasattr(keras.saving, 'register_keras_serializable'):
            @keras.saving.register_keras_serializable()
            class DTypePolicy:
                def __init__(self, name="mixed_float16"):
                    self.name = name
                
                def get_config(self):
                    return {"name": self.name}
                
                @classmethod
                def from_config(cls, config):
                    return cls(**config)
        else:
            # For older Keras versions (2.x), just define the class
            class DTypePolicy:
                def __init__(self, name="mixed_float16"):
                    self.name = name
                
                def get_config(self):
                    return {"name": self.name}
                
                @classmethod
                def from_config(cls, config):
                    return cls(**config)
    except AttributeError:
        # Fallback if keras.saving doesn't exist
        class DTypePolicy:
            def __init__(self, name="mixed_float16"):
                self.name = name
            
            def get_config(self):
                return {"name": self.name}
            
            @classmethod
            def from_config(cls, config):
                return cls(**config)
except ImportError:
    keras = None

# ==========================================
# 1. ENVIRONMENT & PATH INITIALIZATION
# ==========================================
if getattr(sys, 'frozen', False):
    # Packaged environment (MSI/EXE)
    basedir = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
else:
    # Development environment
    basedir = Path(__file__).resolve().parent.parent

# Ensure the app can find adjacent modules
sys.path.insert(0, str(basedir))

# Global Cache to prevent redundant memory allocation
_MODEL = None
_CLASS_INDICES = None

# Model Configuration for 34-class Clinical Rugged EfficientNetV2M
MODEL_CONFIG = {
    "input_size": (224, 224),  # EfficientNetV2M uses 224x224
    "num_classes": 34,  # 33 bacterial species + 1 background class
    "total_params": 105720534,  # ~105M parameters
    "architecture": "EfficientNetV2M",
    "base_model": "EfficientNetV2M",
    "preprocessing": "efficientnet_v2",  # Use EfficientNetV2 preprocessing
    "clinical_rugged": True,  # Model trained with clinical ruggedness
}

def _ensure_tf():
    """Lazy import of TensorFlow to keep GUI startup fast."""
    try:
        import tensorflow as tf
        # Reduce log noise on Windows 11
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        # Setup memory growth to prevent initialization errors
        try:
            gpu_devices = tf.config.list_physical_devices('GPU')
            if gpu_devices:
                try:
                    for gpu in gpu_devices:
                        tf.config.experimental.set_memory_growth(gpu, True)
                except RuntimeError:
                    pass
        except AttributeError:
            pass
        return tf
    except ImportError:
        raise RuntimeError("TensorFlow not found in the current environment.")

# ==========================================
# 2. MODEL & METADATA LOADERS
# ==========================================
def load_model(model_path: Optional[str] = None):
    """Loads the 34-class Clinical Rugged EfficientNetV2M model."""
    global _MODEL, keras
    tf = _ensure_tf()

    if _MODEL is None:
        p = model_path or str(basedir / "model" / "best_clinical_rugged_1777619657.keras")
        
        if not os.path.exists(p):
            raise FileNotFoundError(f"Model file missing at: {p}")

        print(f"Loading 34-class Clinical Rugged EfficientNetV2M model...")
        
        # Load without compile to avoid custom loss issues
        try:
            _MODEL = tf.keras.models.load_model(p, compile=False)
            print("Model loaded successfully!")
            
            # Verify model structure
            print(f"Model has {len(_MODEL.layers)} layers")
            
            # Check input shape
            expected_shape = (None, 224, 224, 3)
            if _MODEL.input_shape != expected_shape:
                print(f"Note: Input shape is {_MODEL.input_shape}")
            
            # Check output shape
            if _MODEL.output_shape[-1] != 34:
                print(f"Note: Model has {_MODEL.output_shape[-1]} output classes")
                
        except Exception as e:
            print(f"Error loading model: {e}")
            raise RuntimeError(f"Failed to load clinical rugged model: {e}")
        
        print(f"--- Model Loaded Successfully ---")
        print(f"Model input shape: {_MODEL.input_shape}")
        print(f"Model output shape: {_MODEL.output_shape}")
        print(f"Total parameters: {_MODEL.count_params():,}")
    return _MODEL

def load_class_indices():
    """Loads the 34-class species mapping for identification (including background)."""
    global _CLASS_INDICES
    if _CLASS_INDICES is None:
        # Build 34-class mapping from clinical dataset structure
        clinical_dir = basedir / "dataset_clinical" / "train"
        if clinical_dir.exists():
            class_names = sorted([d.name for d in clinical_dir.iterdir() if d.is_dir()])
            # The model was trained with 00_Background at index 0, then 33 species
            # So we need to shift indices: background=0, species=1-33
            _CLASS_INDICES = {"0": "00_Background"}
            for i, name in enumerate(class_names):
                _CLASS_INDICES[str(i + 1)] = name
            print(f"Loaded 34-class species mapping from clinical dataset (with background at index 0)")
        else:
            # Fallback to 33-class mapping
            path = basedir / "model" / "species_33_mapping.json"
            if path.exists():
                with open(path, 'r') as f:
                    data = json.load(f)
                    if "index_to_species" in data:
                        _CLASS_INDICES = data["index_to_species"]
                        # Add background class at index 0
                        _CLASS_INDICES = {str(int(k)+1): v for k, v in _CLASS_INDICES.items()}
                        _CLASS_INDICES["0"] = "00_Background"
                        print(f"Loaded 33-class species mapping and added background class")
                    else:
                        _CLASS_INDICES = data if isinstance(data, dict) else {str(i): f"Species_ID_{i}" for i in range(34)}
                        _CLASS_INDICES["0"] = "00_Background"
                        print(f"Loaded species mapping from {path}")
            else:
                # Final fallback
                _CLASS_INDICES = {str(i): f"Species_ID_{i}" for i in range(34)}
                _CLASS_INDICES["0"] = "00_Background"
                print("Using fallback species mapping")
    return _CLASS_INDICES

def get_model_info():
    """Returns information about the loaded model."""
    model = load_model()
    return {
        "name": model.name,
        "input_shape": model.input_shape,
        "output_shape": model.output_shape,
        "total_params": model.count_params(),
        "num_layers": len(model.layers),
        "config": MODEL_CONFIG
    }

# ==========================================
# 3. CORE INFERENCE
# ==========================================
def preprocess_image(image_path: str, target_size=(224, 224)):
    """
    Standardizes image input for the EfficientNetV2M architecture.
    Uses 224x224 input size for the 34-class clinical rugged model.
    """
    tf = _ensure_tf()
    
    # Load and convert to RGB
    img = Image.open(image_path).convert('RGB')
    
    # Resize to exactly 224x224 (EfficientNetV2M training input)
    img = img.resize(target_size, Image.BILINEAR)
    
    # Convert to array and apply EfficientNetV2 specific preprocessing
    # (Scaling pixels from [0, 255] to the model's expected distribution)
    arr = np.array(img).astype('float32')
    arr = tf.keras.applications.efficientnet_v2.preprocess_input(arr)
    
    # Ensure float32 precision for Windows 11 compatibility
    tensor = tf.convert_to_tensor(arr, dtype=tf.float32)
    
    # Add batch dimension: (1, 224, 224, 3)
    return tf.expand_dims(tensor, axis=0)

def predict(image_path: str, model=None, return_all_scores: bool = False) -> Dict[str, Any]:
    """Runs inference and applies clinical confidence guardrails."""
    tf = _ensure_tf()
    if model is None:
        model = load_model()
    
    # Prepare data at 224x224 resolution (33-class model input size)
    x = preprocess_image(image_path, target_size=(224, 224))
    
    # Execute prediction
    raw_output = model.predict(x, verbose=0)
    
    # Extract the prediction
    preds = raw_output[0] if isinstance(raw_output, list) else raw_output
    probabilities = preds[0]
    
    # Get top prediction
    idx = int(np.argmax(probabilities))
    conf = float(probabilities[idx])
    
    # Get top 3 predictions for analysis
    top_3_indices = np.argsort(probabilities)[-3:][::-1]
    top_3 = [
        {"class": int(i), "confidence": float(probabilities[i])}
        for i in top_3_indices
    ]
    
    # Load class mapping
    class_map = load_class_indices()
    species = class_map.get(str(idx), f"Class_{idx}")
    
    # Build result
    result = {
        "species": str(species).replace("_", " "),
        "confidence": conf,
        "class_index": idx,
        "top_3": top_3,
        "all_probabilities": probabilities.tolist() if return_all_scores else None,
        "model_type": "efficientnetv2m_clinical_rugged_34class",
        "input_size": (224, 224)
    }
    
    # Apply clinical guardrail (90% threshold)
    if conf < 0.90:
        result["status"] = "REJECTED"
        result["clinical_note"] = "Confidence below 90% threshold - manual review required"
    else:
        result["status"] = "CONFIRMED"
        result["clinical_note"] = "High confidence prediction"
    
    return result

# ==========================================
# 4. VISUALIZATION (Grad-CAM)
# ==========================================
def grad_cam(image_path: str, model=None, last_conv_name: str = "top_conv") -> Optional[Image.Image]:
    """Generates the diagnostic heat-map. Uses EfficientNetV2M's top_conv layer."""
    tf = _ensure_tf()
    if model is None:
        model = load_model()

    img_array = preprocess_image(image_path, target_size=MODEL_CONFIG["input_size"])
    
    try:
        # For EfficientNetV2M model, find appropriate convolutional layer
        # The model has a dual-branch structure with top_conv and Conv_1 layers
        
        if last_conv_name is None:
            # Auto-detect best convolutional layer for Grad-CAM
            # Look for the last convolutional layer before global pooling
            candidate_layers = [
                "top_conv",              # EfficientNetV2M final conv layer
                "Conv_1",                # Secondary conv layer
                "block7a_project_conv",  # Final block conv
                "block6a_project_conv",  # Earlier block conv
            ]
            
            for layer_name in candidate_layers:
                try:
                    layer = model.get_layer(layer_name)
                    if hasattr(layer, 'output'):
                        output_shape = layer.output.shape
                        if len(output_shape) == 4:  # Conv layer: (batch, h, w, channels)
                            last_conv_name = layer_name
                            print(f"Grad-CAM using layer: {layer_name} (shape: {output_shape})")
                            break
                except ValueError:
                    continue
            
            if last_conv_name is None:
                # Fallback: search for any suitable conv layer
                for layer in model.layers:
                    if hasattr(layer, 'output') and len(layer.output.shape) == 4:
                        # Skip input layer and early layers
                        if 'conv' in layer.name.lower() or 'project' in layer.name.lower():
                            last_conv_name = layer.name
                            print(f"Grad-CAM using detected layer: {layer.name}")
                            break
            
            # If still not found, try to find inside sub-models (like EfficientNetV2-M wrapper)
            if last_conv_name is None:
                for layer in model.layers:
                    if hasattr(layer, 'layers'):  # It's a sub-model
                        for sublayer in layer.layers:
                            if hasattr(sublayer, 'output') and len(sublayer.output.shape) == 4:
                                if 'conv' in sublayer.name.lower() or 'project' in sublayer.name.lower():
                                    last_conv_name = sublayer.name
                                    print(f"Grad-CAM using layer from sub-model: {layer.name}/{sublayer.name}")
                                    break
                        if last_conv_name:
                            break
        
        if last_conv_name is None:
            print("No suitable convolutional layer found for Grad-CAM")
            return None
        
        # Get the actual layer object and track if it's from a sub-model
        conv_layer = None
        sub_model = None
        try:
            conv_layer = model.get_layer(last_conv_name)
        except ValueError:
            # Try to find in sub-models
            for layer in model.layers:
                if hasattr(layer, 'layers'):
                    try:
                        conv_layer = layer.get_layer(last_conv_name)
                        sub_model = layer  # Remember the sub-model
                        break
                    except ValueError:
                        continue
        
        if conv_layer is None:
            print(f"Could not access layer {last_conv_name} for Grad-CAM")
            return None
        
        # Create Grad-CAM model - handle sub-model case
        try:
            if sub_model is not None:
                # Layer is inside a sub-model - build grad model from sub-model
                print(f"Building Grad-CAM from sub-model: {sub_model.name}")
                grad_model = tf.keras.models.Model(
                    inputs=[sub_model.inputs],
                    outputs=[conv_layer.output, sub_model.output]
                )
                # Need to preprocess through the sub-model
                img_array = preprocess_image(image_path, target_size=MODEL_CONFIG["input_size"])
            else:
                # Standard case - layer is directly accessible
                grad_model = tf.keras.models.Model(
                    inputs=[model.inputs],
                    outputs=[conv_layer.output, model.output]
                )
        except ValueError as e:
            print(f"Grad-CAM model creation failed: {e}")
            return None
        
        # Compute gradients
        with tf.GradientTape() as tape:
            last_conv_output, predictions = grad_model(img_array)
            if isinstance(predictions, list):
                predictions = predictions[0]
            
            # Get the predicted class
            pred_class = tf.argmax(predictions[0])
            loss = predictions[:, pred_class]
        
        # Gradients
        grads = tape.gradient(loss, last_conv_output)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Weighted combination
        last_conv_output = last_conv_output[0]
        heatmap = last_conv_output @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        
        # Normalize
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-10)
        
        # Convert to numpy array and resize to match original image size
        heatmap_np = heatmap.numpy()
        heatmap_resized = cv2.resize(heatmap_np, (MODEL_CONFIG["input_size"][1], MODEL_CONFIG["input_size"][0]))
        
        # Apply colormap (jet: blue -> green -> yellow -> red)
        heatmap_uint8 = np.uint8(255 * heatmap_resized)
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Load original image
        orig_img = Image.open(image_path).convert('RGB')
        orig_img = orig_img.resize(MODEL_CONFIG["input_size"], Image.BILINEAR)
        
        # Convert heatmap to PIL Image
        heatmap_img = Image.fromarray(heatmap_colored)
        
        # Blend original image with heatmap (alpha=0.4 for 40% heatmap, 60% original)
        superimposed = Image.blend(orig_img, heatmap_img, alpha=0.4)
        
        return superimposed
        
    except Exception as e:
        print(f"Grad-CAM generation failed: {e}")
        print(f"❌ Grad-CAM generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_superimposed_heatmap(image_path: str, heatmap: Image.Image, alpha: float = 0.4) -> Image.Image:
    """Superimpose Grad-CAM heatmap on original image."""
    # Load original image
    orig_img = Image.open(image_path).convert('RGB')
    orig_img = orig_img.resize(MODEL_CONFIG["input_size"], Image.BILINEAR)
    
    # Resize heatmap to match
    heatmap_resized = heatmap.resize(MODEL_CONFIG["input_size"], Image.BILINEAR)
    
    # Apply colormap (jet)
    heatmap_array = np.array(heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_array, cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL
    heatmap_img = Image.fromarray(heatmap_colored)
    
    # Blend
    superimposed = Image.blend(orig_img, heatmap_img, alpha=alpha)
    
    return superimposed

# ==========================================
# 5. BATCH PROCESSING & UTILITIES
# ==========================================
def predict_batch(image_paths: List[str], model=None) -> List[Dict[str, Any]]:
    """Batch prediction for multiple images."""
    if model is None:
        model = load_model()
    
    results = []
    for path in image_paths:
        try:
            result = predict(path, model=model)
            results.append(result)
        except Exception as e:
            results.append({
                "error": str(e),
                "species": "ERROR",
                "confidence": 0.0,
                "status": "FAILED"
            })
    return results

def clear_model_cache():
    """Clear the cached model to free memory."""
    global _MODEL
    _MODEL = None
    print("Model cache cleared")
