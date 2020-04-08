from time import sleep
import certifi
import urllib3
from bs4 import BeautifulSoup
import json
# import googlemaps
from pymongo.errors import DuplicateKeyError
from tqdm import tqdm
import parameters
from datetime import date
import datetime
from typing import List, Dict

from pymongo import MongoClient
from selenium import webdriver


def save_dict(dictionary, output_file_name):
    with open(output_file_name, 'w') as file:
        json.dump(dictionary, file, indent=4)


class Scraper():
    def __init__(self):
        # self.google_api = parameters.google_api
        self.db_name = 'immo_db_daily'
        self.mongodb_url = parameters.mongodb_url
        self.chrome_path = parameters.chrome_path
        self.city_dictionary = dict(
            # Berlin="Berlin/-/229458/2511138/",
            Berlin=["Berlin;;;;;", "52.51051;13.43068"],
            Bremen=["Bremen;;;;;", "53.12046;8.73764"],
            Dortmund=["Dortmund;;;;;", "51.50805;7.4708"],
            Dusseldorf=["Düsseldorf;;;;;", "51.23824;6.81513"],
            Dresden=["Dresden;;;;;", "51.07714;13.77372"],
            Essen=["Essen;;;;;", "51.44175;7.01662"],
            Frankfurt=["Frankfurt%20am%20Main;;;;;", "50.12117;8.6369"],
            Hamburg=["Hamburg;;;;;", "53.56746;10.02816"],
            Hanover=["Hannover;;;;;", "52.37971;9.76154"],
            Koeln=["Köln;;;;;", "50.95797;6.96838"],
            Leipzig=["Leipzig;;;;;", "51.34084;12.38764"],
            Munich=["München;;;;;", "48.15437;11.54199"],
            Nuernberg=["Nürnberg;;;;;", "49.4395;11.13467"],
            Stuttgart=["Stuttgart;;;;;", "48.779;9.17698"]
        )
        # self.base_url = "https://www.immobilienscout24.de/Suche/S-T/P-1/Wohnung-Miete/Umkreissuche/"
        self.base_url = "https://www.immobilienscout24.de/Suche/radius/wohnung-mieten?centerofsearchaddress="

    # def geo_coder(self, location: str):
    #     gmaps = googlemaps.Client(key=self.google_api)
    #     geocode_result = gmaps.geocode(location)
    #     try:
    #         lat = geocode_result[0]["geometry"]["location"]["lat"]
    #         lon = geocode_result[0]["geometry"]["location"]["lng"]
    #     except:
    #         lat = None
    #         lon = None
    #     return lat, lon

    def city_scraper(self, city: str, number_of_rooms):
        results = []
        print("Begin scraping of rental prices for {} rooms in: {}".format(number_of_rooms, city))
        url = self.base_url + self.city_dictionary[city][0] + "&numberofrooms=" + "{}.0-{}.00&".format(number_of_rooms,
                                                                                                       number_of_rooms) \
              + "&geocoordinates=" + self.city_dictionary[city][1] + ";15.0&enteredFrom=result_list"
        # url = self.base_url + self.city_dictionary[city] + "-/-/15/{},00-{},00".format(number_of_rooms,
        #                                                                                number_of_rooms)

        current_page = 1
        # first we have to set up a Manager for the Website
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

        chrome_path = self.chrome_path
        driver = webdriver.Chrome(chrome_path)
        while True:
            try:
                driver.get(url)
                if len(driver.window_handles) > 1:
                    window_before = driver.window_handles[0]
                    window_after = driver.window_handles[1]
                    driver.switch_to.window(window_before)
                    driver.close()
                    driver.switch_to.window(window_after)

                # now we have to request the content of the website using a GET request
                r = http.request('GET', url)

                # now we have to decode the data, in case it's a byte stream or ASCII
                html = r.data.decode('utf-8')

                soup = BeautifulSoup(html, 'html.parser')

                # access the listings table block
                entries = soup.find_all('li', {'class': "result-list__listing"})
                for entry in entries:
                    # find an id as unique identifier
                    expose = int(entry['data-id'])

                    # scrape the price we are interested in
                    infos = entry.find_all('dl')
                    price = float(infos[0].find('dd').text.split()[0].replace('.', '').replace(',', '.'))

                    distance = entry.find('div', {'class': "nine-tenths"}).find('div', {'class': 'float-left'}).text[
                               :-4]

                    address = entry.find('button', {'title': "Auf der Karte anzeigen"}). \
                        find('div', {'class': 'font-ellipsis'}).text

                    results.append(dict(
                        _id=expose,
                        city=city,
                        price=price,
                        distance_city_center=distance,
                        rooms=number_of_rooms,
                        address=address,
                        date=date.today().strftime("%d/%m/%y")
                    ))

                print("Total entries for {} on this page : {}. Successfully scraped: {}.".format(city, len(entries),
                                                                                                 len(results)))

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(2)
                click_icon = driver.find_element_by_xpath('//*[@id="pager"]/div[3]/a')
                click_icon.click()

                url = driver.current_url
                print("Done scraping page {}.".format(current_page))
                current_page += 1
            except Exception as e:
                print(str(e))
                break

        print("Scraping successfully finished for {} rooms in {}.".format(number_of_rooms, city))
        # count_geo_coding = 0
        #
        # for entry in tqdm(results, desc="Geocoding coordinates for {} rooms in {}".format(number_of_rooms, city)):
        #     try:
        #         entry['lat'] = self.geo_coder(entry['address'])[0]
        #         entry['lon'] = self.geo_coder((entry['address']))[1]
        #         count_geo_coding += 1
        #     except Exception:
        #         entry['lat'] = None
        #         entry['lon'] = None
        # print("Successfully geocoded coordinates for {} entries in {}".format(count_geo_coding, city))
        return results

    def save_to_mongodb(self, results: List[Dict[str, str]] = None):
        client = MongoClient(self.mongodb_url)
        db = client[self.db_name]
        skip_count = 0
        for document in tqdm(results, desc="Saving files to MongoDB"):
            # posts = db.collection
            try:
                db.posts.insert_one(document)
                # posts.insert(document)
            except DuplicateKeyError:
                print("Skipped entry for duplicate keys.")
                skip_count += 1
                continue
        print("Successfully entered information for {} to MongoDB database and skipped {} entries for duplicate keys".
              format(results[0]["city"], skip_count))

    def show_entries_mongodb(self):
        client = MongoClient(self.mongodb_url)
        db = client[self.db_name]
        # query = {"date": "28/11/19"}
        cursor = db.posts.find()
        for document in cursor:
            print(document)

    def delete_entries_mongodb(self):
        connection = MongoClient()
        db = connection[self.db_name]

        cursor = db.collection.find()
        for document in cursor:
            db.collection.remove(document)
        print("MongoDB {} successfully emptied".format(self.db_name))


if __name__ == '__main__':
    test = Scraper()
    count = 0
    start_time = datetime.datetime.now()
    for city in list(test.city_dictionary.keys())[0:]:
        test_results = test.city_scraper(city, 1)
        test.save_to_mongodb(test_results)
        test_results = test.city_scraper(city, 3)
        test.save_to_mongodb(test_results)
        print(count)
        count += 1
    print("total_time: " + str(datetime.datetime.now() - start_time))
    # test.show_entries_mongodb()
