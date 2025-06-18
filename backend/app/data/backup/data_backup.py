import logging
import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataBackup:
    """Handles data backup and restoration operations."""
    
    def __init__(self, backup_dir: str = "data_backups"):
        """
        Initialize the data backup handler.
        
        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = backup_dir
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Ensure the backup directory exists."""
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a backup of the data.
        
        Args:
            data: List of data entries to backup
            metadata: Optional metadata about the backup
            
        Returns:
            str: Path to the backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.backup_dir}/backup_{timestamp}.json"
        
        try:
            backup_data = {
                'timestamp': timestamp,
                'data': data,
                'metadata': metadata or {},
                'entry_count': len(data)
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Created backup at {backup_file} with {len(data)} entries")
            return backup_file
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            raise
    
    def restore_backup(self, backup_file: str) -> List[Dict[str, Any]]:
        """
        Restore data from a backup file.
        
        Args:
            backup_file: Path to the backup file
            
        Returns:
            List[Dict[str, Any]]: Restored data
        """
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            logger.info(f"Restored backup from {backup_file} with {backup_data['entry_count']} entries")
            return backup_data['data']
        except Exception as e:
            logger.error(f"Error restoring backup: {str(e)}")
            raise
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups.
        
        Returns:
            List[Dict[str, Any]]: List of backup information
        """
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.startswith('backup_') and file.endswith('.json'):
                file_path = os.path.join(self.backup_dir, file)
                try:
                    with open(file_path, 'r') as f:
                        backup_data = json.load(f)
                    backups.append({
                        'file': file,
                        'timestamp': backup_data['timestamp'],
                        'entry_count': backup_data['entry_count'],
                        'metadata': backup_data.get('metadata', {})
                    })
                except Exception as e:
                    logger.error(f"Error reading backup {file}: {str(e)}")
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def delete_backup(self, backup_file: str) -> bool:
        """
        Delete a backup file.
        
        Args:
            backup_file: Path to the backup file
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            os.remove(backup_file)
            logger.info(f"Deleted backup {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Error deleting backup: {str(e)}")
            return False
    
    def cleanup_old_backups(self, keep_last_n: int = 5) -> int:
        """
        Clean up old backups, keeping only the most recent N backups.
        
        Args:
            keep_last_n: Number of most recent backups to keep
            
        Returns:
            int: Number of backups deleted
        """
        backups = self.list_backups()
        if len(backups) <= keep_last_n:
            return 0
        
        deleted_count = 0
        for backup in backups[keep_last_n:]:
            backup_file = os.path.join(self.backup_dir, backup['file'])
            if self.delete_backup(backup_file):
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old backups")
        return deleted_count

def main():
    """Test the data backup functionality."""
    backup = DataBackup()
    
    # Create sample data
    sample_data = [
        {'id': 1, 'name': 'Test 1'},
        {'id': 2, 'name': 'Test 2'}
    ]
    
    # Create a backup
    backup_file = backup.create_backup(
        sample_data,
        metadata={'source': 'test', 'version': '1.0'}
    )
    
    # List backups
    backups = backup.list_backups()
    print("\nAvailable Backups:")
    print(json.dumps(backups, indent=2))
    
    # Restore backup
    restored_data = backup.restore_backup(backup_file)
    print("\nRestored Data:")
    print(json.dumps(restored_data, indent=2))
    
    # Clean up old backups
    deleted = backup.cleanup_old_backups(keep_last_n=1)
    print(f"\nDeleted {deleted} old backups")

if __name__ == "__main__":
    main() 