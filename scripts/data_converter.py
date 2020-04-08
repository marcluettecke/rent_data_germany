import read_in_from_MongoDB
import pandas as pd
import json
import statistics


def convert_combined_data_to_df(filepath: str) -> pd.DataFrame:
    """
    Combines the miscellaneous information from the 'combined_data.json' file in a pandas df for further analysis
    Args:
        filepath [str]: filepath of the .json file to read in
    Returns:
         df [pd.Dataframe]: information inserted into a pandas dataframe
    """
    with open(filepath) as jsonfile:
        other_data = json.load(jsonfile)
    df = pd.DataFrame(columns=['city', 'population', 'purchasing_power_sum', 'purchasing_power_per_capita',
                               'purchasing_power_index', 'unemployed_total', 'unemployment_rate',
                               'crimes_committed', 'crime_rate', "new_apartments_rate_percent"])
    for entry in other_data:
        df_temp = pd.DataFrame(
            data=[[entry, other_data[entry]['population'], other_data[entry]['purchasing_power_sum'],
                   other_data[entry]['purchasing_power_per_capita'],
                   other_data[entry]['purchasing_power_index'],
                   other_data[entry]['unemployed_total'],
                   other_data[entry]['unemployment_rate'],
                   other_data[entry]['crimes_committed'], other_data[entry]['crime_rate'],
                   other_data[entry]['new_apartments_rate_percent']]],
            columns=['city', 'population', 'purchasing_power_sum', 'purchasing_power_per_capita',
                     'purchasing_power_index', 'unemployed_total', 'unemployment_rate',
                     'crimes_committed', 'crime_rate', 'new_apartments_rate_percent'])
        df = df.append(df_temp, ignore_index=True)
    df.replace("NA", None)
    df.set_index('city')
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(df)
    return df


class DataConverter:
    """
    Class to convert the MongoDB entries of the 'immo_db' table into a pandas df for further analysis
    """

    def __init__(self):
        """
        Constructor to load all the information from the MongoDB 'immo_db'
        """
        data_reader = read_in_from_MongoDB.DataLoader()
        self.data = data_reader.reader_MongoDB_numbeo()
        self.cities = list(self.data.keys())
        self.one_room_center = {}
        self.three_room_center = {}
        self.one_room_outside = {}
        self.three_room_outside = {}
        for entry in self.data:
            self.one_room_center[entry] = self.data[entry][0]
            self.three_room_center[entry] = self.data[entry][1]
            self.one_room_outside[entry] = self.data[entry][2]
            self.three_room_outside[entry] = self.data[entry][3]

    def convert_rent_to_df(self):
        """
        Create lists, which are then fed into a pandas df for the initial comparison of the ImmoScout data with the
        numbeo data.
        Returns:
             df: the dataframe for the 66 cities scraped and their rent information for various sizes and locations
             (averages)
        """
        # read in all the information for all combinations of room-size with close to city-center / far off in
        # individual lists
        one_room_immo_center = []
        for entry in self.one_room_center.values():
            one_room_immo_center.append(entry['price_immo_one_center'])
        one_room_numbeo_center = []
        for entry in self.one_room_center.values():
            one_room_numbeo_center.append(entry['price_numbeo_one_center'])

        three_room_immo_center = []
        for entry in self.three_room_center.values():
            three_room_immo_center.append(entry['price_immo_three_center'])
        three_room_numbeo_center = []
        for entry in self.three_room_center.values():
            three_room_numbeo_center.append(entry['price_numbeo_three_center'])

        one_room_immo_outside = []
        for entry in self.one_room_outside.values():
            one_room_immo_outside.append(entry['price_immo_one_outside'])
        one_room_numbeo_outside = []
        for entry in self.one_room_outside.values():
            one_room_numbeo_outside.append(entry['price_numbeo_one_outside'])

        three_room_immo_outside = []
        for entry in self.three_room_outside.values():
            three_room_immo_outside.append(entry['price_immo_three_outside'])
        three_room_numbeo_outside = []
        for entry in self.three_room_outside.values():
            three_room_numbeo_outside.append(entry['price_numbeo_three_outside'])
        # create the dataframe object from the numerous lists created above
        df = pd.DataFrame(index=list(self.data.keys()),
                          data=list(zip(one_room_immo_center,
                                        one_room_numbeo_center,
                                        three_room_immo_center,
                                        three_room_numbeo_center,
                                        one_room_immo_outside,
                                        one_room_numbeo_outside,
                                        three_room_immo_outside,
                                        three_room_numbeo_outside
                                        )),
                          columns=['one_room_immo_center', 'one_room_numbeo_center',
                                   'three_rooms_immo_center', 'three_rooms_numbeo_center',
                                   'one_room_immo_outside', 'one_room_numbeo_outside',
                                   'three_rooms_immo_outside', 'three_rooms_numbeo_outside'
                                   ])

        # data cleaningn for entry at Dusseldorf to 90th percentile value, because it was unreasonably high
        df.at["Dusseldorf", "one_room_immo_center"] = df.quantile(0.9, axis=0)['one_room_immo_center']
        df.at["Dusseldorf", "three_rooms_immo_outside"] = df.quantile(0.9, axis=0)['three_rooms_immo_outside']

        return df

    def convert_to_feather(self, dataframe):
        dataframe.reset_index(inplace=True)
        dataframe.to_feather('./data/rent_data_daily.feather')


if __name__ == '__main__':
    converter = DataConverter()
    data = converter.convert_rent_to_df()
    converter.convert_to_feather(data)
    # convert_combined_data_to_df('./data/combined_data.json')
    # print(data)
