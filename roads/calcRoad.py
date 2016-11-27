############## calcRoad.py ###################
# Author: Andrew Larkin
# Developed for Laurel Kincl and Perry Hystad, Oregon State University
# Date last modified: November 9th, 2016

# Description: This script calculates exposure to major and minor roads.  
# Major and minor roads are calculated as the distance from the 
# sampled point to the major or minor road.  

# Requirements:
#      ArcGIS with a liscence for the Spatial Analysis Library
# Tested and developed on:
#      Windows 10
#      Python 2.7
#      ArcGIS 10.3.1

############### setup ################

# import modules 
import arcpy
import os
import sys

#set environmental variables 
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True

# folder paths and variables 
folder = os.path.dirname(sys.argv[0]) + "/"
tempFolder = folder # location to store intermediate files to delete later 
participantFile = folder + "exampleParticipant.shp" # shapefile containing smartphone sample points
mjRdsShapefile = folder + "mjRds.shp" # shapefile containing major road data
#miRdsShapefile = folder + "roads/miRds.shp" # shapefile containing minor road data
    

# For each point in an input shapefile, calculate the distance to the nearest major and minor road, in 
# units of meters.  Results are stored in the temporary shapefile stored in the temp folder
# Results 
#    shapefile (string) - filepath to a shapefile containing points to calculate distance to major and minor roads
#    mjRdsFile (string) - filepath to the shapefile containing major roads in Oregon
#    miRdsFile (string) - filepath to the shapefile containing minor roads in Oregon
def calcNearRds(shapefile,mjRdsFile=None,miRdsFile=None):
    if(mjRdsFile != None):
        arcpy.Near_analysis(shapefile,mjRdsFile,method = 'GEODESIC') # calculate distance to major roads
        arcpy.AddField_management(shapefile, "MJRDS", "DOUBLE") # create a new field to the input shapefile and add major road distances
        arcpy.CalculateField_management(shapefile,"MJRDS","1*!NEAR_DIST!","PYTHON_9.3")
    if(miRdsFile != None):    
        arcpy.Near_analysis(shapefile,miRdsFile,method = 'GEODESIC') # calculate distance to minor roads
        # minor road distances
        arcpy.AddField_management(shapefile, "MIRDS", "DOUBLE")      
        arcpy.CalculateField_management(shapefile,"MIRDS","1*!NEAR_DIST!","PYTHON_9.3")    
    arcpy.CopyFeatures_management(shapefile, tempFolder + "addedRoads.shp") # create a new field to the input shapefile and add

    

###################### main function ################

def main():
    calcNearRds(participantFile,mjRdsShapefile)   
    
main()
        
        
    

################### end of calcRoad.py ##############