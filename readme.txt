Practicum project readme file
Author: Andrew Larkin
Created for: Laurel Kincl and Perry Hystad, Oregon State University

The practicum folder contains functions written in python and R as part of a practicum project to satisfy 
the requirements for a masters in public health through George Washington University.  The site preceptor was 
Laurel Kincl.  Resources for completing the scripts were contributed by Perry Hystad.  

The purpose of the practicum project was to develop GIS-based exposure measures to environmental conditions that may
alter respiratory lung function.  Time activity patterns, collected by smartphone GPS, were combined with georeferenced 
data sets to create time-weighted exposure measures for multiple types of vegetation, major and minor roads, toxic release inventory
sites, and air monitor networks.  

In the practicum folder, each subfolder contains a single python or R script, along with example input and output files. Descriptions and 
directions for running the scripts are found within commented blocks at the start of each script.




Data sources:
	National Land Cover Database: https://explorer.earthengine.google.com/#detail/USGS%2FNLCD
	Landsat 8 NDVI: https://explorer.earthengine.google.com/#detail/LANDSAT%2FLC8_L1T_TOA
	Road Data: http://wiki.openstreetmap.org/wiki/Downloading_data
		Major and minor road classifications http://wiki.openstreetmap.org/wiki/United_States_Road_Classification
		Note: major roads are "primary" and "secondary" roads.  Minor roads are all other roads
	Air Monitor data: https://aqs.epa.gov/aqsweb/documents/data_mart_welcome.html
	TRI Sites and emissions: https://www.epa.gov/toxics-release-inventory-tri-program/tri-data-and-tools