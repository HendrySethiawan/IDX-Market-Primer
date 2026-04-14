"""
Configuration settings for IDX Market Primer project
"""

import os
from datetime import datetime, timedelta

# Market Settings
IDX_MARKET = {
    'trading_hours': {
        'Monday': '09:00 - 12:00 & 13:30 - 15:49',
        'Tuesday': '09:00 - 12:00 & 13:30 - 15:49', 
        'Wednesday': '09:00 - 12:00 & 13:30 - 15:49',
        'Thursday': '09:00 - 12:00 & 13:30 - 15:49',
        'Friday': '09:00 - 12:00 (shortened)'
    },
    'settlement_period': 'T+2',
    'lot_size': 100,
    'time_zone': 'Asia/Jakarta'
}

# Key Tickers and Sectors
KEY_TICKERS = {
    'BBCA.JK': 'Bank Central Asia',
    'TLKM.JK': 'Telkomsel',
    'ASII.JK': 'Astra International',
    '^JKSE': 'Jakarta Composite Index'
}

SECTOR_WEIGHTS = {
    'Financial Services': 40,
    'Industrials': 15,
    'Consumer Goods': 12,
    'Utilities': 8,
    'Healthcare': 6,
    'Energy': 7,
    'Telecommunications': 5,
    'Materials': 3,
    'Real Estate': 4
}

# Data Quality Settings
DATA_QUALITY = {
    'gap_handling_method': 'forward_fill + interpolation',
    'missing_threshold': 0.05,  # 5% missing data acceptable
    'correlation_min_samples': 10
}

# Time Periods
DEFAULT_TIME_PERIODS = {
    'short_term': '3mo',
    'medium_term': '1y', 
    'long_term': '2y'
}
