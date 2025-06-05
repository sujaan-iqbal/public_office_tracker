import json
from pathlib import Path
from typing import Dict, List, Any

class DataLoader:
    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """Load JSON data from file"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: str) -> None:
        """Save data to JSON file"""
        path = Path(file_path)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def get_officials(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract officials list from loaded data"""
        return data.get('officials', [])