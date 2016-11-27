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



# import modules
import arcpy
import os
import sys

# define environmental variables
arcpy.env.overwriteOutput = True

# folder paths and environmental variables
baseFolder = os.path.dirname(sys.argv[0]) + "/"
participantData = baseFolder + "hotspotInput.shp" # input file containing time-location data 
outputFile = baseFolder + "hotspotZones.csv" # name and folder path for final results
hotspotShapefile = baseFolder + "hotSpots.shp"
outputShapefile = baseFolder + "addedHotspots.shp"
ID_ATTRIBUTE = 'study_labe' # attribute field in input file that identifies which individual a sample point belongs to
TIME_ATTRIBUTE = "dTime" # attribute field that identifies amount of time associated with a sample point
SPOT_RADIUS = 10000 # radius of the hotspot, in units of meters
TIME_CUTOFF = 17 # percentage of time cut off for identifying hotspots. 
CSV_DICT = ["latitude","longitude","percTime","zoneVal","studyLabel"] # values to include in output csv
ID_HOTSPOT = '"studyLabel"'
ZONE_ATTRIBUTE = '"zoneVal"'
SEP = "," # separator for the output csv
NEW_LINE = "\n" # new line character for writing the output csv

# custom class containing information relevant to hotspots
class hotSpot:
    # instantiate a hotspot
    def __init__(self,inLat,inLong,inZoneVal,inPercTime,inStudyLabel,inNearbyPts):
        self.latitude = inLat
        self.longitude = inLong
        self.zoneVal = inZoneVal
        self.percTime = inPercTime 
        self.studyLabel = inStudyLabel
        self.nearbyPoints = inNearbyPts
    
    ########### custom functions ############
    
    # identify other potential hotspots that are nearby
    def isNearby(self,comparePt):
        if(comparePt in self.nearbyPoints):
            return(True)
        return(False)
    
    ########## getters and setters ##########
    def getLatitude(self):
        return(self.latitude)
    
    def getLongitude(self):
        return(self.longitude)
    
    def getNearbyZones(self):
        return(self.nearbyPoints)
    
    def getStudyLabel(self):
        return(self.studyLabel)
        
    def getPercTime(self):
        return(self.percTime)
    
    def setZoneVal(self,inZoneVal):
        self.zoneVal = inZoneVal
        
    def getZoneVal(self):
        return(self.zoneVal)
    
    def setZoneVal(self,inZoneVal):
        self.zoneVal = inZoneVal
        
    
########### end of the hotspot custom class ##########    

################### helper functions ###############    
    
    

# Sort hotspots in descending order by the percentage of time included within the 
# hotspot radius.  The output is the same as the input, but sorted by percent time 
# Inputs:
#    inHotspots (hotspot array) - an array of HotSpot objects
# Outputs:
#    inHotspots (hotspot array) - the same array as the input array, but ordered
#    by percentage of time covered
def prioritizeHotspots(inHotspots):
    nonSortedPercents = [0]*len(inHotspots)
    for i in range(0,len(inHotspots)):
        nonSortedPercents[i] = inHotspots[i].getPercTime()
    sortedPercents = sorted(nonSortedPercents,reverse = True)
    for i in range(0,len(inHotspots)):
        inHotspots[i].setZoneVal(sortedPercents.index(nonSortedPercents[i]))
    return(inHotspots)



# Write output csv file of hotspot datapoints
# Inputs:
#    inAllHotSpts (object array) - array of hotspot objects
#    inFilepath (string) - filepath and filename of the resulting csv file
def writeCSV(inAllHotSpots,inFilepath):
    
    i = 0
    # create an output stream object
    ofStream = open(inFilepath, 'wb')
    
    # write the csv header
    for i in range(0,len(CSV_DICT)-1):
        ofStream.write(CSV_DICT[i])
        ofStream.write(SEP)
    ofStream.write(CSV_DICT[len(CSV_DICT)-1])
    ofStream.write(NEW_LINE)
    
    # for each participant in the hotspot array
    for participantHotSpots in inAllHotSpots:
        
        # for each hotspot in the current participant, write the hotspot data into the 
        # output stream
        for hotSpot in participantHotSpots:
            ofStream.write(str(hotSpot.getLatitude()))
            ofStream.write(SEP)
            ofStream.write(str(hotSpot.getLongitude()))
            ofStream.write(SEP)
            ofStream.write(str(hotSpot.getPercTime()))
            ofStream.write(SEP)
            ofStream.write(str(hotSpot.getZoneVal()))
            ofStream.write(SEP)
            ofStream.write(hotSpot.getStudyLabel())
            ofStream.write(NEW_LINE)
    ofStream.close()   
    
    print("completed writing output file: " + inFilepath)
    
    

