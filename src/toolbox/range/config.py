# period for higest/lowest closing price within LOOKBACK_PERIOD * 2 + 1 bars
LOOKBACK_PERIOD = 50
# min bars between closing prices forming ranges. must be at least LOOKBACK_PERIOD
MIN_POINTS_DISTANCE = LOOKBACK_PERIOD
# max bars between closing prices forming ranges. again, must be at least LOOKBACK_PERIOD
MAX_POINTS_DISTANCE = 400
MIN_ZONE_SIZE = 5  # min price difference in % between closing prices forming ranges
MAX_ZONE_SIZE = 15  # max price difference in % between closing prices forming ranges