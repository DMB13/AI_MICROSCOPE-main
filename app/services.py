from __future__ import annotations

import datetime
import time
from pathlib import Path
from shutil import copy2
from typing import Any, Dict, List, Optional, Tuple

import cv2
from PIL import Image

from inference import inference
from model.db import get_db


class InferenceService:
    """Thin wrapper around the inference module for predictions and Grad-CAM."""

    def __init__(self, model: Any = None, last_conv_name: str = "top_activation") -> None:
        self.model = model
        self.last_conv_name = last_conv_name

    def run(
        self,
        image_path: str,
    ) -> Tuple[Dict[str, Any], Optional[Image.Image]]:
        """Run prediction and Grad-CAM for a given image path.

        Returns:
            (result_dict, gradcam_image_or_None)
        """
        result = inference.predict(image_path, model=self.model)

        heatmap_img = inference.grad_cam(
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

    def detect_cameras(self, max_index: int = 5) -> List[str]:
        """Detect available camera indices."""
        cams: List[str] = []
        for i in range(max_index + 1):
            try:
                cap = self.backend.VideoCapture(i, self.backend.CAP_V4L2)
            except Exception:
                cap = self.backend.VideoCapture(i)
            if cap is not None and cap.isOpened():
                cams.append(str(i))
                cap.release()
        if not cams:
            cams = ["No camera detected"]
        return cams

    def start(self, index: int) -> bool:
        """Start a camera stream at the given index."""
        if self.cap is not None and getattr(self.cap, "isOpened", lambda: False)():
            self.stop()
        try:
            cap = self.backend.VideoCapture(index)
        except Exception:
            cap = self.backend.VideoCapture(index)

        if not cap or not cap.isOpened():
            self.cap = None
            self.running = False
            return False

        self.cap = cap
        self.running = True
        return True

    def stop(self) -> None:
        """Stop any active camera stream."""
        self.running = False
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
        self.cap = None

    def read_frame(self) -> Optional[Any]:
        """Read a single frame from the active camera."""
        if not self.running or self.cap is None:
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame.copy()

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

