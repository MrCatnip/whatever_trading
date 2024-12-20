from data_types import BarData
from typing import List
from toolbox import MARibbon, FibonacciRetracement, PotentialRange


class Strategy1():
    # Assuming data
    def backtest(self, bars_low_timeframe: List[BarData], bars_high_timeframe: List[BarData]):
        timeframe_ratio = round(
            len(bars_low_timeframe) / len(bars_high_timeframe))
        tool = MARibbon()
        ma_data, ma_periods = tool.calculate_historical_data(
            bars_low_timeframe)
        tool = FibonacciRetracement()
        fibonacci_retracement_array = tool.calculate_historical_data(
            bars_high_timeframe)
        tool = PotentialRange()
        range_data_array = tool.calculate_historical_data(bars_high_timeframe)
        for i in range(len(bars_high_timeframe)):
            is_within_fib_level = fibonacci_retracement_array[i]
            level_type = range_data_array[i]
            # currently no data to parse since being within key fib level AND within a range is a rarity
            if is_within_fib_level and level_type:
                start_index = i * timeframe_ratio
                end_index = (i+1) * timeframe_ratio
                if level_type == 'Resistance':
                    for j in range(start_index, end_index):
                        print(f'do whatever we want with ma_data[start_index:end_index] for {level_type} level')
                else:
                    for j in range(start_index, end_index):
                        print(f'do whatever we want with ma_data[start_index:end_index] for {level_type} level')
