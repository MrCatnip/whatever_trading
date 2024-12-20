from data_types import BarData
from typing import Literal, List, TypedDict
from toolbox.tool_base import ToolBase
from dataclasses import dataclass
from typing import Optional

LevelType = Literal["Resistance", "Support"]
ExitType = Literal["Breach", "Bounce"]


class PotentialRange(TypedDict):
    breach_price: float
    entry_price: float
    starting_index: int
    ending_index: int


class Range(TypedDict):
    price_low: float
    price_high: float
    starting_index: int
    type: LevelType


class ExtremePoint(TypedDict):
    price: float
    index: int


@dataclass
class RangeConfig:
    # looking for higest/lowest closing price within lookback_period * 2 + 1 bars
    lookback_period: int = 50
    # min bars between closing prices forming ranges. must be at least lookback_period
    min_points_distance: int = 50
    # max bars between closing prices forming ranges. must be at least lookback_period
    max_points_distance: int = 400
    # min price difference in % between closing prices forming ranges
    min_zone_size: float = 5
    # max price difference in % between closing prices forming ranges
    max_zone_size: float = 15


class PotentialRange(ToolBase):
    def __init__(self, config: Optional[RangeConfig] = None):
        # Default configuration if none is provided
        default_config = RangeConfig()

        # Extract configuration values, falling back to defaults where necessary
        config = config or default_config

        self.lookback_period = config.lookback_period or default_config.lookback_period
        self.min_points_distance = config.min_points_distance or default_config.min_points_distance
        self.min_points_distance = max(
            self.lookback_period, self.min_points_distance)
        self.max_points_distance = config.max_points_distance or default_config.max_points_distance
        self.max_points_distance = max(
            self.max_points_distance, self.min_points_distance)
        self.min_zone_size = config.min_zone_size or default_config.min_zone_size
        self.min_zone_size = max(self.min_zone_size, 0)
        self.max_zone_size = config.max_zone_size or default_config.max_zone_size
        self.max_zone_size = max(self.max_zone_size, self.min_zone_size)
        self.current_range: Range = None
        self.current_range_index = -1
        self.ranges: List[Range] = []
        self.data: List[LevelType] = []

    def get_latest_data(self, bars):
        return super().get_latest_data(bars)

    def calculate_historical_data(self, bars):
        potential_resistance_ranges = self.__find_potential_ranges(
            bars, 'Resistance')
        potential_support_ranges = self.__find_potential_ranges(
            bars, 'Support')
        resistance_ranges = self.__get_valid_ranges(
            bars, potential_resistance_ranges, 'Resistance')
        support_ranges = self.__get_valid_ranges(
            bars, potential_support_ranges, 'Support')
        self.ranges = resistance_ranges + support_ranges
        self.data = self.__get_bars_status(bars)
        return self.data

    def add_to_fig(self, fig, bars, data_type="Historical"):
        if data_type == "Historical":
            self.calculate_historical_data(bars)
            data = self.ranges
        elif data_type == "Latest":
            self.get_latest_data(bars)
            data = self.ranges
        elif data_type:
            data = data_type
        timestamps = [bar['timestamp'] for bar in bars]
        # Add the base rectangle shape
        for range_item in data:
            price_high = range_item['price_high']
            price_low = range_item['price_low']
            starting_index = range_item['starting_index']
            # Determine rectangle color based on breach/entry price comparison
            color = 'rgba(255, 255, 0, 0.2)'
            fig.add_shape(
                type="rect",
                name=f"Potential {type} Range",
                x0=timestamps[starting_index],  # Start time (adjust as needed)
                x1=timestamps[-1],  # End time (adjust as needed)
                y0=price_low,  # Lower bound of the range
                y1=price_high,  # Upper bound of the range
                fillcolor=color,
                line={"width": 0},  # No border
            )

    def get_nr_of_subplots(self):
        return 0

    def __find_potential_ranges(self, bars: List[BarData], levelType: LevelType):
        reset_value = 0 if levelType == 'Resistance' else 100000000
        reset_point: ExtremePoint = {'index': 0, 'price': reset_value}
        is_more_extreme = (lambda x, y: x > y) if levelType == 'Resistance' else (
            lambda x, y: x < y)
        right_offset = 0
        point_prev = reset_point
        point = reset_point
        potential_ranges: List[PotentialRange] = []
        for i in range(self.lookback_period, len(bars) - self.lookback_period):
            close = bars[i]['close']
            if is_more_extreme(close, point['price']):
                point = {
                    'index': i,
                    'price': close,
                }
                right_offset = 0
            else:
                right_offset += 1
            if right_offset == self.lookback_period:
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
        return point_prev['index'] != 0 and points_distance >= self.min_points_distance and points_distance <= self.max_points_distance and points_difference >= self.min_zone_size and points_difference <= self.max_zone_size

    def __get_valid_ranges(self, bars: List[BarData], potential_ranges: List[PotentialRange], levelType: LevelType):
        valid_ranges: List[Range] = []
        for i in range(self.lookback_period, len(bars)):
            bar = bars[i]
            j = 0
            while j < len(potential_ranges):
                potential_range = potential_ranges[j]
                if i > potential_range['ending_index'] + self.lookback_period and self.__is_valid_touch(bar, potential_range, levelType):
                    potential_ranges.pop(j)
                    breach_price = potential_range['breach_price']
                    entry_price = potential_range['entry_price']
                    valid_ranges.append({
                        'price_low': entry_price if levelType == 'Resistance' else breach_price,
                        'price_high':  breach_price if levelType == 'Resistance' else entry_price,
                        'starting_index': i,
                        'type': levelType
                    })
                    valid_ranges[-1]['validated_index'] = i
                else:
                    j += 1
        return valid_ranges

    def __is_valid_touch(self, bar: BarData, potential_range: PotentialRange, levelType):
        is_past_entry = (lambda x, y: x > y) if levelType == 'Resistance' else (
            lambda x, y: x < y)
        extreme_type = 'high' if levelType == 'Resistance' else 'low'
        return is_past_entry(bar[extreme_type], potential_range['entry_price']) and not is_past_entry(bar['close'], potential_range['entry_price'])

    def __flip_range(self, range: Range):
        type = range['type']
        range['type'] = 'Resistance' if type == 'Support' else 'Support'

    def __get_bars_status(self, bars: List[BarData]):
        # Set the bar status to none untill first confirmed range
        starting_point = 9999999
        data: List[LevelType] = []
        for range_item in self.ranges:
            starting_point = min(starting_point, range_item['starting_index'])
        for i in range(0, starting_point):
            data.append(None)
        # Then see if a bar is within a range or exiting one
        for i in range(starting_point, len(bars)):
            data.append(self.__get_bar_status(bars[i], i))
        return data

    def __get_bar_status(self, bar: BarData, index: int):
        close: float = bar['close']
        if self.current_range:
            level_type = self.current_range['type']
            high = self.current_range['price_high']
            low = self.current_range['price_low']
            is_breach = (lambda close, high, low: close > high) if level_type == 'Resistance' else (
                lambda close_price, high, low: close_price < low)
            is_bounce = (lambda close, high, low: close < low) if level_type == 'Resistance' else (
                lambda close, high, low: close > high)
            if is_breach(close, high, low):
                self.__flip_range(self.ranges[self.current_range_index])
                self.current_range = None
                self.current_range_index = -1
                return None
            elif is_bounce(close, high, low):
                self.current_range = None
                self.current_range_index = -1
                return None
            else:
                return self.current_range['type']
        else:
            for j in range(len(self.ranges)):
                range_item = self.ranges[j]
                if close > range_item['price_low'] and close < range_item['price_high'] and index >= range_item['starting_index']:
                    self.current_range = range_item
                    self.current_range_index = j
                    return self.current_range['type']
