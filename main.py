import argparse
from pathlib import Path
from src.data_loader import DataLoader
from src.validator import DataValidator
from src.analyzer import DataAnalyzer
from src.exporter import DataExporter
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Public Office Data Tracker")
    parser.add_argument('--input', type=str, default='data/officials.json', 
                       help='Input JSON file with officials data')
    parser.add_argument('--schema', type=str, default='data/schema.json',
                       help='JSON schema file for validation')
    parser.add_argument('--export-csv', type=str, 
                       help='Export data to CSV file')
    parser.add_argument('--export-json', type=str,
                       help='Export data to JSON file')
    parser.add_argument('--analyze', action='store_true',
                       help='Show analysis of the data')
    
    args = parser.parse_args()
    
    # Load and validate data
    try:
        data = DataLoader.load_json(args.input)
        validator = DataValidator(args.schema)
        
        if validator.validate_data(data):
            print("✅ Data validation successful")
        else:
            print("❌ Data validation failed")
            return
        
        officials = DataLoader.get_officials(data)
        
        # Export if requested
        if args.export_csv:
            DataExporter.export_to_csv(officials, args.export_csv)
            print(f"📊 Data exported to CSV: {args.export_csv}")
        
        if args.export_json:
            DataExporter.export_to_json(officials, args.export_json)
            print(f"📄 Data exported to JSON: {args.export_json}")
        
        # Analyze if requested
        if args.analyze:
            analyzer = DataAnalyzer()
            df = analyzer.officials_to_dataframe(officials)
            
            print("\n=== Basic Analysis ===")
            print(f"Total officials: {len(df)}")
            
            party_counts = analyzer.count_by_party(df)
            print("\nOfficials by party:")
            print(party_counts.to_string(index=False))
            
            designation_counts = analyzer.officials_by_designation(df)
            print("\nOfficials by designation:")
            print(designation_counts.to_string(index=False))
            
            df_with_social = analyzer.extract_social_media(df)
            print("\nSocial media presence:")
            social_cols = [col for col in df_with_social.columns if col in ['twitter', 'facebook', 'instagram']]
            print(df_with_social[['name'] + social_cols].to_string(index=False))
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()