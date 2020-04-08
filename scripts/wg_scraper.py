from time import sleep
import certifi
import urllib3
from bs4 import BeautifulSoup
import json
import googlemaps
from pymongo.errors import DuplicateKeyError
from tqdm import tqdm
import parameters
from datetime import date
from typing import List, Dict
from pprint import pprint

from pymongo import MongoClient
from selenium import webdriver


with open('./data/numbeo_germany.json') as f:
    data_dict = json.load(f)

cities = list(data_dict['Germany']['child'].keys())[1:]


def save_dict(dictionary, output_file_name):
    with open(output_file_name, 'w') as file:
        json.dump(dictionary, file, indent=4)


class Scraper():
    def __init__(self):
        self.google_api = parameters.google_api
        self.db_name = 'immo_db'
        self.mongodb_url = parameters.mongodb_url
        self.chrome_path = parameters.chrome_path
        self.city_dictionary = dict(
            Aachen="Aachen/-/-271176/2321026/",
            Aalen="Ostalbkreis_2dAalen/-/6502/2103238/",
            Aschaffenburg="Aschaffenburg/-/-59396/2227902/",
            Augsburg="Augsburg/-/62928/2050892/",
            Bamberg="Bamberg/-/63290/2218634/",
            Bayreuth="Bayreuth/-/111934/2224521/",
            Berlin="Berlin/-/229458/2511138/",
            Bielefeld="Bielefeld/-/-100077/2452533/",
            Bochum="Bochum/-/-189803/2395337/",
            Bonn="Bonn/-/-200590/2311751/",
            Braunschweig="Braunschweig/-/35531/2479826/",
            Bremen="Bremen/-/-83323/2573462/",
            Chemnitz="Chemnitz/-/200657/2324835/",
            Cologne="K_f6ln/-/-209715/2339958/",
            Darmstadt="Darmstadt/-/-95214/2217843/",
            Dessau="Dessau_2dRo_dflau/-/151695/2436080/",
            Dortmund="Dortmund/-/-172926/2398898/",
            Dresden="Dresden/-/260349/2355345/",
            Duisburg="Duisburg/-/-224154/2394222/",
            Dusseldorf="D_fcsseldorf/-/-218996/2371081/",
            Erfurt="Erfurt/-/70187/2339113/",
            Erlangen="Erlangen/-/70066/2186160/",
            Essen="Essen/-/-204255/2392789/",
            Frankfurt="Frankfurt_20am_20Main/-/-95994/2244895/",
            Frankfurt_Oder="Frankfurt_20_28Oder_29/-/302330/2494620/",
            Freiburg_im_Breisgau="Freiburg_20im_20Breisgau/-/-162121/2012539/",
            Gera="Gera/-/144285/2330076/",
            Giessen="Gie_dfen_20_28Kreis_29_2dGie_dfen/-/-92218/2295508/",
            Goettingen="G_f6ttingen_20_28Kreis_29_2dG_f6ttingen/-/-4891/2398652/",
            Halle="Halle_20_28Saale_29/-/134889/2393975/",
            Hamburg="Hamburg/-/1840/2621814/",
            Hanover="Hannover/-/-16001/2491532/",
            Heilbronn="Heilbronn/-/-59390/2138127/",
            Hildesheim="Hildesheim_20_28Kreis_29_2dHildesheim/-/-3303/2466420/",
            Ingolstadt="Ingolstadt/-/99900/2095135/",
            Jena="Jena/-/109744/2332924/",
            Kaiserslautern="Kaiserslautern/-/-160813/2170183/",
            Karlsruhe="Karlsruhe/-/-114684/2124104/",
            Kassel="Kassel/-/-37075/2374877/",
            Kiel="Kiel/-/8076/2706864/",
            Koblenz="Koblenz/-/-168872/2271470/",
            Konstanz="Konstanz_20_28Kreis_29_2dKonstanz/-/-61279/1974928/",
            Krefeld="Krefeld/-/-233698/2383565/",
            Landshut="Landshut/-/156467/2074300/",
            Leipzig="Leipzig/-/163839/2380264/",
            Leverkusen="Leverkusen/-/-206541/2350371/",
            Ludwigshafen="Ludwigshafen_20am_20Rhein/-/-115119/2175830/",
            Luebecke="L_fcbeck/-/49404/2656502/",
            Magdeburg="Magdeburg/-/110902/2465012/",
            Mainz="Mainz/-/-122333/2231631/",
            Mannheim="Mannheim/-/-106827/2177112/",
            Marburg="Marburg_2dBiedenkopf_20_28Kreis_29_2dMarburg/-/-85418/2320705/",
            Moenchengladbach="M_f6nchengladbach/-/-246972/2364436/",
            Muelheim_an_der_Ruhr="M_fclheim_20an_20der_20Ruhr/-/-213390/2389856/",
            Munich="M_fcnchen/-/113055/2029726/",
            Munster="M_fcnster/-/-160749/2448287/",
            Nuremberg="N_fcrnberg/-/81047/2169966/",
            Oldenburg="Oldenburg_20_28Oldenburg_29/-/-117390/2576750/",
            Osnabrueck="Osnabr_fcck/-/-130739/2482001/",
            Paderborn="Paderborn_20_28Kreis_29_2dPaderborn/-/-84951/2419379/",
            Passau="Passau/-/247582/2080473/",
            Pforzheim="Pforzheim/-/-92763/2108226/",
            Potsdam="Potsdam/-/205099/2497524/",
            Ravensburg="Ravensburg_20_28Kreis_29_2dRavensburg/-/-28814/1988074/",
            Regensburg="Regensburg/-/152067/2125736/",
            Reutlingen="Reutlingen_20_28Kreis_29_2dReutlingen/-/-57835/2065737/",
            Rostock="Rostock/-/138201/2687527/",
            Saarbrucken="Stadtverband_20Saarbr_fccken_20_28Kreis_29_2dSaarbr_fccken/-/-215539/2151284/",
            Siegen="Siegen_2dWittgenstein_20_28Kreis_29_2dSiegen/-/-136999/2328283/",
            Solingen="Solingen/-/-202319/2362464/",
            Stuttgart="Stuttgart/-/-59588/2097322/",
            Trier="Trier/-/-237625/2211688/",
            Tubingen="T_fcbingen_20_28Kreis_29_2dT_fcbingen/-/-68987/2069375/",
            Tuttlingen="Tuttlingen_20_28Kreis_29_2dTuttlingen/-/-86869/2010473/",
            Ulm="Ulm/-/-4172/2054105/",
            Wiesbaden="Wiesbaden/-/-123442/2240120/",
            Wolsburg="Wolfsburg/-/52083/2494644/",
            Wuerzburg="W_fcrzburg/-/-4051/2206439/",
            Wuppertal="Wuppertal/-/-195097/2370425/"
        )
        self.base_url = "https://www.immobilienscout24.de/Suche/S-T/P-1/Wohnung-Miete/Umkreissuche/"

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

        url = self.base_url + self.city_dictionary[city] + "-/-/15/{},00-{},00".format(number_of_rooms,
                                                                                       number_of_rooms)
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

                    address = entry.find('button', {'title': "Auf der Karte anzeigen"}).\
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
        # for entry in tqdm(results, desc="Geocoding coordinates for {} rooms in {}".format(number_of_rooms, city)):
        #     try:
        #         entry['lat'] = self.geo_coder(entry['address'])[0]
        #         entry['lon'] =self.geo_coder((entry['address']))[1]
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
        try:
            print("Successfully entered information for {} to MongoDB database and skipped {} entries for duplicate keys".
              format(results[0]["city"], skip_count))
        except Exception:
            pass
        # cursor = db.posts.find({})
        # for document in cursor:
        #     print(document)

    def show_entries_mongodb(self):
        connection = MongoClient()
        db = connection[self.db_name]
        cursor = db.posts.find()
        for document in cursor:
            print(document)

    def delete_entries_mongodb(self):
        connection = MongoClient()
        db = connection[self.db_name]
        cursor = db.posts.find({})
        for document in cursor:
            db.posts.remove(document)
        print("MongoDB {} successfully emptied".format(self.db_name))


if __name__ == '__main__':
    test = Scraper()
    # test_results = test.city_scraper("Aalen", 1)
    # test.show_entries_mongodb()
    # test.delete_entries_mongodb()
    count = 0
    for city in list(test.city_dictionary.keys())[0:]:
        print(city)
        print(count)
        test_results = test.city_scraper(city, 1)
        test.save_to_mongodb(test_results)
        test_results = test.city_scraper(city, 3)
        test.save_to_mongodb(test_results)
        count += 1

    # test.save_to_mongodb(test_results)
    # test.show_entries_mongodb()

#to find zip codes of specific address use this code snippet on scraped data
    # result = test.geo_coder('Bahnhofstr Hamm')
    # gmaps = googlemaps.Client(key=parameters.google_api)
    # print(gmaps.reverse_geocode(result)[0]['address_components'][6]['long_name'])


