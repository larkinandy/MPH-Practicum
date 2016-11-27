############## calcAirExp.py ###################
# Author: Andrew Larkin
# Developed for Laurel Kincl and Perry Hystad, Oregon State University
# Date last modified: November 19th, 2016

# Description: this script calculates inverse distance weighted exposure to TRI sites, 
# distance to nearest air monitor sites, and nearest air monitor  in Oregon.  TRI exposure is calculated as 
# the cumulative sum of total air release (stack plus fugitive air) divided by the 
# distance all TRI sites within a given distance.  Distance to air monitors is calculated separately for each pollutant
# (e.g. distance to nearest PM2.5 air monitor may be different than distanct to nearest NO2 air monitor).  Results are 
# produced in an output shapefile


# Requirements:
#      ArcGIS with a liscence for the Spatial Analysis Library
# Tested and developed on:
#      Windows 10
#      Python 2.
#      ArcGIS 10.3.1
