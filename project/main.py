from project.consumer import PrintConsumer
from project.scraper import AnimalsScraper

CONSUMERS = [PrintConsumer]


def main():
    scraper = AnimalsScraper()
    rows = scraper.run()

    for consumer_class in CONSUMERS:
        consumer_instance = consumer_class(data=rows)
        consumer_instance.process()


if __name__ == '__main__':
    main()
