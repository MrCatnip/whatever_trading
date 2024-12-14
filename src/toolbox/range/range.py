from data_types import BarData
from typing import Literal, List, TypedDict
from toolbox.tool_base import ToolBase
from toolbox.range.config import LOOKBACK_PERIOD, MIN_POINTS_DISTANCE, MAX_POINTS_DISTANCE, MIN_ZONE_SIZE, MAX_ZONE_SIZE


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


class Range(ToolBase):
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
