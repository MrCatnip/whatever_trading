from typing import List, Tuple, Optional
from toolbox.tool_base import ToolBase
from dataclasses import dataclass, field


@dataclass
class VolumeProfileConfig:
    # % from lowest point to highest point
    levels: List[float] = field(default_factory=lambda: [
                                0, 20, 40, 60, 80, 100])
    # >=1, I.E for val "3" the highest bar will take 1/3 of plot width
    plot_bar_ratio: float = 3


class VolumeProfile(ToolBase):
    def __init__(self, config: Optional[VolumeProfileConfig] = None):
        # Default configuration if none is provided
        default_config = VolumeProfileConfig()

        # Extract configuration values, falling back to defaults where necessary
        config = config or default_config

        self.levels = config.levels or default_config.levels
        self.levels.sort()
        self.plot_bar_ratio = config.plot_bar_ratio or default_config.plot_bar_ratio
        self.plot_bar_ratio = max(self.plot_bar_ratio, 1)
        self.data = Tuple[List[float], float]

    def get_latest_data(self, bars):
        return super().get_latest_data(bars)

    def calculate_historical_data(self, bars) -> Tuple[List[float], float]:

        # Find the highest and lowest points in the data
        lowest = min(bar['low'] for bar in bars)
        highest = max(bar['high'] for bar in bars)

        # Calculate the reference volume between each pair of consecutive levels
        reference_volume = 0
        volume_profile = []

        # Initialize volume counters for each level range
        level_volumes = [0] * (len(self.levels) - 1)
        distance = highest - lowest
        for bar in bars:
            bar_low = bar['low']
            bar_high = bar['high']
            bar_volume = bar['volume']

            # For each level range, check if the bar's high-low range intersects with it
            for i in range(len(self.levels) - 1):
                level_start = lowest + (self.levels[i] / 100) * distance
                level_end = lowest + (self.levels[i + 1] / 100) * distance

                if bar_high >= level_start and bar_low <= level_end:
                    # The bar intersects this level range, add its volume to the corresponding level
                    level_volumes[i] += bar_volume

        # Calculate the reference volume (highest volume between two consecutive levels)
        reference_volume = max(level_volumes)

        # Normalize the volume for each level as a percentage of the reference volume
        for volume in level_volumes:
            volume_profile.append((volume / reference_volume)
                                  if reference_volume else 0)
        self.data = volume_profile, reference_volume
        return self.data

    def add_to_fig(self, fig, bars, data_type="Historical"):
        if data_type == "Historical":
            volume_profile, reference_volume = self.calculate_historical_data(bars)
        elif data_type == "Latest":
            volume_profile, reference_volume = self.get_latest_data(bars)
        else:
            volume_profile, reference_volume = self.data

        timestamps = [bar['timestamp'] for bar in bars]
        # Find the highest and lowest points in the data
        lowest = min(bar['low'] for bar in bars)
        highest = max(bar['high'] for bar in bars)
        distance = highest-lowest
        max_shape_width = len(bars) // self.plot_bar_ratio
        level_start = lowest + (self.levels[0] / 100) * distance
        for i in range(1, len(self.levels)):
            level_end = lowest + (self.levels[i] / 100) * distance
            color = 'rgba(90, 34, 139, 0.2)'
            shape_width = int(max_shape_width*volume_profile[i-1])
            if (shape_width):
                fig.add_shape(
                    type="rect",
                    name=f"Validated {type} Range",
                    x0=timestamps[-shape_width],  # Start from the ending_index
                    x1=timestamps[-1],  # End at the last timestamp
                    y0=level_start,  # Lower bound of the range
                    y1=level_end,  # Upper bound of the range
                    fillcolor=color,
                    line={"width": 0},  # No border
                )
            level_start = level_end

    def get_nr_of_subplots(self):
        return 0
