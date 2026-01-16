"""
Data Manager: Centralized JSON storage abstraction layer.

This module provides a clean interface for all data operations, making it easy to:
- Replace JSON storage with a database later
- Ensure atomic file operations
- Centralize data validation
- Maintain data consistency
"""

import json
import os
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime

# File locks to prevent concurrent write conflicts
_file_locks = {
    'users': threading.Lock(),
    'groups': threading.Lock(),
    'contributions': threading.Lock(),
    'loans': threading.Lock(),
    'sessions': threading.Lock()
}


class DataManager:
    """Manages all JSON file operations with thread safety."""
    
    def __init__(self, file_path: str, lock_key: str):
        """
        Initialize data manager for a specific file.
        
        Args:
            file_path: Path to the JSON file
            lock_key: Key for the file lock
        """
        self.file_path = file_path
        self.lock = _file_locks.get(lock_key, threading.Lock())
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create the file and directory if they don't exist."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f)
    
    def read_all(self) -> Dict[str, Any]:
        """
        Read all data from the file.
        
        Returns:
            Dictionary containing all records
        """
        with self.lock:
            try:
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
    
    def write_all(self, data: Dict[str, Any]):
        """
        Write all data to the file (overwrites existing content).
        
        Args:
            data: Dictionary to write
        """
        with self.lock:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a single record by key.
        
        Args:
            key: Record identifier
            
        Returns:
            Record dictionary or None if not found
        """
        data = self.read_all()
        return data.get(key)
    
    def create(self, key: str, value: Dict[str, Any]) -> bool:
        """
        Create a new record.
        
        Args:
            key: Record identifier
            value: Record data
            
        Returns:
            True if created, False if key already exists
        """
        data = self.read_all()
        if key in data:
            return False
        data[key] = value
        self.write_all(data)
        return True
    
    def update(self, key: str, value: Dict[str, Any]) -> bool:
        """
        Update an existing record.
        
        Args:
            key: Record identifier
            value: New record data
            
        Returns:
            True if updated, False if key doesn't exist
        """
        data = self.read_all()
        if key not in data:
            return False
        data[key] = value
        self.write_all(data)
        return True
    
    def upsert(self, key: str, value: Dict[str, Any]):
        """
        Create or update a record.
        
        Args:
            key: Record identifier
            value: Record data
        """
        data = self.read_all()
        data[key] = value
        self.write_all(data)
    
    def delete(self, key: str) -> bool:
        """
        Delete a record.
        
        Args:
            key: Record identifier
            
        Returns:
            True if deleted, False if key doesn't exist
        """
        data = self.read_all()
        if key not in data:
            return False
        del data[key]
        self.write_all(data)
        return True
    
    def filter(self, predicate) -> List[Dict[str, Any]]:
        """
        Filter records based on a predicate function.
        
        Args:
            predicate: Function that takes a record and returns bool
            
        Returns:
            List of matching records
        """
        data = self.read_all()
        return [record for record in data.values() if predicate(record)]
    
    def find(self, predicate) -> Optional[Dict[str, Any]]:
        """
        Find the first record matching a predicate.
        
        Args:
            predicate: Function that takes a record and returns bool
            
        Returns:
            First matching record or None
        """
        data = self.read_all()
        for record in data.values():
            if predicate(record):
                return record
        return None
