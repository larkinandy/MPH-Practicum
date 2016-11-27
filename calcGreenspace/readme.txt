########### calcGreenExposures.py ##########
# Author: Andrew Larkin
# Developed for Laurel Kincl and Perry Hystad, Oregon State University
# Date last modified: November 22nd, 2016

# Description: this script calculates monthly NDVI and class-specific NDVI values within a
# user-defined buffer distance.  The user must provide a series of folders.  Exposure
# raster names must start with the month of coverage and end with the variable type
# (e.g. OctoberNDVI.tif, NovemberHay.tif).  Months and variable types must be defined
# in the 'set global constants' section of the script.  

# Requirements:
#      ArcGIS with a liscence for the Spatial Analysis Library
# Tested and developed on:
#      Windows 10
#      Python 2.
#      ArcGIS 10.3.1