# calculate the sum of time covered by sampling events for a given participant 
# in the dataset.  
# Inputs:
#    inData (shapefile) - shapefile containing participant data, including 
#    amount of time associated with each sampling event
#    inTimeField (string) - name of the attribute field in the shapefile that 
#    containins the amount of time associated with each observation point
#    inId (string) - ID tag associated with the participant of interest.  Used
#    to screen the input file for data from a particular participant
# Outputs:
#    sumVal (float) - the total amount of time, in seconds covered by sampling
#    events for the participant associated with inID
def calcTotalTime(inData,inTimeField,inID):
    sumVal = 0
    numObs = 0
    
    # for each observation point in the shapefile, add the amount of time 
    # associated with the point to the running sum 
    with arcpy.da.SearchCursor(inData, inTimeField) as cursor:
        
        for row in cursor:
            try:
                sumVal += float(row[0])
            except:
                sumVal = sumVal
            numObs +=1
        
        if(numObs>0):
            del row
        del cursor   
    print("the total sample time for participant "  + str(inID) + " is : " + str(sumVal) + " seconds")
    return(sumVal) 




# extract time and user id from each observation point 
# Inputs:
#   inData (shapefile) - input shapefile data to extract value from
# Outputs:
#    FIDArray (integer array) - FID values for all of the inputs
#    dTimeArray (float array) - array of times associated with the observations
def getRowsAndDTime(inData):
    numRows = int(arcpy.GetCount_management(inData).getOutput(0))
    FIDArray = [0]*numRows
    dTimeArray = [0]*numRows
    index = 0
    
    # for each observation, extract the FID value and the amount of time associated by the observations
    with arcpy.da.SearchCursor(inData, ["FID",TIME_ATTRIBUTE]) as cursor:
        
        for row in cursor:
            FIDArray[index] = row[0]
            try:
                dTimeArray[index] = float(row[1])
            except:
                dTimeArray[index] = dTimeArray[index]
            index +=1
            del row
        del cursor 
    return([FIDArray,dTimeArray])
    
    
    
# identify the hotspots for a single participant
# Inputs:
#    inData (shapefile) - shapefile containing all datapoints
#    inID (string) - tag used to identify the 
# Outputs:
#    hotspots (hotspot array) - array of hotspots for the participant identified by inID
def identifyHotSpots(inData,inID):
    
    # screen inData for points that belong to the participant identified by inID
    whereClause =  ID_ATTRIBUTE + "=" + "'" + inID + "'"
    tempSubset = "idSubset"
    tempPoint = "singlePoint"
    tempTable = "in_memory/tempTable"
    arcpy.MakeFeatureLayer_management(inData,tempSubset,whereClause)
    numRows = int(arcpy.GetCount_management(tempSubset).getOutput(0))
    totalTime = calcTotalTime(tempSubset,TIME_ATTRIBUTE,inID)
    [FIDArray,timeArray] = getRowsAndDTime(tempSubset) # get the time associated with each observation point
    candidateHotSpots = []
    
    # for each observation point associated with the current participant of interest
    for FID in FIDArray:
        
        # screeen the input dataset for one data point at a time
        whereClause = "FID = " + str(FID)
        arcpy.MakeFeatureLayer_management(tempSubset,tempPoint,whereClause)
        with arcpy.da.SearchCursor(tempPoint, TIME_ATTRIBUTE) as cursor:
            for row in cursor:
                bufferTime = row[0]
            del row
        del cursor        
        # identify all other datapoints within SPOT_RADIUS meters and store the results in a table 
        arcpy.GenerateNearTable_analysis(tempPoint,tempSubset,tempTable,str(SPOT_RADIUS) + " Meter", 'NO_LOCATION', 'NO_ANGLE', "ALL")
        numRows2 = int(arcpy.GetCount_management(tempTable).getOutput(0))
        nearFIDS = [0]*numRows2
        index = 0
        
        # for each point nearby the main point of interest (i.e. within the hotspot buffer zone), add the point associated with the 
        # nearby point to the sum of times covered by the hostpot
        with arcpy.da.SearchCursor(tempTable, "NEAR_FID") as cursor:
           
            for row in cursor:
                nearFIDS[index] = row[0]
                bufferTime += timeArray[FIDArray.index(row[0])]
                index+=1
                del row
            del cursor
        percBufferTime = (bufferTime/totalTime)*100

        # if the percent of time covered by the hotspot is greater than the cutoff, then add the hotspot to the list of candidate hotspots
        if(percBufferTime > TIME_CUTOFF):    
            with arcpy.da.SearchCursor(tempPoint, ["latitude","longitude","FID",ID_ATTRIBUTE]) as cursor:

                for row in cursor:
                    candidateHotSpots.append(hotSpot(row[0],row[1],row[2],percBufferTime,row[3],nearFIDS))
                    del row
                del cursor

    # screen hotspot data to remove overlapping hotspots
    hotSpots = screenHotspots(candidateHotSpots) 
    print("completed identifying hotspots for participant" + str(inID))
    hotSpots = prioritizeHotspots(hotSpots)

    if(len(hotSpots) > 0):
        return(hotSpots)
    else:
        return("null")


