from data_types import BarData
from typing import List, Literal, Union
from abc import ABC, abstractmethod
import plotly.graph_objects as go

DataType = Union[Literal["Latest", "Historical"], List]


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
    def add_to_fig(self, fig: go.Figure, bars: List[BarData], data_type: DataType = "Historical"):
        """Add the stuff to the figure."""
        pass

    @abstractmethod
    def get_nr_of_subplots(self) -> int:
        """Returns number of expected subplots"""
        pass
