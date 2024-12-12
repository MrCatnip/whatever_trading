import click
from alpaca_interface import AlpacaInterface
from viz import plot_data
from toolbox.range import Range
import json
from data_types import BarData, TimeframeString
from typing import List
import os


@click.group()
def cli():
    """Wusup"""
    pass


@cli.command()
def fetchall():
    timeframes: List[TimeframeString] = [
        "1M", "1W", "1D", "4H", "1H", "30m", "15m", "1m"
    ]
    ticker = "BTC"
    symbol = f"{ticker}/USD"
    for timeframe in timeframes:
        print(f'Fetching for {symbol} - {timeframe}...')
        client = AlpacaInterface(symbol, timeframe)
        bars = client.fetch()
        file_name = get_file_name(ticker, timeframe)
        with open(file_name, "w") as file:
            # Convert each BarData instance to a dictionary before serializing
            json.dump([bar for bar in bars], file, indent=4)
        print('Done!')


@cli.command()
def plotall():
    timeframes: List[TimeframeString] = [
        "1m", "15m", "30m", "1H", "4H", "1D", "1W", "1M"]
    ticker = "BTC"
    symbol = f"{ticker}/USD"
    for timeframe in timeframes:
        print(f"Parsing data for {symbol} - {timeframe}...")
        file_name = get_file_name(ticker, timeframe)
        with open(file_name, "r") as file:
            bars: List[BarData] = json.load(file)
            strategy = Range()
            ranges = strategy.get_historical_data(bars)
            plot_data(bars, ranges)
        print('Done!')


def get_file_name(ticker: str, timeframe: TimeframeString):
    dirname = "AlpacaData"
    os.makedirs(dirname, exist_ok=True)
    timeframe = timeframe if '1m' not in timeframe else '1min'
    return f"{dirname}/{ticker}-{timeframe}.json"


if __name__ == '__main__':
    cli()
