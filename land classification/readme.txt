############## extractLandTypes.py ###################
# Author: Andrew Larkin
# Developed for Laurel Kincl and Perry Hystad, Oregon State University
# Date last modified: November 5th, 2016

# Description: this script combines the National Land Classification Database and rasters of 
# monthly NDVI estiamtes to create type-specific NDVI estimates.  The script works by 
# creating binary rasters of each land type and then taking the product of each
# binary and monthly NDVI raster.  

# Requirements:
#      ArcGIS with a liscence for the Spatial Analysis Library
# Tested and developed on:
#      Windows 10
#      Python 2.7
#      ArcGIS 10.3.1