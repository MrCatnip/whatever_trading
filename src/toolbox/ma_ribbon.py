from typing import List, Tuple, Optional
from toolbox.tool_base import ToolBase
import plotly.graph_objects as go
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MARibbonConfig:
    periods: List[int] = field(default_factory=lambda: [5, 20, 40, 50, 100, 200])


class MARibbon(ToolBase):
    def __init__(self, config: Optional[MARibbonConfig] = None):
        # Default configuration if none is provided
        default_config = MARibbonConfig()

        # Extract configuration values, falling back to defaults where necessary
        config = config or default_config

        self.periods = config.periods or default_config.periods
        self.periods.sort()
        self.data: Tuple[List[List[Optional[float]]], List[int]] = []

    def get_latest_data(self, bars):
        return super().get_latest_data(bars)

    # Define the function to calculate moving averages
    def calculate_historical_data(self, bars) -> Tuple[List[List[Optional[float]]], List[int]]:
        ma_data: List[List[Optional[float]]] = [[]
                                                # Initialize a list for each MA period
                                                for _ in self.periods]

        # Iterate over each MA period
        for period_idx, period in enumerate(self.periods):
            for i in range(len(bars)):
                if i + 1 < period:  # Not enough data for this period
                    ma_data[period_idx].append(None)
                else:
                    # Calculate the average close price over the period
                    window = bars[i + 1 - period:i + 1]
                    average = sum(bar['close'] for bar in window) / period
                    ma_data[period_idx].append(average)
        self.data = ma_data, self.periods
        return self.data

    def add_to_fig(self, fig, bars, data_type="Historical"):
        if data_type == "Historical":
            ma_data, self.periods = self.calculate_historical_data(bars)
        elif data_type == "Latest":
            ma_data = self.get_latest_data(bars)
        else:
            ma_data = data_type

        timestamps = [bar['timestamp'] for bar in bars]

        # Plot the MA ribbons
        for idx, ma in enumerate(ma_data):
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=ma,
                mode='lines',
                name=f'MA {self.periods[idx]}',
                line=dict(width=2),
                fill='tonexty' if idx > 0 else None,  # Fill between traces
                # Customize fill color
                fillcolor=f'rgba({255 - (idx * 50)}, {100 + \
                                                      (idx * 50)}, {255 - (idx * 30)}, 0.3)'
            ))

    def get_nr_of_subplots(self):
        return 0
