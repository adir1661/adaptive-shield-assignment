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
        """ method to fix incorrect data (synonyms are considered valid and will be included with a slash)"""

        # remove the cases where the animal to adjective has a irrelevant description in parenthesis
        text = re.sub(r'(\(|\[).*(\)|\])', '', text)

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

        # get just the second table.
        table = doc.select('table.wikitable')[1]

        # get text separates the lines with ';' to deal with it later.
        collateral_adjectives = [x.get_text(';') for x in table.select('td:nth-child(6)')]
        animal_names = [x.text for x in table.select('td:nth-child(1)')]

        rows = []
        for animal, adjective in zip(animal_names, collateral_adjectives):
            # rows with corrupted data are invalid.
            if self._term_valid(animal) and self._term_valid(adjective):
                if ';' not in adjective:
                    rows.append(dict(
                        collateral_adjective=self._parse_text(adjective),
                        animal=self._parse_text(animal)
                    ))
                # in case there is many adjectives to one animal add all the rows accordingly
                else:
                    rows.extend([dict(
                        collateral_adjective=self._parse_text(sub_adjective),
                        animal=self._parse_text(animal)
                    ) for sub_adjective in adjective.split(';')])

        return rows

    @classmethod
    def _term_valid(cls, term) -> bool:
        """ validate a term to remove rows with irrelevant data."""

        term_parsed = cls._parse_text(term)
        if term_parsed == '' or term_parsed == '?':
            return False

        return True
