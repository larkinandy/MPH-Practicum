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

################### setup ####################

#import modules
import arcpy
import os
import sys

# folder paths and variables
baseFolder = os.path.dirname(sys.argv[0]) + "/"
landClassRaster = baseFolder + "OregonLandClassification.tif" 
classFolder = baseFolder + "classTypes/" # folder to store binary rasters of class types
NDVI_Folder = baseFolder + "NDVI/" # parent folder containing all of the subset NDVI folders
NDVI_GeneralFolder = NDVI_Folder + "general/" # monthly NDVI values, not type-specific
NDVI_TypeFolder = NDVI_Folder + "typeSpecific/" # type specific NDVI values (e.g. NDVI from hay)
monthVars = ["August","September","October"] # variable months.  Must be included in the monthly NDVI variable names
classFiles = [classFolder + "urbanClass.tif",classFolder + "forestClass.tif", classFolder + "shrubClass.tif", classFolder + "grasslandClass.tif", 
              classFolder + "hayClass.tif", classFolder + "cropClass.tif", classFolder + "wetlandsClass.tif"]

# classifications were collapsed into more general categories of interest (e.g. low, mid, and high urban collapsed into urban).  Range of collapsable
# values were defined as max and min of the ranges, defined by the following variables
outputMins = [21,41,52,71,81,82,90]
outputMaxs = [24,43,52,71,81,82,95]

# environmental variables and checkout extension libraries
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

############### helper functions ################



# Create a binary raster from select categorical values in input classification image.
# The result contains 1 for values that fall within the input minimum and maximum values
# (inclusive), 0 otherwise
# Inputs:
#    inRas (string) - complete filepath to input raster
#    extractMin (int) - lower bound for range of inclusive values
#    extractMax (int) - upper bound for range of inclusive values
#    outRas (string) - complete filepath for the output raster
def extractValueRange(inRas,extractMin,extractMax,outRas):
    # SQL clause used by ArcGIS
    whereClause = "VALUE >= " + str(extractMin) + " AND VALUE <= " + str(extractMax)
    # extract values from raster and save in output file
    tempExtract = arcpy.sa.ExtractByAttributes(inRas, whereClause)   
    tempRas = arcpy.sa.Con(arcpy.sa.IsNull(tempExtract),0, 1)
    tempRas.save(outRas)
    print("completed extracting values for the " + outRas + " outputfile")

# Craete type-specific NDVI rasters.  Rasters are created by multiplying NDVI
# rasters with binary classification rasters
# Inputs:
#    NDVIRas (ArcGIS layer) - layer containing NDVI values for the time interval of interest
#    typeRas (ArcGIS layer) - binary classification layer, with 1 for types of interest, 0 o.w.
#    outRas (string) - complete filepath for the output file to create
def calcTypeNDVI(NDVIRas,typeRas,outRas):
    tempRas = arcpy.sa.Times(NDVIRas,typeRas)
    tempRas.save(outRas)

################### main function ###############

def main():
    
    # for each monthly NDVI raster, create a folder to store values if the folder doesn't already exist
    for i in range(0,len(monthVars)):
        if not os.path.exists(NDVI_TypeFolder + monthVars[i] + "/"):
            os.mkdir(NDVI_TypeFolder + monthVars)
            
    # for each classification type defined in the classFiles array, create the binary classification rasters
    for i in range(0,len(classFiles)):
        extractValueRange(landClassRaster,outputMins[i],outputMaxs[i],classFiles[i])
        # for each monthly NDVI raster, calculate type-specific NDVI values and save in the output rasters
        for j in range(0,len(monthVars)):
            NDVI_Input = NDVI_GeneralFolder + monthVars[j] + "NDVI.tif"
            NDVI_Output = NDVI_TypeFolder + monthVars[j] + "/" + (classFiles[i][len(classFolder):len(classFiles[i]) - len("Class.tif")]) + "NDVI" + monthVars[j] + ".tif"
            calcTypeNDVI(NDVI_Input,classFiles[i],NDVI_Output)
    print("completed main function")
    
    
main()




############# end of extractLandTypes.py #################