# Analysis of the rent bubble in Germany

## Introduction
This repository represents a side project to visualize economic factors and rent prices for major German cities interactively.  It was used as a project in my 'Computational Social Science' class as a Data Science master student at the University of Konstanz. The abstract of the resulting paper reads as: 

"The question of drivers for human behavior is complex and finds its epitome in financial- and, consequently, housing-markets through the simultaneous interaction of often millions of agents. This paper allows a first glimpse into exciting interactions between commonly available economic indicators, such as unemployment-rates, crimerates, purchasing power indexes and the rent prices of the most influential German metropolitan areas. A data validity section establishes legitimacy of the scraped data-set by investigating if subjective price overestimation persists, while an interactive visualization encourages the reader to take an active role throughout the paper to observe surprising effects: often, only the absolute values of rent prices appear astonishingly high in pricey cities, but a higher local purchasing power index, allows consumers to own more money in the first place. Low crimeand unemployment-rates demand a price premium for rent, which establishes an unexpected subset of cities to be overpriced in relative terms. Some city-offcials seem aware of the excess demand/supply discrepancy and act proactively, which might offer predictive power for prospective rent bubbles."

## Technical details
The overall pipeline scrapes rent data from the web via python scripts. These files can be found in the /scripts folder especially in wg_scraper.py and wg_scraper_cloud.py. The data was then read into a noSQL database (MongoDB) and queried afterwards with the scripts in read_in_from_MongoDB.py. Complimentary statistics, such as crime rates or unemployment rates are scraped within the statistics_scraper.py files. Common libraries, such as selenium for cases with JS interactivity and beautiful soup are used as scraping vehicles.

Since the leaflet functionalities are sometimes problematic, I switched to R for the visualization in R. Here the major files of interest can be found in map_visualization.R.

## Research results
The question of the project was if an interactive visualization can bring clarity to the often quoted rent bubble of major expensive German cities. Or more acutely: are Munich, Stuttgart and Hamburg really the priciest cities when we account for cost of living there? The results show that it is not as linear of a relationship as often presumed.

The full paper can be read found in the root folder under 'Seminar_paper_writeup.pdf'.

Please don't hesitate if anything is not clear or if you'd like to discuss ideas for future projects! Also, if I can explain web scraping techniques, please let me know, I'm happy to help!
