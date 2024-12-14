from data_types import BarData
from typing import List, Optional, TypedDict
from toolbox.tool_base import ToolBase
import plotly.graph_objects as go

# Ichimoku Constants
LOOKBACK_PERIOD = 50
MIN_POINTS_DISTANCE = LOOKBACK_PERIOD
MAX_POINTS_DISTANCE = 400
MIN_ZONE_SIZE = 5  # min price difference in % between closing prices forming ranges
MAX_ZONE_SIZE = 15  # max price difference in % between closing prices forming ranges


class IchimokuData(TypedDict):
    tenkan_sen: Optional[float]
    kijun_sen: Optional[float]
    senkou_span_a: Optional[float]
    senkou_span_b: Optional[float]
    chikou_span: Optional[float]


class Ichimoku(ToolBase):
    def get_latest_data(self, bars):
        return super().get_latest_data(bars)

    def get_historical_data(self, bars: List[BarData]) -> List[IchimokuData]:
        def calculate_high_low_average(data, period):
            if len(data) < period:
                return None
            highest_high = max(bar['high'] for bar in data[-period:])
            lowest_low = min(bar['low'] for bar in data[-period:])
            return (highest_high + lowest_low) / 2

        ichimoku_data = []

        for i in range(len(bars)):
            # Calculate Tenkan-sen (9-period)
            tenkan_sen = calculate_high_low_average(bars[:i + 1], 9)

            # Calculate Kijun-sen (26-period)
            kijun_sen = calculate_high_low_average(bars[:i + 1], 26)

            # Calculate Senkou Span A (26-period projection)
            if tenkan_sen is not None and kijun_sen is not None:
                senkou_span_a = (tenkan_sen + kijun_sen) / 2
            else:
                senkou_span_a = None

            # Calculate Senkou Span B (52-period projection)
            senkou_span_b = calculate_high_low_average(bars[:i + 1], 52)

            # Calculate Chikou Span (26-period lagging)
            chikou_span = bars[i - 26]['close'] if i >= 26 else None

            ichimoku_data.append({
                "tenkan_sen": tenkan_sen,
                "kijun_sen": kijun_sen,
                "senkou_span_a": senkou_span_a,
                "senkou_span_b": senkou_span_b,
                "chikou_span": chikou_span,
            })

        return ichimoku_data

    def add_to_fig(self, fig, bars, data_type="Historical"):
        # Get the pre-calculated data
        if data_type == "Historical":
            ichimoku_data = self.get_historical_data(bars)
        elif data_type == "Latest":
            ichimoku_data = self.get_latest_data(bars)
        else:
            ichimoku_data = data_type  # Assume data is already pre-calculated
            # Add Tenkan-sen (Conversion Line)
        timestamps = [bar['timestamp'] for bar in bars]
        tenkan_sen = [data['tenkan_sen'] for data in ichimoku_data]
        kijun_sen = [data['kijun_sen'] for data in ichimoku_data]
        senkou_span_a = [data['senkou_span_a'] for data in ichimoku_data]
        senkou_span_b = [data['senkou_span_b'] for data in ichimoku_data]
        chikou_span = [data['chikou_span'] for data in ichimoku_data]
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=tenkan_sen,
            mode='lines',
            name='Tenkan-sen',
            line=dict(color='blue', width=2)
        ))
        # Add Kijun-sen (Base Line)
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=kijun_sen,
            mode='lines',
            name='Kijun-sen',
            line=dict(color='red', width=2)
        ))

        # Add Senkou Span A (Leading Span A)
        future_timestamps = timestamps[26:] + [None] * 26
        fig.add_trace(go.Scatter(
            x=future_timestamps,
            y=senkou_span_a,
            mode='lines',
            name='Senkou Span A',
            line=dict(color='green', width=2)
        ))

        # Add Senkou Span B (Leading Span B)
        fig.add_trace(go.Scatter(
            x=future_timestamps,
            y=senkou_span_b,
            mode='lines',
            name='Senkou Span B',
            line=dict(color='orange', width=2)
        ))

        # Add Cloud (Fill between Senkou Span A and B)
        fig.add_trace(go.Scatter(
            x=future_timestamps + future_timestamps[::-1],
            y=senkou_span_a + senkou_span_b[::-1],
            fill='toself',
            # Semi-transparent fill for cloud
            fillcolor='rgba(128, 128, 255, 0.2)',
            line=dict(width=0),
            name='Cloud'
        ))

        # Add Chikou Span (Lagging Span)
        chikou_timestamps = [None] * 26 + timestamps[:-26]
        fig.add_trace(go.Scatter(
            x=chikou_timestamps,
            y=chikou_span,
            mode='lines',
            name='Chikou Span',
            line=dict(color='purple', width=1, dash='dot')
        ))

    def get_nr_of_subplots(self):
        return 0
