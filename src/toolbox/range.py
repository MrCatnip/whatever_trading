from data_types import BarData
from typing import Literal, List, TypedDict
from toolbox.tool_base import ToolBase
from dataclasses import dataclass
from typing import Optional


class Range(TypedDict):
    breach_price: float
    entry_price: float
    starting_index: int
    ending_index: int
    validated_index: int


class ExtremePoint(TypedDict):
    price: float
    index: int


LevelType = Literal["Resistance", "Support"]

@dataclass
class RangeConfig:
    # looking for higest/lowest closing price within lookback_period * 2 + 1 bars
    lookback_period: int = 50
    # min bars between closing prices forming ranges. must be at least lookback_period
    min_points_distance: int = 50
    # max bars between closing prices forming ranges. must be at least lookback_period
    max_points_distance: int = 400
    min_zone_size: float = 5  # min price difference in % between closing prices forming ranges
    max_zone_size: float = 15  # max price difference in % between closing prices forming ranges


class Range(ToolBase):
    def __init__(self, config: Optional[RangeConfig] = None):
        # Default configuration if none is provided
        default_config = RangeConfig()

        # Extract configuration values, falling back to defaults where necessary
        config = config or default_config

        self.lookback_period = config.lookback_period or default_config.lookback_period
        self.min_points_distance = config.min_points_distance or default_config.min_points_distance
        self.min_points_distance = max(self.lookback_period, self.min_points_distance)
        self.max_points_distance = config.max_points_distance or default_config.max_points_distance
        self.max_points_distance = max(self.max_points_distance, self.min_points_distance)
        self.min_zone_size = config.min_zone_size or default_config.min_zone_size
        self.min_zone_size = max(self.min_zone_size, 0)
        self.max_zone_size = config.max_zone_size or default_config.max_zone_size
        self.max_zone_size = max(self.max_zone_size, self.min_zone_size)
    
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

    def add_to_fig(self, fig, bars, data_type="Historical"):
        if data_type == "Historical":
            data = self.get_historical_data(bars)
        elif data_type == "Latest":
            data = self.get_latest_data(bars)
        else:  # else we have cached the data already
            data = data_type
        timestamps = [bar['timestamp'] for bar in bars]
        # Add the base rectangle shape
        for range_item in data:
            breach_price = range_item['breach_price']
            entry_price = range_item['entry_price']
            starting_index = range_item['starting_index']
            ending_index = range_item['ending_index']
            validated_index = range_item['validated_index']
            # Determine rectangle color based on breach/entry price comparison
            type: LevelType = "Resistance" if breach_price >= entry_price else "Support"
            color = 'rgba(0, 255, 0, 0.2)' if type == 'Resistance' else 'rgba(255, 0, 0, 0.2)'
            intense_color = 'rgba(0, 255, 0, 0.3)' if type == 'Resistance' else 'rgba(255, 0, 0, 0.3)'
            even_more_intense_color = 'rgba(0, 48, 143, 0.3)'
            fig.add_shape(
                type="rect",
                name=f"Potential {type} Range",
                x0=timestamps[starting_index],  # Start time (adjust as needed)
                x1=timestamps[ending_index],  # End time (adjust as needed)
                y0=min(breach_price, entry_price),  # Lower bound of the range
                y1=max(breach_price, entry_price),  # Upper bound of the range
                fillcolor=color,
                line={"width": 0},  # No border
            )
            # Add the intense rectangle shape
            fig.add_shape(
                type="rect",
                name=f"Pending validation {type} Range",
                x0=timestamps[ending_index],  # Start from the ending_index
                x1=timestamps[validated_index],  # End at the last timestamp
                y0=min(breach_price, entry_price),  # Lower bound of the range
                y1=max(breach_price, entry_price),  # Upper bound of the range
                fillcolor=intense_color,
                line={"width": 0},  # No border
            )
            # Add the even more intense rectangle shape
            fig.add_shape(
                type="rect",
                name=f"Validated {type} Range",
                x0=timestamps[validated_index],  # Start from the ending_index
                x1=timestamps[-1],  # End at the last timestamp
                y0=min(breach_price, entry_price),  # Lower bound of the range
                y1=max(breach_price, entry_price),  # Upper bound of the range
                fillcolor=even_more_intense_color,
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
        potential_ranges: List[Range] = []
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

    def __get_valid_ranges(self, bars: List[BarData], potential_ranges: List[Range], levelType: LevelType):
        valid_ranges: List[Range] = []
        for i in range(self.lookback_period, len(bars)):
            bar = bars[i]
            j = 0
            while j < len(potential_ranges):
                potential_range = potential_ranges[j]
                if i > potential_range['ending_index'] + self.lookback_period and self.__is_valid_touch(bar, potential_range, levelType):
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
