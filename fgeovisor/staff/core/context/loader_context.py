import logging

from staff.interfaces.strategies.loader import DataLoader
from staff.core.strategies import GoogleDataLoader, SimpleDataLoader

from visor_bend_site.settings import DEFAULT_CALCULATION_STRATEGY

logger = logging.getLogger(__name__)


class CalculationContext:

    def __init__(self, strategy: DataLoader) -> None:
        self._strategy = strategy

        try:
            self._strategy.auth()
        except Exception as exc:
            logger.exception("Authentification error: ", exc)

    def visualize(self):
        self._strategy.download_image()
        _image_obj = self._strategy.calculate_index()
        return _image_obj
    
    def metrics(self):
        self._strategy.load_data()


class StrategyRegistry:

    _strategies = {
        "gee": None,
        "napi": None,
        "simple": SimpleDataLoader
    }

    @classmethod
    def get_strategy(cls, name: str, *args, **kwargs):
        strategy_class = cls._strategies.get(name)

        if not strategy_class:
            raise ValueError(f"Strategy {name} not found")
        return strategy_class(*args, **kwargs)

    @classmethod
    def registry(cls, name: str, strategy_class: DataLoader):
        cls._strategies[name] = strategy_class


strategy = StrategyRegistry.get_strategy(DEFAULT_CALCULATION_STRATEGY)
calculatuion_context = CalculationContext(strategy)
