from data_types import BarData
from typing import List
from toolbox.tool_base import ToolBase
import plotly.graph_objects as go

FIB_LEVELS = [0, 23.6, 38.2, 50, 61.8, 78.6, 100]


class FibonacciRetracement(ToolBase):
    def get_latest_data(self, bars):
        return super().get_latest_data(bars)

    def get_historical_data(self, bars: List[BarData]) -> List[float]:
        max_close = max(bars, key=lambda bar: bar["close"])["close"]
        min_close = min(bars, key=lambda bar: bar['close'])["close"]
        fib_difference = max_close - min_close
        fib_array = []
        for level in FIB_LEVELS:
            fib_array.append(min_close + level / 100 * fib_difference)
        return fib_array

    def add_to_fig(self, fig, bars, data_type="Historical"):
        if data_type == "Historical":
            fib_array = self.get_historical_data(bars)
        elif data_type == "Latest":
            fib_array = self.get_latest_data(bars)
        else:
            fib_array = data_type
        timestamps = [bar['timestamp'] for bar in bars]
        # Add Fibonacci levels to the figure
        i = 0
        for level in fib_array:
            fig.add_trace(
                go.Scatter(
                    x=[timestamps[0], timestamps[-1]],
                    y=[level, level],
                    mode="lines",
                    line=dict(dash="dash", color="gray"),
                    name=f"Fib {FIB_LEVELS[i]}%",
                )
            )
            i += 1

    def get_nr_of_subplots(self):
        return 0
