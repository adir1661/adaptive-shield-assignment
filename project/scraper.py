import re
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
from requests import Response
from requests.exceptions import ReadTimeout

from project.exceptions import TooManyRetries


class BaseSrcaper(ABC):
    """
    an parent class that contains a "run" method to run a specific scraper to get the relevant data.
    """
    url: str

    @abstractmethod
    def scrape(self, response: Response):
        """
        :param response: http response of the class url.
        :return:
        """
        raise NotImplementedError('')

    def run(self):
        """
        generic function to run handle the request to the scraper wanted page.
        ** ideally i would build an api that handles the requests to the page.
        :return: scraped structured data
        """
        retries = 0

        while True:
            try:
                response = requests.get(self.url)
                response.raise_for_status()
                break
            except ReadTimeout:
                if retries > 3:
                    raise TooManyRetries()
                retries += 1
        return self.scrape(response)


class AnimalsScraper(BaseSrcaper):
    url = 'https://en.wikipedia.org/wiki/List_of_animal_names'

    @staticmethod
    def _parse_text(text: str):
        """ method to fix incorrect data"""

        # remove the cases where the animal to adjective has a irrelevant description in parenthesis
        text = re.sub(r'\(.*\)', '', text)

        text = re.sub(r'Also see.*', '', text)

        text = text.strip()

        return text

    def scrape(self, response):
        """
        implementation for each different scraper.
        :param response:
        :return:  wanted result (ideally would have a structured return value to be able to store in a db.)
        """
        html_content = response.text
        doc = BeautifulSoup(html_content, 'html.parser')
        table = doc.select('table.wikitable')[1]

        animal_names = [x.text for x in table.select('td:nth-child(1)')]
        collateral_adjectives = [x.text for x in table.select('td:nth-child(6)')]

        rows = [dict(
            collateral_adjective=self._parse_text(adjective),
            animal=self._parse_text(animal)
        ) for animal, adjective in
            zip(animal_names, collateral_adjectives) if self._term_valid(animal) and self._term_valid(adjective)

        ]

        return rows

    @classmethod
    def _term_valid(cls, term) -> bool:
        term_parsed = cls._parse_text(term)
        if term_parsed == '' or term_parsed == '?':
            return False

        return True
