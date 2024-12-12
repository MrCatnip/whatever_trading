from data_types import BarData, Range
import plotly.graph_objects as go
from typing import List


def plot_data(bars: List[BarData], ranges: List[Range]):
    # Extract data for plotting
    timestamps = [bar['timestamp'] for bar in bars]
    opens = [bar['open'] for bar in bars]
    highs = [bar['high'] for bar in bars]
    lows = [bar['low'] for bar in bars]
    closes = [bar['close'] for bar in bars]

    # Create the candlestick chart
    fig = go.Figure(data=[
        go.Candlestick(
            x=timestamps,
            open=opens,
            high=highs,
            low=lows,
            close=closes
        )
    ])

    # Add semi-transparent rectangles for ranges
    for range_item in ranges:
        breach_price = range_item['breach_price']
        entry_price = range_item['entry_price']
        starting_index = range_item['starting_index']
        ending_index = range_item['ending_index']
        validated_index = range_item['validated_index']
        # Determine rectangle color based on breach/entry price comparison
        color = 'rgba(0, 255, 0, 0.2)' if breach_price >= entry_price else 'rgba(255, 0, 0, 0.2)'
        intense_color = 'rgba(0, 255, 0, 0.3)' if breach_price >= entry_price else 'rgba(255, 0, 0, 0.3)'
        even_more_intense_color = 'rgba(0, 48, 143, 0.3)'

        # Add the base rectangle shape
        fig.add_shape(
            type="rect",
            x0=timestamps[starting_index],  # Start time (adjust as needed)
            x1=timestamps[ending_index],  # End time (adjust as needed)
            y0=min(breach_price, entry_price),  # Lower bound of the range
            y1=max(breach_price, entry_price),  # Upper bound of the range
            fillcolor=color,
            line=dict(width=0),  # No border
        )
        # Add the intense rectangle shape
        fig.add_shape(
            type="rect",
            x0=timestamps[ending_index],  # Start from the ending_index
            x1=timestamps[validated_index],  # End at the last timestamp
            y0=min(breach_price, entry_price),  # Lower bound of the range
            y1=max(breach_price, entry_price),  # Upper bound of the range
            fillcolor=intense_color,
            line=dict(width=0),  # No border
        )
        # Add the even more intense rectangle shape
        fig.add_shape(
            type="rect",
            x0=timestamps[validated_index],  # Start from the ending_index
            x1=timestamps[-1],  # End at the last timestamp
            y0=min(breach_price, entry_price),  # Lower bound of the range
            y1=max(breach_price, entry_price),  # Upper bound of the range
            fillcolor=even_more_intense_color,
            line=dict(width=0),  # No border
        )

    # Update layout for better visualization
    fig.update_layout(
        title="Candlestick Chart with Ranges",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
    )

    # Show the plot
    fig.show()
