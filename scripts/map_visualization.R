# Imports / setup --------------------------------------------------------------
# plot a map containing the regional info of germany
library(leaflet)
library(tidyverse)
# Add Spatial data - From https://gadm.org/download_country_v3.html
library(raster)
library(jsonlite)
library(stringr)
library(htmlwidgets)
library(knitr)
library(formattable)
library(readr)

rm(list = ls())


# Data-preprocessing --------------------------------------------------------------
#read in economics data
economics_data <- jsonlite::fromJSON(txt='./data/combined_data.json', simplifyDataFrame = TRUE)


cities = c("Berlin", "Hamburg", "Muenchen", "Koeln", "Frankfurt",
           "Stuttgart", "Duesseldorf", "Dortmund", "Essen",
           "Leipzig", "Bremen", "Hannover", "Dresden", "Nuernberg")

population = c()
purchasing_power_sum = c()
purchasing_power_per_capita = c()
purchasing_power_index = c()
unemployed_total = c()
unemployment_rate = c()
crimes_committed = c()
crime_rate= c()
new_apartments_rate_percent = c()

for(entry in head(economics_data, -1)){
    population = c(population, entry$population)
    purchasing_power_sum = c(purchasing_power_sum, entry$purchasing_power_sum)
    purchasing_power_per_capita = c(purchasing_power_per_capita, entry$purchasing_power_per_capita)
    purchasing_power_index = c(purchasing_power_index, entry$purchasing_power_index)
    unemployed_total = c(unemployed_total, entry$unemployed_total)
    unemployment_rate = c(unemployment_rate, entry$unemployment_rate)
    crimes_committed = c(crimes_committed, entry$crimes_committed)
    crime_rate= c(crime_rate, entry$crime_rate)
    new_apartments_rate_percent = c(new_apartments_rate_percent, entry$new_apartments_rate_percent)
}
econ_df = data.frame(cities, population, purchasing_power_sum, purchasing_power_per_capita,
                     purchasing_power_index, unemployed_total, unemployment_rate,
                     crimes_committed, crime_rate, new_apartments_rate_percent)


#read in the main information from rent
rent_all <- feather::read_feather('./data/rent_data.feather') %>%
    dplyr::rename(city = index) %>% 
    subset(select=c("city", "one_room_immo_center", "three_rooms_immo_center",
                    "one_room_immo_outside", "three_rooms_immo_outside")) 

#rename some of the entries in cities to allow for correct merging
cities[3] = "Munich"
cities[4] = "Cologne"
cities[7] = "Dusseldorf"
cities[12] = "Hanover"
cities[14] = "Nuremberg"

#subset all the rent data to the 13 cities we have economic data on
rent_small <- subset(rent_all, city %in% cities)

#re-name them again to allow for the merge
rent_small$city[3] = "Koeln"
rent_small$city[6] = "Duesseldorf"
rent_small$city[10] = "Hannover"
rent_small$city[12] = "Muenchen"
rent_small$city[13] = "Nuernberg"

#merge the two datasets to have one master df
df_complete <- merge(rent_small, econ_df, by.x = "city", by.y="cities")

#readjust the crime rate to percent
df_complete$crime_rate = as.double(df_complete$crime_rate * 100)

#manual data cleaning of huge outlier in rent data
df_complete$one_room_immo_center[5] = mean(df_complete$one_room_immo_center)

#build normalized data columns for the visualization
df_complete['norm_1_center'] <- (df_complete$one_room_immo_center - min(df_complete$one_room_immo_center)) / (max(df_complete$one_room_immo_center) - min(df_complete$one_room_immo_center))

df_complete['norm_3_center'] <- (df_complete$three_rooms_immo_center - min(df_complete$three_rooms_immo_center)) / (max(df_complete$three_rooms_immo_center) - min(df_complete$three_rooms_immo_center))

df_complete['norm_1_outside'] <- (df_complete$one_room_immo_outside - min(df_complete$one_room_immo_outside)) / (max(df_complete$one_room_immo_outside) - min(df_complete$one_room_immo_outside))

df_complete['norm_3_outside'] <- (df_complete$three_rooms_immo_outside - min(df_complete$three_rooms_immo_outside)) / (max(df_complete$three_rooms_immo_outside) - min(df_complete$three_rooms_immo_outside))

ger$CC_2
#hand-code the CC_2 codes
CC_2_codes = c('11000','04011','05913' ,'14612','05111' ,'05113','06412','02000', '03241','05315','14713',
               '09162','09564', '08111' )
df_complete$CC_2 = CC_2_codes

