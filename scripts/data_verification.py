from scipy.stats import ks_2samp
import matplotlib.pyplot as plt
import matplotlib.style as style
import pandas as pd

from data_converter import DataConverter, convert_combined_data_to_df


class DataComparisonNumbeo:
    """
    Class to test the data quality by comparing the data scraped from ImmoScout 24 and Numbeo
    """

    def __init__(self):
        """
        Constructor to initialize and load in the rent data to compare with the help of the DataConverter class
        """
        converter = DataConverter()
        self.rent_data = converter.convert_rent_to_df()

    def visualization(self, rooms: int, location: str, type: str = "bar"):
        """
        Shows a grouped bar-chart for comparison of the distributions of the rent prices.
        Args:
            rooms [int]: either 1 or 3 for the room sizes available
            location [str]: either 'center' or 'outside' for the location in the city available
            type [str]: type of visualization, choices are 'bar' (default) or 'density' for KDE
             plot.
        """
        # set the style of the matplotlib chart
        style.use('seaborn-darkgrid')
        # if statement to differentiate which data columns are used
        if rooms == 1 and location == 'center':
            # to sort by absolute difference between the two figures to increase readability, we create a temporary
            # column and sort the dat aby it
            self.rent_data['difference'] = abs(
                self.rent_data["one_room_numbeo_center"] - self.rent_data["one_room_immo_center"])
            # the actual plotting of the data, here the index is resetted to allow for plotting of the cities,
            # the appropriate data columns are selected and the bar chart option is selected. Fig size is increased for
            # improved readability
            plot_one_center = self.rent_data.sort_values(by='difference', ascending=False) \
                .reset_index().plot(x="index",
                                    y=["one_room_immo_center",
                                       "one_room_numbeo_center"],
                                    kind=type,
                                    figsize=(20, 10))
            # set basic chart attributes such as title, and labels and format them appropriately
            plt.title("Comparison of small city center apartments of ImmoScout24 vs Numbeo", fontsize=30)
            plot_one_center.legend(["Immo 1 rooms center", "Numbeo 1 rooms center"])
            plot_one_center.set_xlabel("City", fontsize=15, weight='bold')
            plot_one_center.set_ylabel("Average prices per city", fontsize=15, weight='bold')

            plt.savefig('one_room_center.png', bbox_inches='tight')
            # plt.show()
            # delete the temporary 'difference' column
            del self.rent_data['difference']

        elif rooms == 3 and location == 'center':
            self.rent_data['difference'] = abs(
                self.rent_data["three_rooms_numbeo_center"] - self.rent_data["three_rooms_immo_center"])

            plot_one_center = self.rent_data.sort_values(by='difference', ascending=False) \
                .reset_index().plot(x="index",
                                    y=["three_rooms_immo_center",
                                       "three_rooms_numbeo_center"],
                                    kind=type,
                                    figsize=(20, 10))
            plt.title("Comparison of large city apartments of ImmoScout24 vs Numbeo", fontsize=30)
            plot_one_center.legend(["Immo 3 rooms center", "Numbeo 3 rooms center"])
            plot_one_center.set_xlabel("City", fontsize=15, weight='bold')
            plot_one_center.set_ylabel("Average prices per city", fontsize=15, weight='bold')

            plt.savefig('three_rooms_center.png', bbox_inches='tight')
            # plt.show()
            del self.rent_data['difference']

        elif rooms == 1 and location == 'outside':
            self.rent_data['difference'] = abs(
                self.rent_data["one_room_numbeo_outside"] - self.rent_data["one_room_immo_outside"])

            plot_one_center = self.rent_data.sort_values(by='difference', ascending=False) \
                .reset_index().plot(x="index",
                                    y=["one_room_immo_outside",
                                       "one_room_numbeo_outside"],
                                    kind=type,
                                    figsize=(20, 10))
            plt.title("Comparison of small city outskirts apartments of ImmoScout24 vs Numbeo", fontsize=30)
            plot_one_center.legend(["Immo 1 rooms outskirts", "Numbeo 1 rooms outskirts"])
            plot_one_center.set_xlabel("City", fontsize=15, weight='bold')
            plot_one_center.set_ylabel("Average prices per city", fontsize=15, weight='bold')

            plt.savefig('one_room_outside.png', bbox_inches='tight')
            # plt.show()
            del self.rent_data['difference']

        elif rooms == 3 and location == 'outside':
            self.rent_data['difference'] = abs(
                self.rent_data["three_rooms_numbeo_outside"] - self.rent_data["three_rooms_immo_outside"])

            plot_one_center = self.rent_data.sort_values(by='difference', ascending=False) \
                .reset_index().plot(x="index",
                                    y=["three_rooms_immo_outside",
                                       "three_rooms_numbeo_outside"],
                                    kind=type,
                                    figsize=(20, 10))
            plt.title("Comparison of large city outskirts apartments of ImmoScout24 vs Numbeo", fontsize=30)
            plot_one_center.legend(["Immo 3 rooms outskirts", "Numbeo 3 rooms outskirts"])
            plot_one_center.set_xlabel("City", fontsize=15, weight='bold')
            plot_one_center.set_ylabel("Average prices per city", fontsize=15, weight='bold')

            plt.savefig('three_rooms_outside.png', bbox_inches='tight')
            plt.show()
            del self.rent_data['difference']


        # if the options do not correspond with the available data, print an error statement
        else:
            print("Unrecognized combination of room number and location. Please correct input.")

    def ks_test(self):
        """
        Statistical comparison of the distributions of the rent prices with the help of scikit-learns Kolmogorov-Smirnov Test Statistic
        """
        print("Kolgoromov-Smirnov test statistic for one room center:")
        print(ks_2samp(self.rent_data['one_room_immo_center'], self.rent_data['one_room_numbeo_center']))

        print("Kolgoromov-Smirnov test statistic for three rooms center:")
        print(ks_2samp(self.rent_data['three_rooms_immo_center'], self.rent_data['three_rooms_numbeo_center']))

        print("Kolgoromov-Smirnov test statistic for one rooms outside:")
        print(ks_2samp(self.rent_data['one_room_immo_outside'], self.rent_data['one_room_numbeo_outside']))

        print("Kolgoromov-Smirnov test statistic for three rooms outside:")
        print(ks_2samp(self.rent_data['three_rooms_immo_outside'], self.rent_data['three_rooms_numbeo_outside']))

    def column_correlation(self):
        """
        Prints the pairwise correlation between the corresponding ImmoScout and Numbeo data columns
        """
        print("Correlation for one room center:")
        print(self.rent_data['one_room_immo_center'].corr(self.rent_data['one_room_numbeo_center']))

        print("Correlation for three rooms center:")
        print(self.rent_data['three_rooms_immo_center'].corr(self.rent_data['three_rooms_numbeo_center']))

        print("Correlation for one rooms outside:")
        print(self.rent_data['one_room_immo_outside'].corr(self.rent_data['one_room_numbeo_outside']))

        print("Correlation for three rooms outside:")
        print(self.rent_data['three_rooms_immo_outside'].corr(self.rent_data['three_rooms_numbeo_outside']))


if __name__ == '__main__':
    test = DataComparisonNumbeo()
    test.column_correlation()
    test.visualization(1, 'center', 'density')
    test.visualization(1, 'outside', 'density')
    test.visualization(3, 'center', 'density')
    test.visualization(3, 'outside', 'density')
