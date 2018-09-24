# MPH-Practicum #

Scripts used to create environmental exposure estiamtes based on GPS time activity patterns

**Author:** [Andrew Larkin](https://www.linkedin.com/in/andrew-larkin-525ba3b5/) <br>
**Affiliation:** [Oregon State University, College of Public Health and Human Sciences](https://health.oregonstate.edu/) <br>
**Principal Investigator:** [Laurel Kincl](https://health.oregonstate.edu/people/laurel-kincl) <br>
**Date last modified:** September 23rd, 2018

**Summary** <br>
The practicum folder contains functions written in python and R as part of a practicum project to satisfy 
the requirements for a [masters in public health through George Washington University](https://publichealthonline.gwu.edu/).  The site preceptor was [Laurel Kincl](https://health.oregonstate.edu/people/laurel-kincl).  Resources for completing the scripts were contributed by [Perry Hystad](https://health.oregonstate.edu/people/perry-hystad).  

The purpose of the practicum project was to develop GIS-based exposure measures to environmental conditions that may
alter respiratory lung function.  Time activity patterns, collected by smartphone GPS, were combined with georeferenced 
data sets to create time-weighted exposure measures for multiple types of vegetation, major and minor roads, toxic release inventory sites, and air monitor networks.  

In the practicum folder, each subfolder contains a single python or R script, along with example input and output files. Descriptions and directions for running the scripts are found within commented blocks at the start of each script.

**Data sources**
- **National Land Cover Database** - https://explorer.earthengine.google.com/#detail/USGS%2FNLCD
- **Landsat 8 NDVI** - https://explorer.earthengine.google.com/#detail/LANDSAT%2FLC8_L1T_TOA
- **Road Data** - http://wiki.openstreetmap.org/wiki/Downloading_data
- **Major and minor road classifications** - http://wiki.openstreetmap.org/wiki/United_States_Road_Classification. <br> Note: major roads are "primary" and "secondary" roads.  Minor roads are all other roads
- **Air Monitor data** - https://aqs.epa.gov/aqsweb/documents/data_mart_welcome.html
- **TRI Sites and emissions** - https://www.epa.gov/toxics-release-inventory-tri-program/tri-data-and-tools
