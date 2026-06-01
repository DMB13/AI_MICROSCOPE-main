#!/usr/bin/env python3
"""
Health Check Service for AI Microscope Application
Validates system components on startup
"""

from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum
import os

from utils.logger import log_info, log_error, log_warning


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth:
    """Health status of a single component."""
    
    def __init__(
        self,
        name: str,
        status: HealthStatus,
        message: str,
        details: Optional[Dict] = None
    ):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details
        }


class HealthCheckService:
    """Service for checking system health on startup."""
    
    def __init__(self):
        """Initialize health check service."""
        self.results: List[ComponentHealth] = []
    
    def check_all(self) -> Dict[str, any]:
        """Run all health checks.
        
        Returns:
            Dictionary with overall status and component details
        """
        self.results = []
        
        # Check each component
        self._check_storage()
        self._check_model()
        self._check_camera()
        self._check_database()
        self._check_dependencies()
        
        # Determine overall status
        overall_status = self._get_overall_status()
        
        return {
            "status": overall_status.value,
            "components": [r.to_dict() for r in self.results],
            "healthy_count": sum(1 for r in self.results if r.status == HealthStatus.HEALTHY),
            "degraded_count": sum(1 for r in self.results if r.status == HealthStatus.DEGRADED),
            "unhealthy_count": sum(1 for r in self.results if r.status == HealthStatus.UNHEALTHY)
        }
    
    def _check_storage(self) -> None:
        """Check storage directories."""
        try:
            base_dir = Path(__file__).resolve().parent.parent
            required_dirs = [
                "storage",
                "storage/images",
                "storage/exports",
                "logs"
            ]
            
            missing = []
            for dir_name in required_dirs:
                dir_path = base_dir / dir_name
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    missing.append(dir_name)
            
            if missing:
                self.results.append(ComponentHealth(
                    name="Storage",
                    status=HealthStatus.DEGRADED,
                    message=f"Created missing directories: {', '.join(missing)}",
                    details={"missing_dirs": missing}
                ))
            else:
                self.results.append(ComponentHealth(
                    name="Storage",
                    status=HealthStatus.HEALTHY,
                    message="All storage directories available"
                ))
        except Exception as e:
            self.results.append(ComponentHealth(
                name="Storage",
                status=HealthStatus.UNHEALTHY,
                message=f"Storage check failed: {str(e)}",
                details={"error": str(e)}
            ))
            log_error(f"Storage health check failed: {str(e)}", exc_info=True)
    
    def _check_model(self) -> None:
        """Check AI model availability."""
        try:
            base_dir = Path(__file__).resolve().parent.parent
            model_dir = base_dir / "model"
            
            if not model_dir.exists():
                self.results.append(ComponentHealth(
                    name="Model",
                    status=HealthStatus.UNHEALTHY,
                    message="Model directory not found"
                ))
                return
            
            # Check for model files
            model_files = list(model_dir.glob("*.h5")) + list(model_dir.glob("*.keras"))
            
            if not model_files:
                self.results.append(ComponentHealth(
                    name="Model",
                    status=HealthStatus.UNHEALTHY,
                    message="No model files found in model directory"
                ))
            else:
                model_size = sum(f.stat().st_size for f in model_files) / (1024 * 1024)
                self.results.append(ComponentHealth(
                    name="Model",
                    status=HealthStatus.HEALTHY,
                    message=f"Found {len(model_files)} model file(s)",
                    details={
                        "model_files": [f.name for f in model_files],
                        "total_size_mb": round(model_size, 2)
                    }
                ))
        except Exception as e:
            self.results.append(ComponentHealth(
                name="Model",
                status=HealthStatus.UNHEALTHY,
                message=f"Model check failed: {str(e)}",
                details={"error": str(e)}
            ))
            log_error(f"Model health check failed: {str(e)}", exc_info=True)
    
    def _check_camera(self) -> None:
        """Check camera availability."""
        try:
            import cv2
            
            # Try to detect cameras
            cameras_found = 0
            for i in range(3):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    cameras_found += 1
                    cap.release()
            
            if cameras_found > 0:
                self.results.append(ComponentHealth(
                    name="Camera",
                    status=HealthStatus.HEALTHY,
                    message=f"Found {cameras_found} camera(s)",
                    details={"camera_count": cameras_found}
                ))
            else:
                self.results.append(ComponentHealth(
                    name="Camera",
                    status=HealthStatus.DEGRADED,
                    message="No cameras detected (can use upload mode)",
                    details={"camera_count": 0}
                ))
        except Exception as e:
            self.results.append(ComponentHealth(
                name="Camera",
                status=HealthStatus.DEGRADED,
                message=f"Camera check failed: {str(e)} (can use upload mode)",
                details={"error": str(e)}
            ))
            log_warning(f"Camera health check failed: {str(e)}")
    
    def _check_database(self) -> None:
        """Check database availability."""
        try:
            base_dir = Path(__file__).resolve().parent.parent
            db_path = base_dir / "clinical_records.db"
            
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                self.results.append(ComponentHealth(
                    name="Database",
                    status=HealthStatus.HEALTHY,
                    message=f"Database found ({size_mb:.2f} MB)",
                    details={"size_mb": round(size_mb, 2)}
                ))
            else:
                # Database will be created on first use
                self.results.append(ComponentHealth(
                    name="Database",
                    status=HealthStatus.HEALTHY,
                    message="Database will be created on first use"
                ))
        except Exception as e:
            self.results.append(ComponentHealth(
                name="Database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database check failed: {str(e)}",
                details={"error": str(e)}
            ))
            log_error(f"Database health check failed: {str(e)}", exc_info=True)
    
    def _check_dependencies(self) -> None:
        """Check critical dependencies."""
        try:
            # Map package name (pip) -> import module name
            dependencies = {
                "tensorflow": ("tensorflow", "2.18"),
                "opencv-python": ("cv2", None),
                "Pillow": ("PIL", None),
                "customtkinter": ("customtkinter", None),
                "numpy": ("numpy", None)
            }
            
            missing = []
            version_info = {}
            
            for package, (import_name, min_version) in dependencies.items():
                try:
                    mod = __import__(import_name)
                    version = getattr(mod, "__version__", "unknown")
                    version_info[package] = version
                    
                    if min_version and version < min_version:
                        missing.append(f"{package} (requires >={min_version}, has {version})")
                except ImportError:
                    missing.append(package)
            
            if missing:
                self.results.append(ComponentHealth(
                    name="Dependencies",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Missing dependencies: {', '.join(missing)}",
                    details={"missing": missing, "versions": version_info}
                ))
            else:
                self.results.append(ComponentHealth(
                    name="Dependencies",
                    status=HealthStatus.HEALTHY,
                    message="All critical dependencies installed",
                    details={"versions": version_info}
                ))
        except Exception as e:
            self.results.append(ComponentHealth(
                name="Dependencies",
                status=HealthStatus.UNHEALTHY,
                message=f"Dependency check failed: {str(e)}",
                details={"error": str(e)}
            ))
            log_error(f"Dependency health check failed: {str(e)}", exc_info=True)
    
    def _get_overall_status(self) -> HealthStatus:
        """Get overall health status.
        
        Returns:
            Overall HealthStatus
        """
        if any(r.status == HealthStatus.UNHEALTHY for r in self.results):
            return HealthStatus.UNHEALTHY
        elif any(r.status == HealthStatus.DEGRADED for r in self.results):
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY
    
    def print_report(self) -> None:
        """Print health check report to console."""
        print("\n" + "="*60)
        print("AI MICROSCOPE HEALTH CHECK REPORT")
        print("="*60)
        
        for result in self.results:
            status_symbol = "✓" if result.status == HealthStatus.HEALTHY else "⚠" if result.status == HealthStatus.DEGRADED else "✗"
            print(f"\n{status_symbol} {result.name}: {result.status.value.upper()}")
            print(f"  {result.message}")
            if result.details:
                for key, value in result.details.items():
                    print(f"  - {key}: {value}")
        
        overall = self._get_overall_status()
        print("\n" + "="*60)
        print(f"OVERALL STATUS: {overall.value.upper()}")
        print("="*60 + "\n")
