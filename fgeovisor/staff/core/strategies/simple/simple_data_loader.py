import logging

from staff.interfaces.strategies.loader import DataLoader


logger = logging.getLogger(__name__)

SIMPLE_METRIC = {
    "date": "2025-01-01",
    "ndvi": {
        "min": 0.1,
        "max": 0.2,
        "mean": 1
    },
    "evi": {
        "min": 0.1,
        "max": 0.2,
        "mean": 1
    },
}

class SimpleDataLoader(DataLoader):

    def __init__(self):
        pass

    def download_image(self):
        logging.debug("simple data loader download image")
        return True
    
    def calculate_index(self):
        logging.debug("simple data loader calculate index")
        return True
    
    @classmethod
    def auth(cls):
        logging.debug("simple data loader auth")
        return True
    
    def load_data(self):
        logging.debug("simple data loader load data")
        return SIMPLE_METRIC