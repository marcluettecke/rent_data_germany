import json

# helper calculation for crime rate
# with open('./data/combined_data.json') as jsonfile:
#     data = json.load(jsonfile)
#
# for key in data:
#     data[key]['crime_rate'] = round(data[key]['crimes_committed'] / data[key]['population'],ndigits=2)
#
# with open('./data/combined_data.json', 'w') as jsonfile:
#     json.dump(data, jsonfile)

# with open('./data/numbeo_germany.json') as jsonfile:
#     data = json.load(jsonfile)

# city_data = data['Germany']['child']
#
# city_data.pop('')
# rent_data = {}
# for key in city_data:
#     rent_data[key] = city_data[key]["Rent Per Month"]
# # print(rent_data)
# rent_data_clean = {}
# for key in rent_data:
#     try:
#         rent_data_clean[key] = dict(
#             one_room_city_center=int(rent_data[key][0][1][:-5][1:].replace(',', '')),
#             one_room_outside=int(rent_data[key][1][1][:-5][1:].replace(',', '')),
#             three_rooms_city_center=int(rent_data[key][2][1][:-5][1:].replace(',', '')),
#             three_rooms_outside=int(rent_data[key][3][1][:-5][1:].replace(',', ''))
#         )
#     except Exception:
#         continue
#     print(rent_data_clean)
#
#     with open('./data/rent_data_numbeo.json', 'w') as jsonfile:
#         json.dump(rent_data_clean, jsonfile)

#https://www.statistikportal.de/de/haushalte-und-wohnen/bautaetigkeit-und-wohnen
with open('./data/new_buildings.json') as jsonfile:
    data = json.load(jsonfile)
    # print(data)

for entry in data:
    entry['new_apartments_rate_percent'] = round((entry['new_apartments'] / entry['existing_apartments']) * 100, 5)
with open('./data/new_buildings.json', 'w') as jsonfile:
    json.dump(data, jsonfile)

