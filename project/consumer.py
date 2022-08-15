from abc import ABC, abstractmethod
from pprint import pprint
from typing import List, Dict


class BaseConsumer(ABC):
    """ consumer base class to process the scraped data"""
    data: List[Dict]

    def __init__(self, data):
        self.data = data

    @abstractmethod
    def process(self):
        raise NotImplementedError('')


class PrintConsumer(BaseConsumer):
    """ consumer for the print use case """


    def process(self):
        # sorting for the sake of the presentation.
        sorted_data = sorted(self.data, key=lambda d: ( d['collateral_adjective'],d['animal'],))

        # orginizing the string to be more readable.
        presentable_data = [f"collateral_adjective: {d['collateral_adjective']} => animal: {d['animal']}" for d in sorted_data]
        pprint(presentable_data)
