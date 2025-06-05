from typing import List, Dict, Any
import pandas as pd

class DataAnalyzer:
    @staticmethod
    def officials_to_dataframe(officials: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert officials list to pandas DataFrame"""
        return pd.DataFrame(officials)
    
    @staticmethod
    def count_by_party(df: pd.DataFrame) -> pd.DataFrame:
        """Count officials by political party"""
        return df['party'].value_counts().reset_index().rename(
            columns={'index': 'party', 'party': 'count'}
        )
    
    @staticmethod
    def officials_by_designation(df: pd.DataFrame) -> pd.DataFrame:
        """Group officials by their designation"""
        return df.groupby('designation').size().reset_index(name='count')
    
    @staticmethod
    def extract_social_media(df: pd.DataFrame) -> pd.DataFrame:
        """Extract social media information into separate columns"""
        # Expand social media data
        social_df = df['social_media'].apply(
            lambda x: pd.Series(x) if isinstance(x, dict) else pd.Series()
        )
        return pd.concat([df, social_df], axis=1)