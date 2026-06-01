#!/usr/bin/env python3
"""
Heatmap Overlay for AI Microscope Application
Handles side-by-side original + heatmap with opacity control
"""

import numpy as np
from PIL import Image, ImageEnhance
from typing import Optional, Tuple
import cv2

from utils.logger import log_info


class HeatmapOverlay:
    """Manages heatmap overlay on original images."""
    
    def __init__(self):
        """Initialize heatmap overlay."""
        self.opacity = 0.5  # Default 50% opacity
    
    def set_opacity(self, opacity: float) -> None:
        """Set overlay opacity.
        
        Args:
            opacity: Opacity value (0.0 to 1.0)
        """
        self.opacity = max(0.0, min(1.0, opacity))
    
    def create_colormap_heatmap(self, heatmap: np.ndarray, colormap: int = cv2.COLORMAP_JET) -> np.ndarray:
        """Apply colormap to heatmap.
        
        Args:
            heatmap: Raw heatmap array
            colormap: OpenCV colormap constant
            
        Returns:
            Colored heatmap
        """
        heatmap_normalized = ((heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-10) * 255).astype(np.uint8)
        return cv2.applyColorMap(heatmap_normalized, colormap)
    
    def overlay_heatmap(self, original: np.ndarray, heatmap: np.ndarray) -> np.ndarray:
        """Overlay heatmap on original image with opacity.
        
        Args:
            original: Original image (BGR or RGB)
            heatmap: Heatmap array
            
        Returns:
            Overlayed image
        """
        # Create colored heatmap
        colored_heatmap = self.create_colormap_heatmap(heatmap)
        
        # Blend images
        overlay = cv2.addWeighted(original, 1 - self.opacity, colored_heatmap, self.opacity, 0)
        
        return overlay
    
    def create_side_by_side(self, original: np.ndarray, heatmap: np.ndarray, width: int = 800) -> np.ndarray:
        """Create side-by-side view of original and overlay.
        
        Args:
            original: Original image
            heatmap: Heatmap array
            width: Target width for side-by-side view
            
        Returns:
            Side-by-side image
        """
        # Create overlay
        overlay = self.overlay_heatmap(original, heatmap)
        
        # Resize images to same height
        h = max(original.shape[0], overlay.shape[0])
        original_resized = cv2.resize(original, (width, h))
        overlay_resized = cv2.resize(overlay, (width, h))
        
        # Concatenate horizontally
        side_by_side = np.hstack([original_resized, overlay_resized])
        
        return side_by_side
    
    def save_side_by_side(self, original_path: str, heatmap: np.ndarray, output_path: str) -> None:
        """Save side-by-side view to file.
        
        Args:
            original_path: Path to original image
            heatmap: Heatmap array
            output_path: Output file path
        """
        original = cv2.imread(original_path)
        if original is None:
            raise ValueError(f"Could not load image from {original_path}")
        
        side_by_side = self.create_side_by_side(original, heatmap)
        cv2.imwrite(output_path, side_by_side)
        log_info(f"Side-by-side image saved to {output_path}")
