######### processMODIS.py ############
# Author: Andrew Larkin
# Developed for Laurel Kincl, Oregon State University
# Date last modified: September 20th, 2016
# Description: The purpose of this script is to download daily Level 2 MODIS atmosphere 
# products from the designated NASA FTP site.  Files are downloaded in .hdf foormat
# Only files within the spatial and temporal extent of interest are downloaded.  
# Files must be downloaded separately for aqua and terra satellites
######################################


######### setup ##########

# import packages
import datetime
from datetime import datetime
import sys
import os
import urllib2
import arcpy

# define constants
folder = os.path.dirname(sys.argv[0]) + "/" # designated folder to store all MODIS-related data
#FTP = "ftp://ladsweb.nascom.nasa.gov/allData/6/MYD04_L2/"
FTP = "ftp://ladsweb.nascom.nasa.gov/allData/6/MOD04_L2/" # ftp site containing .hdf files 

FILESTART = "MOD04_L2" #"MYD04_L2" # the first 8 characters of every .hdf file.  Used for searching through file lists.
# note that the first eight characters differ for aqua (MOD04_L2) and terra (MYD04_L2)

# start and end dates for the time period of interest
START_DATE = "01-08-2015"
END_DATE = "31-10-2015"

# latitude and longitude boundaries for the study area of interest
LAT_MAX = 46.2
LAT_MIN = 41.5
LONG_MAX = -116
LONG_MIN = -124

# variables names of latitude and longitude boundaries in the .hdf metadata
LATITUDE_BOUND = "GRINGPOINTLATITUDE"
LONGITUDE_BOUND = "GRINGPOINTLONGITUDE"

# folder to store .hdf files
outputFolder = folder + "MODIS_files/"

############### helper functions ###############


# Description: The FTP folder structure names files acoording to Julian date of the aquired image.
# This function takes the startDate and endDate and inputs, and returns the list of folders within
# the FTP site that may contain .hdf files that fall within the time interval of interest
# INPUTS:
#    startDate - startDate for the time interval of interest, in day-month-year format
#    endDate - endDate for the time interval of interest, in day-month-year format
# OUTPUTS:
#    list of output folders, string array format
def identifyFolders(startDate, endDate):
    a = datetime.strptime(startDate, "%d-%m-%Y")    
    b = datetime.strptime(endDate, "%d-%m-%Y")
    return(range(int(a.strftime("%j")),int(b.strftime("%j"))+1))

    
    
# Description: Given an input file with .hdf metadata, find the latitude bounds.
# INPUTS:
#    metaString - a string object containing the metadata
# OUTPUTS:
#    latBounds - a 2D float array with the minimum and maximum latitude bounds 
#                for the .hdf file
def getLatBounds(metaString):
    latIndex = 0 
    latBounds = [9999,-9999]
    latIndex = str(metaString).find(LATITUDE_BOUND,latIndex) # LATITUDE_BOUND is a global constant
    endIndex = str(metaString).find(LATITUDE_BOUND,latIndex + 1 + len(LATITUDE_BOUND))
    subIndex = metaString[latIndex:endIndex] 
    latIndex = str(subIndex).find("(")
    endIndex = str(subIndex).find(")")
    subIndex2 = subIndex[latIndex+1:endIndex]
    latIndex = 0
    
    # search through metaString for all latitude values and update the min and max latBounds as
    # necessary
    while(endIndex != -1):
        endIndex = str(subIndex2).find(",",latIndex+1)
        testFloat = float(str(subIndex2[latIndex:endIndex]))
        latIndex = endIndex +1

        # if the candidate latitude value is less than the current minimum latitude bound, 
        # update the minimum latitude bound
        if(testFloat < latBounds[0]):
            latBounds[0] = testFloat
        # if the candidate latitude value is greater than the current maximum latitude bound, 
        # update the maximum latitude bound            
        if(testFloat > latBounds[1]):
            latBounds[1] = testFloat
    
    return(latBounds)



