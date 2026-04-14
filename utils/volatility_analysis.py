"""
Volatility analysis for IDX markets using GARCH models
"""

import pandas as pd
import numpy as np
from arch import arch_model
import warnings
warnings.filterwarnings('ignore')

class VolatilityAnalyzer:
    """Analyzes volatility regimes in financial time series"""
    
    @staticmethod
    def garch_volatility_analysis(data_dict):
        """
        Perform GARCH analysis on selected tickers
        
        Args:
            data_dict (dict): Dictionary of ticker DataFrames
            
        Returns:
            dict: Analysis results for each ticker
        """
        results = {}
        
        print("Performing GARCH volatility analysis...")
        
        for ticker, df in data_dict.items():
            if not df.empty:
                try:
                    # Calculate log returns
                    returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
                    
                    if len(returns) < 20:  # Need minimum observations
                        print(f"  Insufficient data for GARCH on {ticker}")
                        results[ticker] = None
                        continue
                        
                    # Fit GARCH model (GARCH(1,1))
                    model = arch_model(returns * 100, vol='Garch', p=1, q=1)
                    fitted_model = model.fit(disp='off')
                    
                    # Extract volatility estimates
                    conditional_volatility = fitted_model.conditional_volatility
                    
                    results[ticker] = {
                        'model': None,  # Don't serialize the full model object
                        'volatility_series': [float(x) for x in conditional_volatility],
                        'avg_volatility': float(conditional_volatility.mean()),
                        'max_volatility': float(conditional_volatility.max()),
                        'min_volatility': float(conditional_volatility.min())
                    }
                    
                    print(f"  ✓ GARCH analysis completed for {ticker}")
                    
                except Exception as e:
                    print(f"  ✗ GARCH modeling failed for {ticker}: {e}")
                    results[ticker] = None
            else:
                print(f"  No data available for {ticker}")
                results[ticker] = None
        
        return results
    
    @staticmethod
    def calculate_correlation_matrix(data_dict):
        """
        Create correlation matrix for selected tickers
        
        Args:
            data_dict (dict): Dictionary of ticker DataFrames
            
        Returns:
            DataFrame: Correlation matrix
        """
        # Extract close prices from all dataframes
        close_prices = pd.DataFrame()
        
        for ticker, df in data_dict.items():
            if not df.empty and 'Close' in df.columns:
                close_prices[ticker] = df['Close']
        
        if close_prices.empty:
            return pd.DataFrame()
            
        # Calculate correlations (convert to float)
        corr_matrix = close_prices.corr(method='pearson')
        corr_matrix = corr_matrix.astype(float)  # Ensure all values are Python floats
        
        print("Correlation matrix calculated successfully")
        return corr_matrix
