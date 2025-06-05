from jsonschema import validate, ValidationError
from typing import Dict, List, Any
from pathlib import Path
import json

class DataValidator:
    def __init__(self, schema_file: str):
        self.schema = self._load_schema(schema_file)
    
    def _load_schema(self, schema_file: str) -> Dict[str, Any]:
        """Load JSON schema from file"""
        path = Path(schema_file)
        if not path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data against schema"""
        try:
            validate(instance=data, schema=self.schema)
            return True
        except ValidationError as e:
            print(f"Validation error: {e.message}")
            return False
    
    def validate_official(self, official: Dict[str, Any]) -> bool:
        """Validate a single official against the schema"""
        dummy_data = {"officials": [official]}
        return self.validate_data(dummy_data)