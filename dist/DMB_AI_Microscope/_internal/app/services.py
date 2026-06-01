from __future__ import annotations

import datetime
import cv2
import time
from PIL import Image
from pathlib import Path
from typing import Optional, Any, List, Dict, Tuple
from shutil import copy2

import inference as inference_module
from model.db import get_db


class InferenceService:
    """Thin wrapper around the inference module for predictions and Grad-CAM."""

    def __init__(self, model: Any = None, last_conv_name: str = "top_conv") -> None:
        self.model = model
        self.last_conv_name = last_conv_name

    def predict(self, image_path: str, top_k: int = 5) -> Dict[str, Any]:
        """Run prediction on an image and return top-k results with scores.
        Args:
            image_path: Path to the image file.
            top_k: Number of top predictions to return (not used by inference module).
        Returns:
            Dictionary with top_k predictions and metadata.
        """
        if self.model is None:
            raise ValueError("Model not set. Call set_model() first.")
        return inference_module.predict(image_path, self.model)

    def run(
        self,
        image_path: str,
    ) -> Tuple[Dict[str, Any], Optional[Image.Image]]:
        """Run prediction and Grad-CAM for a given image path.

        Returns:
            (result_dict, gradcam_image_or_None)
        """
        result = self.predict(image_path)

        heatmap_img = inference_module.grad_cam(
            image_path,
            model=self.model,
            last_conv_name=self.last_conv_name,
        )

        return result, heatmap_img


class RecordService:
    """Handles persistence of clinical records and related image files."""

    def __init__(
        self,
        records_dir: Optional[Path] = None,
        db: Any = None,
    ) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self.records_dir = records_dir or (base_dir / "model" / "records")
        self.db = db or get_db()

    def save_record(
        self,
        patient_id: str,
        result: Dict[str, Any],
        source_image_path: str,
        gradcam_path: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
    ) -> Dict[str, Any]:
        """Persist a clinical record and return the stored record payload.

        This mirrors the previous behavior in the GUI:
        - Copies the source image into the records directory with a timestamped name
        - Inserts a row into the clinical_records table
        """
        self.records_dir.mkdir(parents=True, exist_ok=True)

        ts = timestamp or datetime.datetime.now()
        timestamp_slug = ts.strftime("%Y%m%d_%H%M%S")
        img_dest = self.records_dir / f"capture_{timestamp_slug}.png"

        copy2(source_image_path, img_dest)

        db_timestamp = ts.isoformat()
        row_id = self.db.insert_record(
            patient_id=patient_id or "N/A",
            species=result.get("species"),
            confidence=result.get("confidence"),
            image_path=str(img_dest),
            gradcam_path=gradcam_path,
            timestamp=db_timestamp,
        )

        payload = {
            "id": row_id,
            "patient_id": patient_id or "N/A",
            "timestamp": db_timestamp,
            "species": result.get("species"),
            "confidence": result.get("confidence"),
            "image_path": str(img_dest),
            "gradcam_path": gradcam_path,
        }
        return payload


class CameraService:
    """Encapsulates all camera access and live frame capture."""

    def __init__(self, backend: Any = None) -> None:
        self.backend = backend or cv2
        self.cap: Optional[Any] = None
        self.running: bool = False

    def detect_cameras(self, max_index: int = 10) -> List[str]:
        """Detect available camera indices with aggressive detection and USB priority."""
        cams: List[str] = []
        usb_cameras: List[str] = []
        other_cameras: List[str] = []
        
        # Check all indices aggressively
        for i in range(max_index + 1):
            try:
                # Try multiple backend options for robustness
                cap = None
                for backend in [self.backend.CAP_DSHOW, self.backend.CAP_V4L2, 0]:
                    try:
                        cap = self.backend.VideoCapture(i, backend)
                        if cap is not None and cap.isOpened():
                            break
                    except Exception:
                        continue
                
                if cap is None:
                    cap = self.backend.VideoCapture(i)
                
                if cap is not None and cap.isOpened():
                    # Try to get camera info to identify USB cameras
                    try:
                        backend_name = cap.getBackendName()
                        # USB cameras typically use DSHOW on Windows or V4L2 on Linux
                        is_usb = 'DSHOW' in backend_name or 'V4L2' in backend_name or i > 0
                    except Exception:
                        is_usb = i > 0  # Assume index > 0 is USB camera
                    
                    cam_name = f"Camera {i}"
                    if is_usb:
                        cam_name += " (USB)"
                        usb_cameras.append(cam_name)
                    else:
                        other_cameras.append(cam_name)
                    
                    cap.release()
            except Exception:
                continue
        
        # Prioritize USB cameras
        cams = usb_cameras + other_cameras
        
        if not cams:
            cams = ["No camera detected"]
        return cams

    def get_best_camera_index(self, max_index: int = 10) -> int:
        """Get the best available camera index with USB priority."""
        # Try to find USB cameras first (indices > 0 typically USB)
        for i in range(max_index, 0, -1):  # Check higher indices first (usually USB)
            try:
                cap = None
                for backend in [self.backend.CAP_DSHOW, self.backend.CAP_V4L2, 0]:
                    try:
                        cap = self.backend.VideoCapture(i, backend)
                        if cap is not None and cap.isOpened():
                            break
                    except Exception:
                        continue
                
                if cap is None:
                    cap = self.backend.VideoCapture(i)
                
                if cap is not None and cap.isOpened():
                    cap.release()
                    return i
            except Exception:
                continue
        
        # Fall back to index 0 (built-in camera)
        try:
            cap = self.backend.VideoCapture(0)
            if cap is not None and cap.isOpened():
                cap.release()
                return 0
        except Exception:
            pass
        
        return -1  # No camera found

    def start(self, index: int) -> bool:
        """Start a camera stream at the given index."""
        if self.cap is not None and getattr(self.cap, "isOpened", lambda: False)():
            self.stop()
        try:
            cap = self.backend.VideoCapture(index)
        except Exception:
            cap = self.backend.VideoCapture(index)
        
        if cap is not None and cap.isOpened():
            self.cap = cap
            self.running = True
            return True
        return False

    def stop(self) -> None:
        """Stop any active camera stream."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.running = False

    def read_frame(self) -> Optional[Any]:
        """Read a single frame from the active camera."""
        if self.cap is None or not self.running:
            return None
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None

    def capture_frame_to_file(self, frame: Any, records_dir: Path) -> Path:
        """Persist a BGR frame to an image file in the records directory."""
        records_dir.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        img_dest = records_dir / f"capture_{timestamp}.png"
        self.backend.imwrite(str(img_dest), frame)
        return img_dest


def apply_image_adjustments(img: Image.Image, brightness: int, contrast: int) -> Image.Image:
    """Apply brightness and contrast adjustments to an image."""
    from PIL import ImageEnhance

    result = img

    if brightness != 0:
        enhancer = ImageEnhance.Brightness(result)
        factor = 1.0 + (brightness / 100.0)
        result = enhancer.enhance(factor)

    if contrast != 0:
        enhancer = ImageEnhance.Contrast(result)
        factor = 1.0 + (contrast / 100.0)
        result = enhancer.enhance(factor)

    return result

