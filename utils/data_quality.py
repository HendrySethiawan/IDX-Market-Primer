"""
Data quality assessment and handling for emerging markets
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataQualityManager:
    """Manages data quality assessment for financial time series"""
    
    @staticmethod
    def detect_data_gaps(df):
        """
        Detect gaps in trading days
        
        Args:
            df (DataFrame): Time series DataFrame
            
        Returns:
            list: List of gap periods
        """
        if df.empty:
            return []
            
        # Convert index to datetime if needed
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df = df.set_index(pd.to_datetime(df.index))
            except:
                pass
                
        daily_diffs = df.index.to_series().diff().dt.days
        
        gaps = {}
        for idx, diff in daily_diffs.items():
            if diff > 1:
                # This indicates a gap
                gaps[str(idx)] = int(diff)
                
        return gaps
    
    @staticmethod
    def handle_data_gaps(df):
        """
        Handle data gaps using forward fill + interpolation
        
        Args:
            df (DataFrame): Original DataFrame
            
        Returns:
            DataFrame: Cleaned DataFrame with missing values filled
        """
        if df.empty:
            return df
            
        df_filled = df.copy()
        
        # Forward fill and backward fill for missing values
        df_filled.fillna(method='ffill', inplace=True)
        df_filled.fillna(method='bfill', inplace=True)
        
        # Interpolate for any remaining gaps
        numeric_cols = df_filled.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            df_filled[numeric_cols] = df_filled[numeric_cols].interpolate(method='linear')
            
        return df_filled
    
    @staticmethod
    def quality_report(data_dict, min_completeness=0.95):
        """
        Generate comprehensive data quality report
        
        Args:
            data_dict (dict): Dictionary of DataFrames
            min_completeness (float): Minimum acceptable completeness
            
        Returns:
            dict: Quality assessment results
        """
        reports = {}
        
        for ticker, df in data_dict.items():
            if not df.empty:
                # Calculate completeness metrics
                total_rows = len(df)
                missing_rows = df.isnull().sum().sum()
                
                completeness_score = 1 - (missing_rows / (total_rows * len(df.columns)))
                
                # Detect gaps
                gaps = DataQualityManager.detect_data_gaps(df)
                
                reports[ticker] = {
                    'completeness': float(completeness_score),
                    'total_rows': int(total_rows),
                    'missing_values': int(missing_rows),
                    'gap_periods': list(gaps.keys()),
                    'quality_rating': 'Good' if completeness_score >= min_completeness else 'Poor'
                }
                
        return reports
