from typing import List, Tuple, Optional
from toolbox.tool_base import ToolBase
import plotly.graph_objects as go

MA_PERIODS = [10, 20, 30]
MA_PERIODS.sort()


class MARibbon(ToolBase):
    def get_latest_data(self, bars):
        return super().get_latest_data(bars)

    # Define the function to calculate moving averages
    def get_historical_data(self, bars) -> Tuple[List[List[Optional[float]]], List[int]]:
        ma_data: List[List[Optional[float]]] = [[]
                                                # Initialize a list for each MA period
                                                for _ in MA_PERIODS]

        # Iterate over each MA period
        for period_idx, period in enumerate(MA_PERIODS):
            for i in range(len(bars)):
                if i + 1 < period:  # Not enough data for this period
                    ma_data[period_idx].append(None)
                else:
                    # Calculate the average close price over the period
                    window = bars[i + 1 - period:i + 1]
                    average = sum(bar['close'] for bar in window) / period
                    ma_data[period_idx].append(average)

        return ma_data, MA_PERIODS

    def add_to_fig(self, fig, bars, data_type="Historical"):
        if data_type == "Historical":
            ma_data, MA_PERIODS = self.get_historical_data(bars)
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
                name=f'MA {MA_PERIODS[idx]}',
                line=dict(width=2),
                fill='tonexty' if idx > 0 else None,  # Fill between traces
                # Customize fill color
                fillcolor=f'rgba({255 - (idx * 50)}, {100 + \
                                                      (idx * 50)}, {255 - (idx * 30)}, 0.3)'
            ))

    def get_nr_of_subplots(self):
        return 0
