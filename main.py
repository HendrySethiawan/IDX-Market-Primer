"""
Main execution script for IDX Market Primer
"""

import sys
import os
from datetime import datetime
import json
import logging
import numpy as np
import pandas as pd
from config.settings import *
from data.market_data import IDXMarketData
from utils.volatility_analysis import VolatilityAnalyzer
from utils.data_quality import DataQualityManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('idx_market_primer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_directory_structure():
    """Create necessary directory structure"""
    directories = ['data', 'logs', 'reports']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

def run_market_analysis():
    """
    Main execution function for market analysis
    """
    logger.info("Starting IDX Market Primer Analysis")
    
    # Create directory structure
    create_directory_structure()
    
    try:
        # Initialize data manager
        data_manager = IDXMarketData()
        
        # Fetch data
        logger.info("Fetching historical data...")
        idx_data = data_manager.fetch_ticker_data(KEY_TICKERS, period="2y")
        
        if not idx_data:
            logger.error("No data fetched. Exiting.")
            return
        
        # Calculate metrics
        logger.info("Calculating market metrics...")
        summary_df = data_manager.calculate_metrics(idx_data)
        
        # Save summary to CSV
        output_file = 'reports/market_summary.csv'
        summary_df.to_csv(output_file, index=False)
        logger.info(f"Market summary saved to {output_file}")
        
        # Perform volatility analysis
        logger.info("Performing GARCH volatility analysis...")
        garch_results = VolatilityAnalyzer.garch_volatility_analysis(idx_data)
        
        # Create correlation matrix
        logger.info("Calculating correlation matrix...")
        corr_matrix = VolatilityAnalyzer.calculate_correlation_matrix(idx_data)
        
        # Save correlation matrix
        if not corr_matrix.empty:
            corr_file = 'reports/correlation_matrix.csv'
            corr_matrix.to_csv(corr_file)
            logger.info(f"Correlation matrix saved to {corr_file}")
            
        # Data quality assessment
        logger.info("Assessing data quality...")
        quality_report = DataQualityManager.quality_report(idx_data)
        
        # Save quality report - FIXED: Convert numpy types to Python native types
        quality_file = 'reports/data_quality.json'
        # Convert any numpy types to Python native types for JSON serialization
        safe_quality_report = {}
        for key, value in quality_report.items():
            if isinstance(value, dict):
                safe_value = {}
                for k, v in value.items():
                    if isinstance(v, (np.integer, np.floating)):
                        safe_value[k] = float(v)
                    else:
                        safe_value[k] = v
                safe_quality_report[key] = safe_value
            else:
                safe_quality_report[key] = value
                
        with open(quality_file, 'w') as f:
            json.dump(safe_quality_report, f, indent=2)
        logger.info(f"Data quality report saved to {quality_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("IDX MARKET PRIMER - ANALYSIS COMPLETE")
        print("="*60)
        
        if not summary_df.empty:
            print("\nMarket Summary:")
            for _, row in summary_df.iterrows():
                print(f"{row['Name']} ({row['Ticker']}):")
                print(f"  Return: {row['Annualized_Return']:.2f}% | Volatility: {row['Annualized_Volatility']:.3f}")
        
        print("\nKey Results:")
        for ticker, result in garch_results.items():
            if result:
                print(f"{ticker} - Avg Volatility: {result['avg_volatility']:.4f}")
        
        # Save comprehensive report
        generate_comprehensive_report(summary_df, garch_results, corr_matrix)
        
        logger.info("Analysis completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

def generate_comprehensive_report(summary_df, garch_results, correlation_matrix):
    """
    Generate comprehensive markdown report
    """
    try:
        # Convert DataFrame to dictionary for JSON serialization
        summary_dict = {}
        if not summary_df.empty:
            summary_dict = summary_df.to_dict('records')
        
        # Create clean string representations of the results  
        garch_str_results = []
        for ticker, result in garch_results.items():
            if result:
                garch_str_results.append({
                    'ticker': ticker,
                    'avg_volatility': f"{result['avg_volatility']:.4f}"
                })
        
        report_content = f"""
# IDX Market Analysis Report

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Market Structure Overview

- Trading Hours: {IDX_MARKET['trading_hours']}
- Settlement Period: {IDX_MARKET['settlement_period']}  
- Lot Size: {IDX_MARKET['lot_size']} shares
- Time Zone: {IDX_MARKET['time_zone']}

## Key Asset Performance

"""

        # Add asset performance data (handle potential NaN)
        for row in summary_dict:
            try:
                report_content += f"- **{row.get('Name', 'Unknown')}** ({row.get('Ticker', 'N/A')}): "
                price_change = row.get('Price_Change_%', 0.0)
                volatility = row.get('Annualized_Volatility', 0.0)
                report_content += f"{price_change:.2f}% change, "
                report_content += f"Volatility: {volatility:.3f}\n"
            except:
                continue
            
        report_content += "\n## Sector Analysis\n"

        for sector, weight in SECTOR_WEIGHTS.items():
            report_content += f"- {sector}: {weight}% of market\n"

        # Add GARCH results
        report_content += "\n## Volatility Analysis Results\n"
        
        if garch_results:
            for ticker, result in garch_results.items():
                if result:
                    report_content += f"- {ticker}: Avg Volatility = {result['avg_volatility']:.4f}\n"

        # Add correlation matrix
        if not correlation_matrix.empty:
            report_content += "\n## Correlation Matrix\n"
            report_content += "Correlations between key assets:\n"
            
            # Handle any potential issues with the correlation matrix
            try:
                for col in correlation_matrix.columns:
                    row_str = f"{col}: "
                    for idx in correlation_matrix.index:
                        if idx != col and not pd.isna(correlation_matrix.loc[idx, col]):
                            val = float(correlation_matrix.loc[idx, col])
                            row_str += f"{idx}={val:.3f}, "
                    report_content += row_str.rstrip(", ") + "\n"
            except Exception as e:
                logger.warning(f"Error in correlation matrix formatting: {e}")

        # Save to file
        with open('reports/idx_market_analysis.md', 'w') as f:
            f.write(report_content)
            
        logger.info("Comprehensive markdown report saved")
        
    except Exception as e:
        logger.error(f"Error generating comprehensive report: {str(e)}")

if __name__ == "__main__":
    run_market_analysis()
