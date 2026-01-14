"""
File history manager for tracking recently opened files.
"""
import os
import json
from typing import List, Optional
from pathlib import Path


class FileHistory:
    """Manages file history for recently opened documents."""
    
    def __init__(self, max_items: int = 10):
        """
        Initialize file history manager.
        
        Args:
            max_items: Maximum number of files to keep in history
        """
        self.max_items = max_items
        self.config_dir = Path.home() / ".speed_reader"
        self.config_file = self.config_dir / "file_history.json"
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure the config directory exists."""
        self.config_dir.mkdir(exist_ok=True)
    
    def add_file(self, file_path: str):
        """
        Add a file to the history.
        
        Args:
            file_path: Path to the file to add
        """
        if not file_path or not os.path.exists(file_path):
            return
        
        history = self.get_history()
        
        # Remove if already exists (to move to top)
        if file_path in history:
            history.remove(file_path)
        
        # Add to beginning
        history.insert(0, file_path)
        
        # Limit to max_items
        history = history[:self.max_items]
        
        # Save
        self._save_history(history)
    
    def get_history(self) -> List[str]:
        """
        Get the file history.
        
        Returns:
            List of file paths, most recent first
        """
        if not self.config_file.exists():
            return []
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                history = data.get('history', [])
                # Filter out files that no longer exist
                return [f for f in history if os.path.exists(f)]
        except Exception:
            return []
    
    def get_last_file(self) -> Optional[str]:
        """
        Get the last opened file.
        
        Returns:
            Path to last file, or None if no history
        """
        history = self.get_history()
        return history[0] if history else None
    
    def clear_history(self):
        """Clear all file history."""
        if self.config_file.exists():
            try:
                self.config_file.unlink()
            except Exception:
                pass
    
    def save_position(self, file_path: str, position: int):
        """
        Save reading position for a file.
        
        Args:
            file_path: Path to the file
            position: Word index position
        """
        try:
            data = self._load_data()
            if 'positions' not in data:
                data['positions'] = {}
            data['positions'][file_path] = position
            self._save_data(data)
        except Exception as e:
            print(f"Error saving position: {e}")
    
    def get_position(self, file_path: str) -> Optional[int]:
        """
        Get saved reading position for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Word index position, or None if not found
        """
        try:
            data = self._load_data()
            positions = data.get('positions', {})
            return positions.get(file_path)
        except Exception:
            return None
    
    def _load_data(self) -> dict:
        """Load data from config file."""
        if not self.config_file.exists():
            return {}
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_history(self, history: List[str]):
        """Save history to file."""
        try:
            data = self._load_data()
            data['history'] = history
            data['last_file'] = history[0] if history else None
            self._save_data(data)
        except Exception as e:
            print(f"Error saving file history: {e}")
    
    def _save_data(self, data: dict):
        """Save data to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
