"""
Data management for IDX market analysis
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class IDXMarketData:
    """Handles data fetching and processing for IDX markets"""
    
    def __init__(self):
        self.tickers = None
        
    def fetch_ticker_data(self, tickers_dict, period="2y"):
        """Fetch historical data from Yahoo Finance for IDX tickers"""
        data = {}
        failed_tickers = []
        
        print("Fetching data for IDX assets...")
        
        for ticker, name in tickers_dict.items():
            try:
                print(f"  Fetching {name} ({ticker})...")
                df = yf.download(ticker, period=period, auto_adjust=True)
                
                if not df.empty:
                    df['Name'] = name
                    df['Ticker'] = ticker
                    
                    if not isinstance(df.index, pd.DatetimeIndex):
                        df.index = pd.to_datetime(df.index)
                        
                    data[ticker] = df
                    print(f"    ✓ Successfully fetched {len(df)} records")
                else:
                    failed_tickers.append((ticker, name))
                    print(f"    ✗ No data found for {name}")
                    
            except Exception as e:
                failed_tickers.append((ticker, name))
                print(f"    ✗ Error fetching {name}: {str(e)}")
        
        if failed_tickers:
            print(f"\nFailed to fetch data for: {[f'{t[1]} ({t[0]})' for t in failed_tickers]}")
            
        return data
    
    def calculate_metrics(self, data_dict):
        """Calculate key market metrics"""
        df_list = []
        
        for ticker, df in data_dict.items():
            if df.empty:
                continue
                
            try:
                # 🔑 FIX: Use .squeeze() to convert 1-col DataFrames to 1D Series
                close_prices = df['Close'].squeeze()
                volume_series = df['Volume'].squeeze()
                
                if len(close_prices) < 2:
                    continue
                    
                returns_series = close_prices.pct_change().dropna()
                
                # Calculate metrics (will be scalars when input is a Series)
                vol_raw = returns_series.std() * np.sqrt(252)
                mean_ret_raw = returns_series.mean()
                
                # 🔑 Safely convert to float (handles both scalars and 1-element Series)
                volatility = float(vol_raw) if not isinstance(vol_raw, pd.Series) else float(vol_raw.iloc[0])
                annualized_return = float(mean_ret_raw * 252) if not isinstance(mean_ret_raw, pd.Series) else float((mean_ret_raw * 252).iloc[0])
                
                # Price change
                price_change = float((close_prices.iloc[-1] / close_prices.iloc[0] - 1) * 100)
                
                summary_row = {
                    'Ticker': str(ticker),
                    'Name': str(df['Name'].iloc[0]) if 'Name' in df.columns else str(ticker),
                    'Start_Date': str(df.index.min()),
                    'End_Date': str(df.index.max()),
                    'Price_Change_%': price_change,
                    'Annualized_Return': annualized_return,
                    'Annualized_Volatility': volatility,
                    'Max_Drawdown': self.calculate_max_drawdown(close_prices),
                    'Volume_Avg': float(volume_series.mean())
                }
                
                # Replace any NaN metrics with 0.0
                for key, value in summary_row.items():
                    if isinstance(value, (float, np.float64)) and pd.isna(value):
                        summary_row[key] = 0.0
                        
                df_list.append(summary_row)
                
            except Exception as e:
                print(f"Error calculating metrics for {ticker}: {str(e)}")
                # Fallback row
                try:
                    df_list.append({
                        'Ticker': str(ticker),
                        'Name': str(df['Name'].iloc[0]) if 'Name' in df.columns else str(ticker),
                        'Start_Date': str(df.index.min()),
                        'End_Date': str(df.index.max()),
                        'Price_Change_%': 0.0,
                        'Annualized_Return': 0.0,
                        'Annualized_Volatility': 0.0,
                        'Max_Drawdown': 0.0,
                        'Volume_Avg': 0.0
                    })
                except Exception as e2:
                    print(f"Error in fallback for {ticker}: {str(e2)}")
                continue
        
        try:
            return pd.DataFrame(df_list)
        except Exception as e:
            print(f"Error creating DataFrame: {e}")
            return pd.DataFrame()
    
    def calculate_max_drawdown(self, prices):
        """Calculate maximum drawdown from price series"""
        try:
            if len(prices) < 2:
                return 0.0
                
            cumulative = prices / prices.iloc[0]
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return float(drawdown.min())
        except Exception:
            return 0.0
    
    def get_lq45_list(self):
        """Return LQ45 companies list"""
        return [
            'BBCA.JK', 'TLKM.JK', 'ASII.JK', 'UNVR.JK',
            'SIDO.JK', 'SMGR.JK', 'BMRI.JK', 'WSKT.JK'
        ]
