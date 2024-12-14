import click
from alpaca_interface import AlpacaInterface
from viz import look_at_this_graph
import json
from data_types import BarData, TimeframeString, ToolName
from typing import List
import os

TIMEFRAMES: List[TimeframeString] = [
    # "1M", "1W", "1D", "4H", "1H", "30m", "15m", "1m"
    "1D"
]
TICKERS = ["BTC"]
LOOKBACK_PERIOD = 20000
TOOL_NAMES: List[ToolName] = ['Range', 'Ichimoku', 'FibonacciRetracement']

@click.group()
def cli():
    """Wusup"""
    pass


@cli.command()
def fetchall():
    for ticker in TICKERS:
        symbol = get_symbol(ticker)
        for timeframe in TIMEFRAMES:
            print(f'Fetching for {symbol} - {timeframe}...')
            client = AlpacaInterface(symbol, timeframe)
            bars = client.fetch()
            file_name = get_file_name(ticker, timeframe)
            with open(file_name, "w") as file:
                json.dump([bar for bar in bars], file, indent=4)
            print('Done!')


@cli.command()
def plot():
    for ticker in TICKERS:
        ticker = "BTC"
        symbol = get_symbol(ticker)
        for timeframe in TIMEFRAMES:
            print(f"Parsing data for {symbol} - {timeframe}...")
            file_name = get_file_name(ticker, timeframe)
            with open(file_name, "r") as file:
                bars: List[BarData] = json.load(file)
                bars = bars[-min(LOOKBACK_PERIOD, len(bars)):]
                look_at_this_graph(bars, symbol, timeframe, TOOL_NAMES)
                print('Done!')


def get_symbol(ticker):
    return f"{ticker}/USD"


def get_file_name(ticker: str, timeframe: TimeframeString):
    dirname = "AlpacaData"
    os.makedirs(dirname, exist_ok=True)
    timeframe = timeframe if '1m' not in timeframe else '1min'
    return f"{dirname}/{ticker}-{timeframe}.json"


if __name__ == '__main__':
    cli()
