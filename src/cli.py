import click
from alpaca_interface import AlpacaInterface
from viz import plot_data
from toolbox.whatever import Whatever
import json
from data_types import BarData
from typing import List


@click.group()
def cli():
    """Wusup"""
    pass


@cli.command()
def run():
    #client = AlpacaInterface("BTC/USD", '1D', 2000)
    #bars = client.fetch()
    with open("bar_data.json", "r") as file:
        bars: List[BarData] = json.load(file)
    
    strategy = Whatever()
    ranges = strategy.get_historical_data(bars)
    plot_data(bars, ranges)


if __name__ == '__main__':
    cli()
