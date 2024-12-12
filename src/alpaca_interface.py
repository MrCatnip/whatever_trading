from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import datetime
from dateutil.relativedelta import relativedelta
from typing import List
from data_types import BarData, TimeframeString

# No keys required for crypto data
client = CryptoHistoricalDataClient()


class AlpacaInterface:
    def __init__(self, symbol, timeframe: TimeframeString, lookbackPeriod=0):
        self.symbol = symbol
        (self.timeframe, self.intervalMs) = self._parse_timeframe(timeframe)
        self.lookbackPeriod = lookbackPeriod
        self.timeframeString: TimeframeString = timeframe

    def _parse_timeframe(self, timeframe: TimeframeString):
        match timeframe:
            case "1m":
                return (TimeFrame(1, TimeFrameUnit.Minute), 60 * 1000)
            case "15m":
                return (TimeFrame(15, TimeFrameUnit.Minute), 15 * 60 * 1000)
            case "30m":
                return (TimeFrame(30, TimeFrameUnit.Minute), 30 * 60 * 1000)
            case "1H":
                return (TimeFrame(1, TimeFrameUnit.Hour), 60 * 60 * 1000)
            case "4H":
                return (TimeFrame(4, TimeFrameUnit.Hour), 4 * 60 * 60 * 1000)
            case "1D":
                return (TimeFrame(1, TimeFrameUnit.Day), 24 * 60 * 60 * 1000)
            case "1W":
                return (TimeFrame(1, TimeFrameUnit.Week), 7 * 24 * 60 * 60 * 1000)
            case "1M":
                return (TimeFrame(1, TimeFrameUnit.Month), 0) # not needed

    def _get_start_date(self):
        current_utc = datetime.datetime.now(datetime.timezone.utc)
        match self.timeframeString:
            case "1m":
                rounded = current_utc.replace(second=0, microsecond=0)
            case "15m":
                rounded = current_utc - datetime.timedelta(
                    minutes=current_utc.minute % 15, seconds=current_utc.second, microseconds=current_utc.microsecond)
            case "30m":
                rounded = current_utc - \
                    datetime.timedelta(minutes=current_utc.minute %
                                       30, seconds=current_utc.second, microseconds=current_utc.microsecond)

            case "1H":
                rounded = current_utc.replace(
                    minute=0, second=0, microsecond=0)

            case "4H":
                rounded = current_utc - datetime.timedelta(hours=current_utc.hour % 4, minute=current_utc.minute,
                                                           second=current_utc.second, microseconds=current_utc.microsecond)

            case "1D":
                rounded = current_utc.replace(
                    hour=0, minute=0, second=0, microsecond=0)

            case "1W":
                weekday = current_utc.weekday()
                not_so_rounded = current_utc - datetime.timedelta(days=weekday, hours=current_utc.hour, minutes=current_utc.minute,
                                                                  seconds=current_utc.second, microseconds=current_utc.microsecond)
                rounded = not_so_rounded.replace(
                    hour=0, minute=0, second=0, microsecond=0)
            case "1M":
                # Get the first day of the current month
                rounded = current_utc.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0)
                # Subtract (lookbackPeriod - 1) months
                rounded -= relativedelta(months=self.lookbackPeriod-1)
                return rounded
        rounded -= datetime.timedelta(milliseconds=self.intervalMs *
                                      (self.lookbackPeriod-1))
        return rounded

    def fetch(self) -> List[BarData]:
        request_params = CryptoBarsRequest(
            symbol_or_symbols=[self.symbol],
            timeframe=self.timeframe,
            start=self._get_start_date() if self.lookbackPeriod else datetime.datetime(2021, 1, 1),
            limit=self.lookbackPeriod if self.lookbackPeriod else 20000000
        )
        bars = client.get_crypto_bars(request_params)
        data: List[BarData] = []
        for bar in bars[self.symbol]:
            data.append({
                "timestamp": bar.timestamp.isoformat(),
                "open": float(bar.open),
                "high": float(bar.high),
                "low": float(bar.low),
                "close": float(bar.close),
                "volume": float(bar.volume)
            })
        return data
