from data_types import TimeframeString
from typing import List
from toolbox import ToolName

TIMEFRAMES: List[TimeframeString] = [
    # "1M", "1W", "1D", "4H", "1H", "30m", "15m", "1m"
    "1D"
]
TICKERS = ["BTC"]
LOOKBACK_PERIOD = 20000
TOOL_NAMES: List[ToolName] = ['Range', 'Ichimoku',
                              'FibonacciRetracement', 'MARibbon', "VolumeProfile", 'Range']
