from typing import TypedDict, Literal


class BarData(TypedDict):
    timestamp: str  # ISO 8601 format string
    open: float
    high: float
    low: float
    close: float
    volume: float


TimeframeString = Literal["1m", "15m", "30m", "1H", "4H", "1D", "1W", "1M"]

ToolName = Literal["Range", "Ichimoku", "FibonacciRetracement", "MARibbon"]
