import numpy as np

from res.strings import Limits

MTR = Limits.MAX_TREND_RATIO


def ceil(i: float) -> float:
    return i if -MTR <= i <= MTR else np.sign(i) * MTR
