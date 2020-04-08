library(shiny)
library(shinyWidgets)
library(shinydashboard)
library(shinydashboardPlus)
library(dplyr)
library(ggplot2)
library(leaflet)
library(rgdal)

#rm(list = ls())

#data
# df <- read.csv("./data/sog_test_export.csv", sep = ';')
data_ord <- readr::read_rds("data/data_ord.Rds")
data_pat <- readr::read_rds("data/data_pat.Rds")

spat_dta_ord <- readr::read_rds("data/spat_dta_ord.Rds")
spat_dta_pat <- readr::read_rds("data/spat_dta_pat.Rds")

#header item
header <- dashboardHeaderPlus(
  title = "Test SOG Dashboard",
  fixed = TRUE,
  enable_rightsidebar = TRUE,
  rightSidebarIcon = "gears",
  left_menu = tagList(
    dropdownBlock(
      id = "mydropdown",
      title = "Dropdown 1",
      icon = icon("sliders"),
      sliderInput(
        inputId = "n",
        label = "Number of observations",
        min = 10,
        max = 100,
        value = 30
      ),
      prettyToggle(
        inputId = "na",
        label_on = "NAs keeped",
        label_off = "NAs removed",
        icon_on = icon("check"),
        icon_off = icon("remove")
      )
    ),
    dropdownBlock(
      id = "mydropdown2",
      title = "Dropdown 2",
      icon = icon("sliders"),
      prettySwitch(
        inputId = "switch4",
        label = "Fill switch with status:",
        fill = TRUE,
        status = "primary"
      ),
      prettyCheckboxGroup(
        inputId = "checkgroup2",
        label = "Click me!",
        thick = TRUE,
        choices = c("Click me !", "Me !", "Or me !"),
        animation = "pulse",
        status = "info"
      )
    )
  ),
  dropdownMenu(
    type = "tasks",
    badgeStatus = "danger",
    taskItem(value = 20, color = "aqua", "Refactor code"),
    taskItem(value = 40, color = "green", "Design new layout"),
    taskItem(value = 60, color = "yellow", "Another task"),
    taskItem(value = 80, color = "red", "Write documentation")
  )
)

sidebar <- dashboardSidebar(sidebarMenu(
  menuItem(
    "Overview",
    tabName = "dashboard",
    icon = icon("chart-line")
  ),
  menuItem(
    "Map",
    tabName = "dashboard2",
    icon = icon("map")
  ),
  menuItem(
    "Map2 (WIP)",
    tabName = "dashboard3",
    icon = icon("map")
  ),
  menuItem(
    "Visit-us",
    icon = icon("send", lib = 'glyphicon'),
    href = "https://correlaid.org/"
  )
))



rightsidebar <- rightSidebar(
  background = "dark",
  rightSidebarTabContent(
    id = 1,
    title = "Tab 1",
    icon = "desktop",
    active = TRUE,
    sliderInput(
      "obs",
      "Number of observations:",
      min = 0,
      max = 1000,
      value = 500
    )
  ),
  rightSidebarTabContent(
    id = 2,
    title = "Tab 2",
    textInput("caption", "Caption", "Data Summary")
  ),
  rightSidebarTabContent(
    id = 3,
    icon = "paint-brush",
    title = "Tab 3",
    numericInput("obs", "Observations:", 10, min = 1, max = 100)
  )
)



frow1 <- 
  fluidRow(
    br(),
    br(),
    valueBoxOutput("value1"),
    valueBoxOutput("value2"),
    valueBoxOutput("value3")
)

frow2 <-
  fluidRow(
    box(
      title = "Spenden pro Mitgliedstyp (Top 5 Staedte)",
      status = "primary",
      solidHeader = TRUE,
      collapsible = TRUE,
      width = 12,
      plotOutput("revenuebyRegion")
    )
  )


fluidpage <- fluidPage(
  br(),
  br(),
  leafletOutput("mymap"),
  # mapview:::plainViewOutput("test"),
  p(),
  actionButton("recalc", "New points")
)

