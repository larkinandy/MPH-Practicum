############ calcGreenExposures.py ##########
# Author: Andrew Larkin
# Developed for Laurel Kincl and Perry Hystad, Oregon State University
# Date last modified: November 22nd, 2016

# Description: this script calculates monthly NDVI and class-specific NDVI values within a
# user-defined buffer distance.  The user must provide a series of folders.  Exposure
# raster names must start with the month of coverage and end with the variable type
# (e.g. OctoberNDVI.tif, NovemberHay.tif).  Months and variable types must be defined
# in the 'set global constants' section of the script.  


# import modules 
import arcpy
import os
import sys

#set environmental variables 
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"in_memory/"


# folder paths and variables 
folder = os.path.dirname(sys.argv[0]) + "/"
tempFolder = folder + "tempFiles/"  # location to store intermediate files to delete later 
rasterFolder = folder + "rasters/" # folder containing input NDVI rasters
variableTypes = ["NDVI","crop","hay","grassland","forest","shrub","urban","wetlands"] # list of monthly NDVI rasters
monthList = ["August","September","October"] # list of months covered by the NDVI dataset
inputShapefile = "exampleParticipant.shp" # shapefile containing smartphone sample points
MONTH_FIELD = "months" # field in the inputShapefile attribute table that corresponds to a month
BUFFER_DISTANCE = 5000
outputFile = folder + "outputFile.shp"

################### helper functions ####################

# calculate average NDVI and composition of NDVI (e.g. hay, crop, etc) for points in an input shapefile.  
# Potential rasters are stored in a single input folder.  Calculated values are added to the input shapefile
# as a new attirbute field
# INPUTS:
#    rasterFolder (string) - filepath to the folder containing list of input rasters.  
#    shapefile (string) - filepath to the shapefile containing points to calculate raster values for
#    outputFile (string) - filepath and name for the results output
def calcNDVIExposure(rasterFolder, shapefile, outputFile):

    tempFileList = []   # to store monthly intermediate files that are merged at the end 

    # for each month within the input dataset, calculate NDVI and composition values.  The monthly
    # subset values are merge at the end of the function
    for month in range(0,len(monthList)):
        
        monthSubset = "temp" + str(month)
        whereClause =  MONTH_FIELD + str(" = ") + "'" + str(monthList[month]) + "'"  
        arcpy.Select_analysis(shapefile,monthSubset,whereClause) # extract smartphone values for the month of interest
        currentShapefile = monthSubset
        extent = arcpy.Describe(currentShapefile).extent
        
        # for each variable, calculate the exposure value
        for varType in range(0,len(variableTypes)):
            
            if(variableTypes[varType] == "NDVI"):
                rawRaster = rasterFolder + monthList[month] + "/" + monthList[month] + "NDVI.tif"
            else:
                rawRaster = rasterFolder + monthList[month] + "/" + variableTypes[varType] + "NDVI" + monthList[month] + ".tif"
                arcpy.DeleteField_management(currentShapefile, "RASTERVALU")     
                        
            # load the variable raster into memory and calculate exposure values for the buffer size of interest
            if(os.path.exists(rawRaster)):
                projectedRaster = "projectedRaster"          
                outCS = arcpy.SpatialReference('NAD 1983 UTM Zone 10N')
                arcpy.ProjectRaster_management(rawRaster,projectedRaster,outCS)
                neighborhood = arcpy.sa.NbrCircle(BUFFER_DISTANCE, "MAP")
                tempRaster = arcpy.sa.FocalStatistics(projectedRaster,neighborhood,"MEAN")                
                newShapefile = currentShapefile + "v" + variableTypes[varType]
                arcpy.sa.ExtractValuesToPoints(currentShapefile,tempRaster,newShapefile)
                currentShapefile = newShapefile
                arcpy.AddField_management(currentShapefile, variableTypes[varType], "DOUBLE")
                arcpy.CalculateField_management(currentShapefile,variableTypes[varType],"1*!RASTERVALU!","PYTHON_9.3")
               
                # if the variable type is not NDVI, calculate the percent of NDVI that is captured by the variable
                if(variableTypes[varType] != 'NVDI'):
                    arcpy.AddField_management(currentShapefile, variableTypes[varType] + "perc", "DOUBLE")
                    arcpy.CalculateField_management(currentShapefile,variableTypes[varType] + "perc","!" + variableTypes[varType] + "!" + "/!NDVI!","PYTHON_9.3")      
            else:
                print "warning: filepath " + rasterFilepath + " doesn't exist"
            
        tempFileList.append(currentShapefile)
        
    # combine monthly files into single file and write the results to the output file
    arcpy.Merge_management(tempFileList,outputFile)


############# main script ###########

def main():

    calcNDVIExposure(rasterFolder,inputShapefile,outputFile)
    
main()



########## end of calcGreenExposures.py #########