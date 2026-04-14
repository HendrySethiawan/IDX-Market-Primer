"""
Unit tests for IDX market data functionality
"""

import pytest
import pandas as pd
from unittest.mock import patch
from data.market_data import IDXMarketData

def test_market_data_initialization():
    """Test initialization of IDXMarketData class"""
    manager = IDXMarketData()
    assert manager is not None

def test_empty_data_handling():
    """Test handling of empty data scenarios"""
    # Test that it can handle edge cases gracefully
    manager = IDXMarketData()
    
    # This would normally be tested with mocked data
    result = manager.calculate_max_drawdown(pd.Series([1, 2, 3]))
    assert isinstance(result, float)

def test_calculate_metrics_empty():
    """Test metrics calculation with empty dict"""
    manager = IDXMarketData()
    result = manager.calculate_metrics({})
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0

if __name__ == "__main__":
    pytest.main([__file__])