fluidpage2 <- fluidPage(
  br(),
  br(),
  leafletOutput("map_lc"),
  p()
)

body <- dashboardBody(
  tabItems(
    tabItem(tabName = "dashboard",
            frow1, frow2),
    tabItem(tabName = "dashboard2",
            fluidpage),
    tabItem(tabName = "dashboard3",
            fluidpage2)
  )
)
  
ui <- dashboardPagePlus(header,
                        sidebar,
                        body,
                        rightsidebar,
                        title = "DashboardPage")

#test objects for map function
r_colors <- rgb(t(col2rgb(colors()) / 255))
names(r_colors) <- colors()

server = function(input, output) {
  summe.spenden <- sum(data_pat$amount)
  
  spenden.region <- 
    data_pat %>%
    #important to notice is that the dplyr package needs to be specified explicitly, since the plyr package from the preprocessing will screw up some of the functionalities if not detached here.
    dplyr::group_by(from) %>% 
    dplyr::summarise(value = sum(amount)) %>% 
    dplyr::filter(value==max(value))
  
  spenden.art <-
    data_pat %>%
    dplyr::group_by(member_type) %>%
    dplyr::summarise(value = sum(amount)) %>%
    dplyr::filter(value==max(value))
  output$value1 <-
    renderValueBox({
      valueBox(
        formatC(spenden.region$value,format = "d",big.mark = ','),
        paste('Top Region:', spenden.region$from),
        icon = icon("stats", lib = 'glyphicon'),
        color = "purple"
      )
    })
  output$value2 <-
    renderValueBox({
      valueBox(
      formatC(summe.spenden,format = "d",big.mark = ','),
      paste('Summe Spenden:'),
      icon = icon("eur", lib = 'glyphicon'),
      color = "green"
      )
    })
  output$value3 <-
    renderValueBox({
      valueBox(
        formatC(spenden.art$value,
                format = "d",
                big.mark = ','),
        paste('Top Typ:', spenden.art$member_type),
        icon = icon("menu-hamburger", lib = 'glyphicon'),
        color = "yellow"
      )
    })
  top10 <-
    data_pat %>%
    dplyr::select(from, member_type, amount) %>% 
    dplyr::group_by(from) %>% 
    dplyr::summarize(summe = sum(amount)) %>% 
    dplyr::arrange(desc(summe)) %>% 
    top_n(5)
  
  top5 <- as.character(top10$from)
  top5_cities <- data_pat[data_pat$from %in% top5, ]
  
  output$revenuebyRegion <-
    renderPlot({
      ggplot(data = top5_cities,            
             aes(
               x = from,
               y = amount,
               fill = factor(member_type)
             )
      ) + 
        geom_bar(position = "dodge", stat = "identity") + ylab("Betrag (in Euros)") +
        xlab("Stadt") +
        theme(legend.position = "bottom",plot.title = element_text(size = 15, face = "bold")) +            ggtitle("Spenden pro Stadt / Typ") + labs(fill = "Typ")
    })
  
  # define the coordinates and proj4string function im mapview
  coordinates(data_pat) <- ~ lon + lat
  proj4string(data_pat) <- "+init=epsg:4326"
  #create a mapview object
  m <- mapview(data_pat, cex = "amount", zcol = "member_type", at = seq(0, 1000, 50))
  
  #create output to be displayed in the UI environment
  output$mymap <-  renderLeaflet({
    # set default view to be an appropriate zoom on Germany
    m@map %>% setView(10, 50, zoom = 5.2)
  })
  
  # Map with clustered Spendendaten (according to Lokalgruppen):
  
  map_lc <- 
    mapview(spat_dta_pat2,
            zcol = "lc")
  output$map_lc <- 
    renderLeaflet({
      setView(map_lc@map, 10, 50, zoom = 5.2)
    })
  
}

shinyApp(
  ui = ui, server = server
  
)