import parameters
import json
from pymongo import MongoClient
from itertools import groupby
from operator import itemgetter
import pandas as pd
from pprint import PrettyPrinter


class DataLoader:
    """
    Class to define a functionality to interact with the previously scraped rent data and the saved numbeo data and combine them in a comprehensive data source, here a dictionary
    """

    def __init__(self):
        self.db_name = 'immo_db'
        self.mongodb_url = parameters.mongodb_url

    def reader_MongoDB_numbeo(self):
        """
        Method to format numbeo and MongoDB data into dictionary
        :return: result_all [Dict]: Dictionary containing four entries per city, for the two apartment sizes and the two distances to the city center
        """
        # if data_comparison:
        with open('./data/rent_data_numbeo.json') as jsonfile:
            numbeo_data = json.load(jsonfile)
        # else:
        #     numbeo_data = dict(
        #         Berlin=None,
        #         Bremen=None,
        #         Dusseldorf=None,
        #         Hamburg=None,
        #         Frankfurt=None,
        #         Hanover=None,
        #         Munich=None,
        #         Stuttgart=None
        #     )

        # get the data from the DB
        client = MongoClient(self.mongodb_url)
        db = client[self.db_name]
        col = db.posts
        entries = list(col.find())

        # bring the data in comparable format
        list_of_close_to_center = []
        list_of_outside_city_center = []
        for entry in entries:
            try:
                if float(entry['distance_city_center']) < 5:
                    list_of_close_to_center.append(entry)
                else:
                    list_of_outside_city_center.append(entry)
            # make sure we understand which entries we exclude
            except ValueError as e:
                print("error ", e, "on line ", entry)
                continue
        # to find the average over all the entries for a given city, we use the following list comprehensions -
        # one for the inside and one for the outside entries with a threshold of 5 km from city center
        grouper = itemgetter("city", "rooms")

        result_list_inside = []
        for key, grp in groupby(sorted(list_of_close_to_center, key=grouper), grouper):
            temp_dict = dict(zip(["city", "rooms"], key))
            temp_list = [item["price"] for item in grp]
            temp_dict["price"] = sum(temp_list) / len(temp_list)
            result_list_inside.append(temp_dict)

        result_list_outside = []
        for key, grp in groupby(sorted(list_of_outside_city_center, key=grouper), grouper):
            temp_dict = dict(zip(["city", "rooms"], key))
            temp_list = [item["price"] for item in grp]
            temp_dict["price"] = sum(temp_list) / len(temp_list)
            result_list_outside.append(temp_dict)

        # a little clumsy, but we build for individual dictionaries to merge later one per city, two for 1 or 3 bedrooms
        # and two for city center or outside to compare it with the four values we have obtained from numbeo
        result_dictionary_inside_one = {}
        for key in numbeo_data.keys():
            for entry in result_list_inside:
                if entry['city'] == key and entry['rooms'] == 1:
                    result_dictionary_inside_one[key] = dict(
                        price_immo_one_center=entry['price'],
                        price_numbeo_one_center=numbeo_data[key]['one_room_city_center']
                    )
        result_dictionary_inside_three = {}
        for key in numbeo_data.keys():
            for entry in result_list_inside:
                if entry['city'] == key and entry['rooms'] == 3:
                    result_dictionary_inside_three[key] = dict(
                        price_immo_three_center=entry['price'],
                        price_numbeo_three_center=numbeo_data[key]['three_rooms_city_center']
                    )
        result_dictionary_outside_one = {}
        for key in numbeo_data.keys():
            for entry in result_list_outside:
                if entry['city'] == key and entry['rooms'] == 1:
                    result_dictionary_outside_one[key] = dict(
                        price_immo_one_outside=entry['price'],
                        price_numbeo_one_outside=numbeo_data[key]['one_room_outside']
                    )

        result_dictionary_outside_three = {}
        for key in numbeo_data.keys():
            for entry in result_list_outside:
                if entry['city'] == key and entry['rooms'] == 3:
                    result_dictionary_outside_three[key] = dict(
                        price_immo_three_outside=entry['price'],
                        price_numbeo_three_outside=numbeo_data[key]['three_rooms_outside']
                    )
        # finally we merge the results into one big dictionary and skip an entry (was only 1) if it is not present in
        # all of them
        dictionaries = [result_dictionary_inside_one,
                        result_dictionary_inside_three,
                        result_dictionary_outside_one,
                        result_dictionary_outside_three]
        result_all = {}
        for key in result_dictionary_inside_one.keys():
            try:
                result_all[key] = tuple(d[key] for d in dictionaries)
            except KeyError as e:
                print("error ", e, "on line ", key)
                continue
        return result_all


if __name__ == '__main__':
    data_reader = DataLoader()
    data = data_reader.reader_MongoDB_numbeo()
    print(data)

