import click
from alpaca_interface import AlpacaInterface
from viz import look_at_this_graph
import json
from data_types import BarData, TimeframeString
from typing import List
from config import LOOKBACK_PERIOD, TICKERS, TIMEFRAMES, TOOL_NAMES
from strategies import Strategy1
import os

TOOL_NAMES = list(dict.fromkeys(TOOL_NAMES))


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
        symbol = get_symbol(ticker)
        for timeframe in TIMEFRAMES:
            print(f"Parsing data for {symbol} - {timeframe}...")
            file_name = get_file_name(ticker, timeframe)
            with open(file_name, "r") as file:
                bars: List[BarData] = json.load(file)
                bars = bars[-min(LOOKBACK_PERIOD, len(bars)):]
                look_at_this_graph(bars, symbol, timeframe, TOOL_NAMES)
                print('Done!')


@cli.command()
def backtest():
    for ticker in TICKERS:
        symbol = get_symbol(ticker)
        low_timeframe: TimeframeString = '15m'
        high_timeframe: TimeframeString = '1H'
        bars_low_timeframe: List[BarData] = []
        bars_high_timeframe: List[BarData] = []
        file_name = get_file_name(ticker, low_timeframe)
        with open(file_name, "r") as file:
            bars_low_timeframe = json.load(file)
        file_name = get_file_name(ticker, high_timeframe)
        with open(file_name, "r") as file:
            bars_high_timeframe = json.load(file)
        strategy = Strategy1()
        strategy.backtest(bars_low_timeframe, bars_high_timeframe)

def get_symbol(ticker):
    return f"{ticker}/USD"


def get_file_name(ticker: str, timeframe: TimeframeString):
    dirname = "AlpacaData"
    os.makedirs(dirname, exist_ok=True)
    timeframe = timeframe if '1m' not in timeframe else '1min'
    return f"{dirname}/{ticker}-{timeframe}.json"


if __name__ == '__main__':
    cli()
