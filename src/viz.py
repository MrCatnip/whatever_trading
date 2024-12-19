from data_types import BarData
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List
from toolbox import FibonacciRetracement, MARibbon, Range, Ichimoku, VolumeProfile, ToolName


def __get__tool(tool_name: ToolName):
    if (tool_name == 'Range'):
        return Range()
    elif (tool_name == "Ichimoku"):
        return Ichimoku()
    elif (tool_name == "FibonacciRetracement"):
        return FibonacciRetracement()
    elif (tool_name == "MARibbon"):
        return MARibbon()
    elif (tool_name == "VolumeProfile"):
        return VolumeProfile()
    else:
        raise ValueError(f"Invalid tool name: {tool_name}")


def look_at_this_graph(bars: List[BarData], symbol, timeframe, tool_names: List[ToolName]):
    # Extract data for plotting
    timestamps = [bar['timestamp'] for bar in bars]
    opens = [bar['open'] for bar in bars]
    highs = [bar['high'] for bar in bars]
    lows = [bar['low'] for bar in bars]
    closes = [bar['close'] for bar in bars]

    subplot_count = 1
    for tool_name in tool_names:
        tool = __get__tool(tool_name)
        subplot_count += tool.get_nr_of_subplots()

    fig = make_subplots(rows=subplot_count, cols=1,
                        shared_xaxes=True, vertical_spacing=0.05)

    fig.add_trace(
        go.Candlestick(
            x=timestamps,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            name=f"{symbol} {timeframe}"
        ),
        row=1, col=1
    )

    for tool_name in tool_names:
        tool = __get__tool(tool_name)
        tool.add_to_fig(fig, bars)

    # Update layout for better visualization
    fig.update_layout(
        title=f"{symbol} {timeframe}",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
    )

    # Show the plot
    fig.show()