# Visualization --------------------------------------------------------------
#read in the polygon file of Germany
ger <- getData("GADM", country="Germany", level=2) # Change granularity level 1-3
ger@data <- dplyr::left_join(ger@data, df_complete, by = "CC_2")

# rename for visualization purposes and problems with letter encoding
ger$NAME_2[99] = "München"

#define coloring to fill the polygons
#define bin size
bins_base <- quantile(df_complete$population)

bins_rent1c <- quantile(df_complete$one_room_immo_center)
bins_rent1o <- quantile(df_complete$one_room_immo_outside)
bins_rent3c <- quantile(df_complete$three_rooms_immo_center)
bins_rent3o <- quantile(df_complete$three_rooms_immo_outside)
bins_unempl <- quantile(df_complete$unemployment_rate)
bins_crime <- quantile(df_complete$crime_rate)

bins_pp <- quantile(df_complete$purchasing_power_index)
bins_newapt <- unique(quantile(df_complete$new_apartments_rate_percent))

#define color palette
color_base <- colorBin("BuPu", domain = ger$population, bins = bins_base)

color_rent1c <- colorBin("Reds", domain = ger$one_room_immo_center, bins = bins_rent1c)
color_rent1o <- colorBin("Reds", domain = ger$one_room_immo_outside, bins = bins_rent1o)
color_rent3c <- colorBin("Reds", domain = ger$three_rooms_immo_center, bins = bins_rent3c)
color_rent3o <- colorBin("Reds", domain = ger$three_rooms_immo_outside, bins = bins_rent3o)


color_unempl <- colorBin("Reds", domain=ger$unemployment_rate, bins = bins_unempl)
color_crime <- colorBin("Reds", domain=ger$crime_rate, bins = bins_crime)


color_pp <- colorBin("RdYlBu", domain=ger$purchasing_power_index, bins = bins_pp)
color_newapt <- colorBin("RdYlBu", domain=ger$new_apartments_rate_percent, bins=bins_newapt)

#polygon popups
popup  <- paste0("<strong>Name: </strong>", ger$NAME_2, "<br>",
                 "<strong>Population: </strong>", 
                 comma(ger$population, digits = 0), "<br>",
                 "<strong>Purchasing power index: </strong>", 
                 ger$purchasing_power_index, "<br>",
                 "<strong>Unemployment rate: </strong>", 
                 comma(ger$unemployment_rate, digits=2), "%<br>",
                 "<strong>Crime rate: </strong>", 
                 comma(ger$crime_rate, digits=1), "%<br>",
                 "<strong>New apartment rate: </strong>", 
                 comma(ger$new_apartments_rate_percent, digits=2), "%<br>")


#define the label styling
label_base <- sprintf(
    "<strong></strong>Population in %s:<br/>%s",
    ger$NAME_2, format(comma(ger$population, digits=0), scientific = FALSE)
) %>% lapply(htmltools::HTML)

label_rent1c <- sprintf(
    "<strong>Average rent for 1 room in city-center in </strong>%s:<br/>%g €",
    ger$NAME_2, floor(ger$one_room_immo_center)
) %>% lapply(htmltools::HTML)

label_rent1o <- sprintf(
    "<strong>Average rent for 1 room outside of city in </strong>%s:<br/>%g €",
    ger$NAME_2, floor(ger$one_room_immo_outside)
) %>% lapply(htmltools::HTML)

label_rent3c <- sprintf(
    "<strong>Average rent for 3 rooms in city-center in </strong>%s:<br/>%g €",
    ger$NAME_2, floor(ger$three_rooms_immo_center)
) %>% lapply(htmltools::HTML)

label_rent3o <- sprintf(
    "<strong>Average rent for 3 rooms outside of city in </strong>%s:<br/>%g €",
    ger$NAME_2, floor(ger$three_rooms_immo_outside)
) %>% lapply(htmltools::HTML)

label_crime <- sprintf(
    "<strong>Crime rate in </strong>%s:<br/>%g<br/> %%",
    ger$NAME_2, comma(ger$crime_rate,2)
) %>% lapply(htmltools::HTML)

label_unemployment_rate <- sprintf(
    "<strong>Unemployment rate in </strong>%s:<br/>%g %%",
    ger$NAME_2, comma(ger$unemployment_rate,2)
) %>% lapply(htmltools::HTML)

label_purchasing_power <- sprintf(
    "<strong>Purchasing power in </strong>%s:<br/>%g",
    ger$NAME_2, ger$purchasing_power_index
) %>% lapply(htmltools::HTML)

label_newapt <- sprintf(
    "<strong>Rate of new apartments in </strong>%s:<br/>%g %%",
    ger$NAME_2, ger$new_apartments_rate_percent
) %>% lapply(htmltools::HTML)



