from typing import TypedDict


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