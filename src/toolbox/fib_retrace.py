from typing import List, Optional
from toolbox.tool_base import ToolBase
import plotly.graph_objects as go
from dataclasses import dataclass, field
from data_types import BarData


@dataclass
class FibonacciRetracementConfig:
    # % from lowest point to highest point
    levels: List[float] = field(default_factory=lambda: [
                                0, 23.6, 38.2, 50, 61.8, 78.6, 100])
    # buffer % wise from key level
    zone: float = 2


class FibonacciRetracement(ToolBase):
    def __init__(self, config: Optional[FibonacciRetracementConfig] = None):
        # Default configuration if none is provided
        default_config = FibonacciRetracementConfig()

        # Extract configuration values, falling back to defaults where necessary
        config = config or default_config

        self.levels = config.levels or default_config.levels
        self.levels.sort()
        self.zone = config.zone or default_config.zone
        self.fib_levels: List[float] = []
        self.data: List[bool] = []

    def get_latest_data(self, bars):
        return super().get_latest_data(bars)

    def calculate_historical_data(self, bars):
        max_close = max(bars, key=lambda bar: bar["close"])["close"]
        min_close = min(bars, key=lambda bar: bar['close'])["close"]
        fib_difference = max_close - min_close
        fib_array = []
        for level in self.levels:
            fib_array.append(min_close + level / 100 * fib_difference)
        self.fib_levels = fib_array
        for i in range(0, len(bars)):
            bar = bars[i]
            self.data.append(self.__is_within_level(bar))
        return self.data

    def __is_within_level(self, bar: BarData):
        close = bar["close"]
        for fib_level in self.fib_levels:
            return abs(fib_level - close)/fib_level*100 <= self.zone

    def add_to_fig(self, fig, bars, data_type="Historical"):
        if data_type == "Historical":
            self.calculate_historical_data(bars)
            data = self.fib_levels
        elif data_type == "Latest":
            self.get_latest_data(bars)
            data = self.fib_levels
        else:
            data = data_type
        timestamps = [bar['timestamp'] for bar in bars]
        # Add Fibonacci levels to the figure
        i = 0
        for level in data:
            fig.add_trace(
                go.Scatter(
                    x=[timestamps[0], timestamps[-1]],
                    y=[level, level],
                    mode="lines",
                    line=dict(dash="dash", color="gray"),
                    name=f"Fib {self.levels[i]}%",
                )
            )
            i += 1

    def get_nr_of_subplots(self):
        return 0
