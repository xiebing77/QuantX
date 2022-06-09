from .momentum_indicator import calc_momentum_indicators
from .volatility_indicator import calc_volatility_indicators
from .cycle_indicator import calc_cycle_indicators


def calc_feature(quoter, config, kdf, calc_all=False):
    return (calc_momentum_indicators(quoter, config, kdf, calc_all) +
            calc_volatility_indicators(quoter, config, kdf, calc_all) +
            calc_cycle_indicators(quoter, config, kdf, calc_all))