# return a list of unique values
# Inputs:
#    inShapefile (shapefile) - shapefile containing all points of interest
#    inField (string) - name of the attribute field containing the data to return 
# Outputs:
#    sorted array of unique values for the attribute field of interest 
def uniqueValues(inShapefile, inField):
    with arcpy.da.SearchCursor(inShapefile, [inField]) as cursor:
        return sorted({row[0] for row in cursor})



# determine if two hotspots overlap
# Inputs:
#    inOverlap (int) - id value for the hotspot of interest
#    inAllHotSpts (hotspot array) - array of all hotspotss
# Outputs:
#    hotspot of interest 
def getCompareCandidate(inOverlap,inAllHotSpots):
    for i in range(0,len(inAllHotSpots)):
        if(inAllHotSpots[i].getZoneVal()==inOverlap):
            return(inAllHotSpots[i])
    return(False)



# compare a hotspot to other hotspots that may overap.  Return true
# if the candidate hotspot has the highest percent coverage compared 
# to overlapping hotspots, false otherwise.
# Inputs:
#    inCandidate (hotspot) - candidate hotspot object of interest
#    inAllHostpost (hotspot array) - array of candidate hotspots that might 
#    overlap the hotspot of interest
# Outputs:
#    true if the candidate hotspot has the highest percentage time coverage
#    compared to overlapping hotspots, false otherwise
def screenHotspot(inCandidate,inAllHotspots):
    overlapZones = inCandidate.getNearbyZones()
    
    # for each overlap zones, compare the overlap zone to overlapping hotspots.
    # return true if the candidate hotspot is the best option, false otherwise
    for overlap in overlapZones:
        compareCandidate = getCompareCandidate(overlap,inAllHotspots)
        if(compareCandidate != False and compareCandidate.getPercTime() > inCandidate.getPercTime()):
            return(False)
    return(True)
            


# screen all cadidate hotspots for potential overlapping candidate hotspots
# among the overlapping spots, keep the hotspots with the highest percentage
# time coverage
# Inputs:
#    inCandidates (hostpost array) - candidate array of hotspots
# Outputs:
#    finalList (hostpost array) - screened hotspot array, without overlap
def screenHotspots(inCandidates):
    finalList = []
    for candidate in inCandidates:
        if(screenHotspot(candidate,inCandidates)):
            finalList.append(candidate)
    return(finalList)
        
        
        
# join zone data to participant data
# Inputs:
#    inParticipants (string) - filepath to the shapefile with participant data  
#    inHotspots (string) - filepath to the shapefile with hotspot locations and statistics
#    outputFile (string) - filepath to the output shapefile
#    uniqueIds (string array) - array of values that uniquely identify which participant 
#    data comes from        
def assignZones(inParticipants, inHotspots, outputFile,uniqueIds):
    tempFiles = []
    
    # for each participant in the dataset, subset the participant data and hotspot data
    # for each participant, and add hotspot statistics to participant data 
    for idVal in uniqueIds:
    
        tempAllParticipants = "t_particip" + str(idVal) 
        whereClause =  ID_ATTRIBUTE + " = " + "'" + str(idVal) + "'"
        arcpy.MakeFeatureLayer_management(inParticipants,tempAllParticipants,whereClause)
        whereClause =  ID_HOTSPOT + " = " + "'" + str(idVal) + "'"
        tempBuffers = "t" + str(idVal)
        arcpy.MakeFeatureLayer_management(inHotspots, tempBuffers,whereClause)
        tempParticip2 = "in_memory/t_part_sub" + str(idVal)
        arcpy.SpatialJoin_analysis(tempAllParticipants,tempBuffers,tempParticip2,match_option= "WITHIN_A_DISTANCE_GEODESIC", 
                                   search_radius= str(SPOT_RADIUS) + " Meters")
        tempFiles.append(tempParticip2)

    arcpy.Merge_management(tempFiles,outputFile)
            
            
################# main function #################    


def main():
    uniqueIDs = uniqueValues(participantData,ID_ATTRIBUTE)
    hotSpotSets = []
    #for each participant in the study, calculate the hostpots for that participant
    for idVal in uniqueIDs:
            hotSpotSubset = identifyHotSpots(participantData,idVal)
            if(hotSpotSubset != "null"):
                hotSpotSets.append(hotSpotSubset)
            else:
                print("warning: no hotspots for participant " + str(idVal))
    writeCSV(hotSpotSets, outputFile)
    assignZones(participantData,hotspotShapefile,outputShapefile,uniqueIDs)
    print("completed main function")



    
    
main()


############## end of identifyHotspots.py ##################
