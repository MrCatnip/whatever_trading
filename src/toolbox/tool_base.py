from data_types import BarData
from typing import List
from abc import ABC, abstractmethod
from plotly.graph_objects import Figure

class ToolBase(ABC):
    @abstractmethod
    def get_latest_data(self, bars: List[BarData]):
        """Retrieve the latest data."""
        pass

    @abstractmethod
    def get_historical_data(self, bars: List[BarData]):
        """Retrieve historical data."""
        pass

    @abstractmethod
    def get_historical_data(self, bars: List[BarData]):
        """Retrieve historical data."""
        pass