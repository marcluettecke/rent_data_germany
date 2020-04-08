
import requests
import wg_scraper
from bs4 import BeautifulSoup
import json


class PurchasingPower:
    def __init__(self):
        self.results = []
        self.url = "https://www.gfk.com/de/insights/press-release/deutsche-haben-2019-rund-763-euro-mehr-zur-verfuegung/"

    def scraper(self):
        print("Begin scraping")
        page_response = requests.get(self.url).text
        soup = BeautifulSoup(page_response, 'lxml')
        # print(soup.prettify())
        result = []
        table = soup.find_all('table', {'class': 'contenttable'})[2]
        entries = table.find_all('tr')
        for entry in entries[1:]:
            values = entry.find_all('td')
            result.append(dict(
                city=values[1].text[3:],
                population=float(values[2].text.replace('.', '').replace(',', '.')),
                purchasing_power_sum=float(values[3].text.replace('.', '').replace(',', '.')),
                purchasing_power_per_capita=int(values[4].text.replace('.', '').replace(',', '.')),
                purchasing_power_index=float(values[5].text.replace('.', '').replace(',', '.')),
            ))
        wg_scraper.save_dict(result, './data/combined_data.json')


# test = PurchasingPower()
# test.scraper()
