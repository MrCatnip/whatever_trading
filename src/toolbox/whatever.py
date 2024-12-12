from data_types import BarData, Range
from typing import Literal, List, TypedDict
from strategy_base import StrategyBase

LOOKBACK_PERIOD = 50 # period for higest/lowest closing price within LOOKBACK_PERIOD * 2 + 1 bars
# min bars between closing prices forming ranges. must be at least LOOKBACK_PERIOD
MIN_POINTS_DISTANCE = LOOKBACK_PERIOD
# max bars between closing prices forming ranges. again, must be at least LOOKBACK_PERIOD
MAX_POINTS_DISTANCE = 400
MIN_ZONE_SIZE = 5  # min price difference in % between closing prices forming ranges
MAX_ZONE_SIZE = 15  # max price difference in % between closing prices forming ranges


class ExtremePoint(TypedDict):
    price: float
    index: int


LevelType = Literal["Resistance", "Support"]


class Whatever(StrategyBase):
    def get_latest_data(self, bars):
        return super().get_latest_data(bars)

    def get_historical_data(self, bars):
        potential_resistance_ranges = self.__find_potential_ranges(
            bars, 'Resistance')
        potential_support_ranges = self.__find_potential_ranges(
            bars, 'Support')
        resistance_ranges = self.__get_valid_ranges(
            bars, potential_resistance_ranges, 'Resistance')
        support_ranges = self.__get_valid_ranges(
            bars, potential_support_ranges, 'Support')
        ranges = resistance_ranges + support_ranges
        return ranges

    def __find_potential_ranges(self, bars: List[BarData], levelType: LevelType):
        reset_value = 0 if levelType == 'Resistance' else 100000000
        reset_point: ExtremePoint = {'index': 0, 'price': reset_value}
        is_more_extreme = (lambda x, y: x > y) if levelType == 'Resistance' else (
            lambda x, y: x < y)
        right_offset = 0
        point_prev = reset_point
        point = reset_point
        potential_ranges: List[Range] = []
        for i in range(LOOKBACK_PERIOD, len(bars) - LOOKBACK_PERIOD):
            close = bars[i]['close']
            if is_more_extreme(close, point['price']):
                point = {
                    'index': i,
                    'price': close,
                }
                right_offset = 0
            else:
                right_offset += 1
            if right_offset == LOOKBACK_PERIOD:
                if self.__is__potential_range(point, point_prev):
                    potential_ranges.append({
                        'breach_price': point['price'] if is_more_extreme(point['price'], point_prev['price']) else point_prev['price'],
                        'entry_price': point['price'] if not is_more_extreme(point['price'], point_prev['price']) else point_prev['price'],
                        'starting_index': point['index'] if point['index'] < point_prev['index'] else point_prev['index'],
                        'ending_index': point['index'] if point['index'] > point_prev['index'] else point_prev['index'],
                        'validated_index': 0
                    })
                right_offset = 0
                point_prev = point
                point = reset_point
        return potential_ranges

    def __is__potential_range(self, point: ExtremePoint, point_prev: ExtremePoint):
        points_distance = point['index'] - point_prev['index']
        points_difference = abs(
            (point['price'] - point_prev['price']) / point['price'] * 100)
        return point_prev['index'] != 0 and points_distance >= MIN_POINTS_DISTANCE and points_distance <= MAX_POINTS_DISTANCE and points_difference >= MIN_ZONE_SIZE and points_difference <= MAX_ZONE_SIZE

    def __get_valid_ranges(self, bars: List[BarData], potential_ranges: List[Range], levelType: LevelType):
        valid_ranges: List[Range] = []
        for i in range(LOOKBACK_PERIOD, len(bars)):
            bar = bars[i]
            j = 0
            while j < len(potential_ranges):
                potential_range = potential_ranges[j]
                if i > potential_range['ending_index'] + LOOKBACK_PERIOD and self.__is_valid_touch(bar, potential_range, levelType):
                    valid_ranges.append(potential_ranges.pop(j))
                    valid_ranges[-1]['validated_index'] = i
                else:
                    j += 1
        return valid_ranges

    def __is_valid_touch(self, bar: BarData, potential_range: Range, levelType):
        is_past_entry = (lambda x, y: x > y) if levelType == 'Resistance' else (
            lambda x, y: x < y)
        extreme_type = 'high' if levelType == 'Resistance' else 'low'
        return is_past_entry(bar[extreme_type], potential_range['entry_price']) and not is_past_entry(bar['close'], potential_range['entry_price'])
