from data_types import BarData
from typing import List
from abc import ABC, abstractmethod

class StrategyBase(ABC):
    @abstractmethod
    def get_latest_data(self, bars: List[BarData]):
        """Retrieve the latest signal."""
        pass

    @abstractmethod
    def get_historical_data(self, bars: List[BarData]):
        """Retrieve historical signals."""
        pass