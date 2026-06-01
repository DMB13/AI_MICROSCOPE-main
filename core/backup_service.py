#!/usr/bin/env python3
"""
Backup Service for AI Microscope Application
Handles automatic database backups for clinical data protection
"""

import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import zipfile

from utils.logger import log_info, log_error, log_warning


class BackupService:
    """Service for automatic database backups."""
    
    def __init__(
        self,
        db_path: Optional[Path] = None,
        backup_dir: Optional[Path] = None,
        max_backups: int = 10
    ):
        """Initialize backup service.
        
        Args:
            db_path: Path to database file (default: clinical_records.db)
            backup_dir: Directory for backups (default: storage/backups)
            max_backups: Maximum number of backups to keep
        """
        if db_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            db_path = base_dir / "clinical_records.db"
        
        if backup_dir is None:
            base_dir = Path(__file__).resolve().parent.parent
            storage_dir = base_dir / "storage"
            storage_dir.mkdir(exist_ok=True)
            backup_dir = storage_dir / "backups"
        
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.max_backups = max_backups
    
    def create_backup(self, compress: bool = True) -> Optional[Path]:
        """Create a backup of the database.
        
        Args:
            compress: Whether to compress the backup
            
        Returns:
            Path to backup file or None if failed
        """
        if not self.db_path.exists():
            log_warning(f"Database file not found: {self.db_path}")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if compress:
                backup_name = f"clinical_records_backup_{timestamp}.zip"
                backup_path = self.backup_dir / backup_name
                
                with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(self.db_path, "clinical_records.db")
            else:
                backup_name = f"clinical_records_backup_{timestamp}.db"
                backup_path = self.backup_dir / backup_name
                shutil.copy2(self.db_path, backup_path)
            
            log_info(f"Backup created: {backup_path}")
            
            # Clean old backups
            self._clean_old_backups()
            
            return backup_path
        except Exception as e:
            log_error(f"Failed to create backup: {str(e)}", exc_info=True)
            return None
    
    def _clean_old_backups(self) -> None:
        """Remove old backups, keeping only max_backups."""
        try:
            backups = sorted(
                self.backup_dir.glob("clinical_records_backup_*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # Remove excess backups
            for old_backup in backups[self.max_backups:]:
                old_backup.unlink()
                log_info(f"Removed old backup: {old_backup.name}")
        except Exception as e:
            log_error(f"Failed to clean old backups: {str(e)}", exc_info=True)
    
    def get_backups(self) -> List[Path]:
        """Get list of existing backups.
        
        Returns:
            List of backup paths sorted by date (newest first)
        """
        try:
            backups = sorted(
                self.backup_dir.glob("clinical_records_backup_*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            return backups
        except Exception as e:
            log_error(f"Failed to list backups: {str(e)}", exc_info=True)
            return []
    
    def restore_backup(self, backup_path: Path) -> bool:
        """Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful, False otherwise
        """
        if not backup_path.exists():
            log_error(f"Backup file not found: {backup_path}")
            return False
        
        try:
            # Create backup of current database before restore
            if self.db_path.exists():
                current_backup = self.db_path.with_suffix(".db.pre-restore")
                shutil.copy2(self.db_path, current_backup)
            
            # Restore from backup
            if backup_path.suffix == ".zip":
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(self.backup_dir)
                    extracted = self.backup_dir / "clinical_records.db"
                    shutil.move(extracted, self.db_path)
            else:
                shutil.copy2(backup_path, self.db_path)
            
            log_info(f"Database restored from: {backup_path}")
            return True
        except Exception as e:
            log_error(f"Failed to restore backup: {str(e)}", exc_info=True)
            return False
    
    def get_backup_size(self) -> int:
        """Get total size of all backups in bytes.
        
        Returns:
            Total size in bytes
        """
        try:
            total_size = sum(f.stat().st_size for f in self.get_backups())
            return total_size
        except Exception as e:
            log_error(f"Failed to calculate backup size: {str(e)}", exc_info=True)
            return 0
