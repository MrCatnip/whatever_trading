from typing import TypedDict, Literal


class BarData(TypedDict):
    timestamp: str  # ISO 8601 format string
    open: float
    high: float
    low: float
    close: float
    volume: float

class Range(TypedDict):
    breach_price: float
    entry_price: float
    starting_index: int
    ending_index: int
    validated_index: int

TimeframeString = Literal["1m", "15m", "30m", "1H", "4H", "1D", "1W", "1M"]
