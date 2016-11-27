############## identifyHotspots.py ###################
# Author: Andrew Larkin
# Developed for Laurel Kincl and Perry Hystad, Oregon State University
# Date last modified: November 11th, 2016

# Description: this script identifies locations where participants spend a large percentage of time,
# called "hotspots".  Hotspots are defined as areas where a participant more than or equal to a 
# variable -defined percentage of time.  Time-location patterns are based on a combination of latitude,
# longitude, and time variables as defined in the variable definition section. Results are written 
# as an output csv file.

# Requirements:
#      ArcGIS with a liscence for the Spatial Analysis Library
# Tested and developed on:
#      Windows 10
#      Python 2.
#      ArcGIS 10.3.1