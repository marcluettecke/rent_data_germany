import requests
from wg_scraper import save_dict
from bs4 import BeautifulSoup


class UnemploymentScraper:
    def __init__(self):
        self.results = []
        self.url = "https://www.statistikportal.de/en/node/535"

    def scraper(self):
        print("Begin scraping")
        page_response = requests.get(self.url).text
        soup = BeautifulSoup(page_response, 'lxml')
        result = []
        table = soup.find('table', {'class': 'table'})
        entries = table.find_all('tr')[3:]
        for entry in entries:
            values = entry.find_all('td')
            result.append(dict(
                state=values[0].text,
                unemployed_total=int(values[1].text.replace('.', '')),
                unemployment_rate=float(values[2].text.replace(',', '.'))
            ))
        print(result)
        save_dict(result, './data/unemployment_rate.json')

test = UnemploymentScraper()
test.scraper()