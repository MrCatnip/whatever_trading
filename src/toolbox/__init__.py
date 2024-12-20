from typing import Literal
from .fib_retrace import FibonacciRetracement
from .ma_ribbon import MARibbon
from .range import PotentialRange
from .ichimoku import Ichimoku
from .vol_profile import VolumeProfile
ToolName = Literal["Range", "Ichimoku",
                   "FibonacciRetracement", "MARibbon", "VolumeProfile"]