# Description: Given an input file with .hdf metadata, find the longitude bounds.
# INPUTS:
#    metaString - a string object containing the metadata
# OUTPUTS:
#    latBounds - a 2D float array with the minimum and maximum latitude bounds 
#                for the .hdf file
def getLonBounds(metaString):
    lonIndex = 0 
    lonBounds = [9999,-9999]
    lonIndex = str(metaString).find(LONGITUDE_BOUND,lonIndex)
    endIndex = str(metaString).find(LONGITUDE_BOUND,lonIndex + 1 + len(LONGITUDE_BOUND))
    subIndex = metaString[lonIndex:endIndex]
    lonIndex = str(subIndex).find("(")
    endIndex = str(subIndex).find(")")
    subIndex2 = subIndex[lonIndex+1:endIndex]
    lonIndex = 0
    
    # search through metaString for all latitude values and update the min and max longBounds as
    # necessary    
    while(endIndex != -1):
        endIndex = str(subIndex2).find(",",lonIndex+1)
        testFloat = float(str(subIndex2[lonIndex:endIndex]))
        lonIndex = endIndex +1
        
        # if the candidate latitude value is less than the current minimum latitude bound, 
        # update the minimum latitude bound        
        if(testFloat < lonBounds[0]):
            lonBounds[0] = testFloat
            
        # if the candidate latitude value is greater than the current maximum latitude bound, 
        # update the maximum latitude bound         
        if(testFloat > lonBounds[1]):
            lonBounds[1] = testFloat
    return(lonBounds)    


    
# Description: Determine if the one dimension of the study area extent and the .hdf spatial
# extent overlap
# INPUTS:
#    bounds - a 2d float array with lower and upper bounds of the .hdf file
#    minComp - lower bound for the study area
#    maxComp - upper bound for the study area
# OUTPUTS:
#    boolean indicator of whether .hdf file extent and the study extent overlap for 
#    the dimension of interest
def boundsCheck(bounds,minComp,maxComp):
    if((bounds[0] < minComp) & (bounds[1] > minComp)):
        return True
    if((bounds[0] < maxComp) & (bounds[1] > maxComp)):
        return True    
    return False
    
    
    
# Description: Determine if the study area coordinates are within the .hdf file coordinates
# INPUTS:
#    latMin (float) - lower latitude bound for the study area
#    latMax (float) - upper latitude bound for the study area
#    longMin (float) - lower longitude bound for the study area
#    longMax (float) - upper longitude bound for the study area
#    inputURL (string) - string representation of FTP link to .hdf file
# OUTPUTS:
#    boolean indicator of whether .hdf file extent and the study extent overlap    
def rangeCheck(latMin,latMax, longMin, longMax, inputURL):
    tempFile = urllib2.urlopen(inputURL).read()
    # check if the latitude dimension overlaps
    latBounds = getLatBounds(tempFile)
    isValid = boundsCheck(latBounds,latMin,latMax)
    if(isValid):
        # check if the longitude dimension overlaps
        lonBounds = getLonBounds(tempFile)
        isValid = boundsCheck(lonBounds,longMin,longMax)
    return(isValid)
    
    
    
# Description: create a list of all .hdf files associated with a specific julian date
# INPUTS:
#    folder (string) - FTP path to the folder that potentially contains .hdf files
# OUTPUTS:
#    string array of .hdf file names contained within the folder of interest    
def getHDFList(folder):
    hdfList = []
    endIndex = 1
    index = 0
    hdfText = urllib2.urlopen(folder).read()
    while(endIndex != -1):
        index = str(hdfText).find(FILESTART,index)
        endIndex = str(hdfText).find(".hdf",index)
        hdfList.append(hdfText[index:endIndex+4])
        index = endIndex + 5
    hdfList = hdfList[0:len(hdfList)-1]    
    return(hdfList)
   
   
   
############### main function #############


    
def main():        
    # convert start and end date to julian format, get an array of julian dates that 
    # cover the time period of interest
    dateRange = identifyFolders(START_DATE,END_DATE)
    dateRange = dateRange[0:len(dateRange)]
    
    # for each day in the time interval of interest 
    for dateVal in dateRange:
        # get a list of hdf files associated with the specific da
        tempFolder = FTP + "2015/" + str(dateVal) + "/"
        hdfList = getHDFList(tempFolder)
        print(hdfList)
        i=0
        # for each hdf file in the generated list, check if it's spatial extent overlaps the study area.
        # if they overlap, download the hdf file
        for hdfFile in hdfList:
            isInRange = rangeCheck(LAT_MIN, LAT_MAX, LONG_MIN, LONG_MAX, tempFolder + hdfFile)
            if(isInRange):
                outputFile = outputFolder + "MODIS" + str(dateVal) + "n" + str(i) + ".hdf"
                f = open(outputFile,'wb')    
                f.write(urllib2.urlopen(tempFolder + hdfFile).read())
                f.close()           
                i+=1
            
main()


########### end of processMODIS.py ##########