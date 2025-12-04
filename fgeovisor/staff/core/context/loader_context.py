import logging
from typing import Dict

from staff.interfaces.strategies.loader import DataLoader
from staff.core.strategies import GoogleDataLoader, SimpleDataLoader

from visor_bend_site.settings import DEFAULT_CALCULATION_STRATEGY

logger = logging.getLogger(__name__)


class CalculationContext:

    def __init__(self, strategy: DataLoader) -> None:
        self._strategy = strategy()

    def visualize(self, polygon, index, date_start):
        self._strategy.download_image()
        _image_obj = self._strategy.calculate_index()
        return _image_obj

    def metrics(self, obj, date_start, date_end):
        self._strategy.load_data()


class StrategyRegistry:

    _strategies: Dict[str, DataLoader] = {}

    @classmethod
    def get_strategy(cls, name: str, *args, **kwargs) -> DataLoader:
        strategy_class = cls._strategies.get(name)

        if not strategy_class:
            raise ValueError(f"Strategy {name} not found")
        return strategy_class(*args, **kwargs)

    @classmethod
    def registry(cls, name: str, strategy_class: DataLoader) -> None:
        try:
            strategy_class.auth()
            cls._strategies[name] = strategy_class
        except Exception as e:
            logger.exception("Failed to register %s: Cant authenticate",
                             strategy_class)


StrategyRegistry.registry("simple", SimpleDataLoader)
