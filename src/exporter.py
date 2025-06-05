from typing import List, Dict, Any
import csv
import json
from pathlib import Path

class DataExporter:
    @staticmethod
    def export_to_csv(officials: List[Dict[str, Any]], file_path: str) -> None:
        """Export officials data to CSV file"""
        if not officials:
            raise ValueError("No officials data to export")
        
        # Flatten nested structures
        flattened = []
        for official in officials:
            flat_official = official.copy()
            
            # Flatten social media
            if 'social_media' in flat_official:
                for platform, handle in flat_official['social_media'].items():
                    flat_official[f'social_{platform}'] = handle
                del flat_official['social_media']
            
            # Flatten contact
            if 'contact' in flat_official:
                for method, value in flat_official['contact'].items():
                    flat_official[f'contact_{method}'] = value
                del flat_official['contact']
            
            flattened.append(flat_official)
        
        # Get all possible fieldnames
        fieldnames = set()
        for record in flattened:
            fieldnames.update(record.keys())
        
        # Write to CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(flattened)
    
    @staticmethod
    def export_to_json(officials: List[Dict[str, Any]], file_path: str) -> None:
        """Export officials data to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({"officials": officials}, f, indent=2)