# plot map
my_map <- leaflet(options = leafletOptions(minZoom = 5.8)) %>% 
    addProviderTiles(provider = "Wikimedia") %>%
    setView(lat=51.133333, lng=10.416667, zoom = 5.8) %>%
    
    # Add rent 1 room center information
    addPolygons(data = ger,
                group = "Base map",
                stroke = T,
                color = "white",
                weight = 1.5,
                opacity = 0.3,
                fillColor= ~color_base(population),
                label = label_base,
                labelOptions = labelOptions(
                    style = list("font-weight" = "normal", padding = "3px 8px"),
                    textsize = "15px",
                    direction = "auto"),
                fillOpacity = 0.3,
                popup = popup, 
                highlightOptions = highlightOptions(weight = 4,
                                                    color = "#666",
                                                    fillOpacity = 0.7,
                                                    bringToFront = TRUE)) %>%
    
    # Add rent 1 room center information
    addPolygons(data = ger,
                group = "Rent 1 room city-center",
                stroke = T,
                color = "grey",
                weight = 2,
                opacity = 0.3,
                fillColor= ~color_rent1c(one_room_immo_center),
                label = label_rent1c,
                labelOptions = labelOptions(
                    style = list("font-weight" = "normal", padding = "3px 8px"),
                    textsize = "15px",
                    direction = "auto"),
                fillOpacity = 0.3,
                popup = popup, 
                highlightOptions = highlightOptions(weight = 4,
                                                    color = "#666",
                                                    fillOpacity = 0.7,
                                                    bringToFront = TRUE)) %>%
    
    addLegend("bottomright", group = "Rent 1 room city-center", pal = color_rent1c,
              values = floor(as.numeric(ger$one_room_immo_center)),
              title = "1 room rent prices per district (center)",
              labFormat = labelFormat(suffix = " €")) %>%
    
    # Add rent 1 room outside information
    addPolygons(data = ger,
                group = "Rent 1 room outside",
                stroke = T,
                color = "grey",
                weight = 2,
                opacity = 0.3,
                fillColor= ~color_rent1c(one_room_immo_outside),
                label = label_rent1o,
                labelOptions = labelOptions(
                    style = list("font-weight" = "normal", padding = "3px 8px"),
                    textsize = "15px",
                    direction = "auto"),
                fillOpacity = 0.3,
                popup = popup, 
                highlightOptions = highlightOptions(weight = 4,
                                                    color = "#666",
                                                    fillOpacity = 0.7,
                                                    bringToFront = TRUE)) %>%
    
    addLegend("bottomright", group = "Rent 1 room outside", pal = color_rent1o,
              values = floor(as.numeric(ger$one_room_immo_outside)),
              title = "1 room rent prices per district (outside)",
              labFormat = labelFormat(suffix = " €")) %>%
    
    # Add rent 3 rooms center information
    addPolygons(data = ger,
                group = "Rent 3 rooms city-center",
                stroke = T,
                color = "grey",
                weight = 2,
                opacity = 0.3,
                fillColor= ~color_rent3c(three_rooms_immo_center),
                label = label_rent3c,
                labelOptions = labelOptions(
                    style = list("font-weight" = "normal", padding = "3px 8px"),
                    textsize = "15px",
                    direction = "auto"),
                fillOpacity = 0.3,
                popup = popup, 
                highlightOptions = highlightOptions(weight = 4,
                                                    color = "#666",
                                                    fillOpacity = 0.7,
                                                    bringToFront = TRUE)) %>%
    
    addLegend("bottomright", group = "Rent 3 rooms city-center", pal = color_rent3c,
              values = floor(as.numeric(ger$three_rooms_immo_center)),
              title = "3 room rent prices per district (center)",
              labFormat = labelFormat(suffix = " €")) %>%
    
    
    
    # Add rent 3 rooms outside information
    addPolygons(data = ger,
                group = "Rent 3 rooms outside",
                stroke = T,
                color = "grey",
                weight = 2,
                opacity = 0.3,
                fillColor= ~color_rent3o(three_rooms_immo_outside),
                label = label_rent3o,
                labelOptions = labelOptions(
                    style = list("font-weight" = "normal", padding = "3px 8px"),
                    textsize = "15px",
                    direction = "auto"),
                fillOpacity = 0.3,
                popup = popup, 
                highlightOptions = highlightOptions(weight = 4,
                                                    color = "#666",
                                                    fillOpacity = 0.7,
                                                    bringToFront = TRUE)) %>%
    
    addLegend("bottomright", group = "Rent 3 rooms outside", pal = color_rent3o,
              values = floor(as.numeric(ger$three_rooms_immo_outside)),
              title = "3 room rent prices per district (outside)",
              labFormat = labelFormat(suffix = " €")) %>%
    
    
    # Add unemployment rate
    addPolygons(data = ger,
                group = "Unemployment rate",
                stroke = T,
                color = "grey",
                weight = 2,
                opacity = 0.3,
                fillColor= ~color_unempl(unemployment_rate),
                label = label_unemployment_rate,
                labelOptions = labelOptions(
                    style = list("font-weight" = "normal", padding = "3px 8px"),
                    textsize = "15px",
                    direction = "auto"),
                fillOpacity = 0.4,
                popup = popup, 
                highlightOptions = highlightOptions(weight = 4,
                                                    color = "#666",
                                                    fillOpacity = 0.7,
                                                    bringToFront = TRUE)) %>%
    
    addLegend("bottomright", group = "Unemployment rate", pal = color_unempl,
              values = as.numeric(ger$unemployment_rate),
              title = "Unemployment rate per district",
              labFormat = labelFormat(suffix = " %")) %>%
    
    # Add crime rate
    addPolygons(data = ger,
                group = "Crime rate",
                stroke = T,
                color = "grey",
                weight = 2,
                opacity = 0.3,
                fillColor= ~color_crime(crime_rate),
                label = label_crime,
                labelOptions = labelOptions(
                    style = list("font-weight" = "normal", padding = "3px 8px"),
                    textsize = "15px",
                    direction = "auto"),
                fillOpacity = 0.4,
                popup = popup, 
                highlightOptions = highlightOptions(weight = 4,
                                                    color = "#666",
                                                    fillOpacity = 0.7,
                                                    bringToFront = TRUE)) %>%
    
    addLegend("bottomright", group = "Crime rate", pal = color_crime,
              values = comma(as.numeric(ger$crime_rate),2),
              title = "Crime rate per district",
              labFormat = labelFormat(suffix = " %")) %>%
    
    # Add purchasing power index
    addPolygons(data = ger,
                group = "Purchasing power index",
                stroke = T,
                color = "grey",
                weight = 2,
                opacity = 0.3,
                fillColor= ~color_pp(purchasing_power_index),
                label = label_purchasing_power,
                labelOptions = labelOptions(
                    style = list("font-weight" = "normal", padding = "3px 8px"),
                    textsize = "15px",
                    direction = "auto"),
                fillOpacity = 0.4,
                popup = popup, 
                highlightOptions = highlightOptions(weight = 4,
                                                    color = "#666",
                                                    fillOpacity = 0.7,
                                                    bringToFront = TRUE)) %>%
    
    addLegend("bottomright", group = "Purchasing power index", pal = color_pp,
              values = as.numeric(ger$purchasing_power_index),
              title = "Purchasing power index per district") %>%
    
    # Add news apartments rate
    addPolygons(data = ger,
                group = "New apartments % rate",
                stroke = T,
                color = "grey",
                weight = 2,
                opacity = 0.3,
                fillColor= ~color_newapt(new_apartments_rate_percent),
                label = label_newapt,
                labelOptions = labelOptions(
                    style = list("font-weight" = "normal", padding = "3px 8px"),
                    textsize = "15px",
                    direction = "auto"),
                fillOpacity = 0.6,
                popup = popup, 
                highlightOptions = highlightOptions(weight = 4,
                                                    color = "#666",
                                                    fillOpacity = 0.7,
                                                    bringToFront = TRUE)) %>%
    
    addLegend("bottomright", group = "New apartments % rate", pal = color_newapt,
              values = as.numeric(ger$purchasing_power_index),
              title = "Quantiles of new apartments per district",
              labFormat = labelFormat(suffix = " %")) %>%
    
    
    
    # Add interactive controls
    addLayersControl(position = "topleft",
        overlayGroups = c("Rent 1 room city-center", "Rent 1 room outside",
                          "Rent 3 rooms city-center", "Rent 3 rooms outside",
                          "Unemployment rate", "Crime rate",
                          "Purchasing power index", "New apartments % rate"),
        options = layersControlOptions(collapsed = FALSE)
    ) %>%
    hideGroup(c("Rent 1 room city-center", "Rent 1 room outside",
                "Rent 3 rooms city-center", "Rent 3 rooms outside",
                "Unemployment rate", "Crime rate",
                "Purchasing power index", "New apartments % rate"))

# Data - Export --------------------------------------------------------------
saveWidget(my_map, file="map.html", selfcontained = FALSE)
readr::write_rds(ger, "data/ger.Rds")
readr::write_rds(df_complete, "data/df_complete.Rds")

