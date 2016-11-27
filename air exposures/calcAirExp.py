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


# import modules
import arcpy
import os
import sys 
import datetime
import time

# set environmental parameters
arcpy.env.workspace = r"in_memory/"
arcpy.env.overwriteOutput = True

# define filepaths 
baseFolder = os.path.dirname(sys.argv[0]) + "/"
participantShapefile = baseFolder + "exampleParticipant.shp"#"participantInput.shp" # input file containing participant points
TRIShapefile = baseFolder + "TRI_sites.shp" # shapefile containing TRI sites in Oregon
monitorShapefile = baseFolder + "AirMonitor.shp" # shapefile with air monitor measurements
resultsShapefile = baseFolder + "AirExpResults.shp" # output file for both the air monitor and TRI results

# constants
SEARCH_DISTANCE = "20000" # maximmum distance to search for TRI sites, in meters
tempPoint = "singlePoint" # file to temporarily store data for a single participant sample point
tempTable = "in_memory/tempTable" # file to temporarily store results of near analyses
TRI_FIELD = "TRI_exp" # name of the TRI exposure variable to add to the output file
TRI_AIR = "Total_Air" # name of the total air emissions variable in the TRI input shapefile
POLLUTANT_CATEGORY = "pollutant" # name of variable with pollutant type in the air monitor input shapefile
DATE_CATEGORY = "Date_Local" # name of the variable with date of air monitor/smartphone sample, in Y-m-d format
HOUR_CATEGORY = "Hour" # name of the variable with hour of air monitor/smartphone sample in H:MM format
TIME_CATEGORY = "when_time" # name of the variable that has epoch time of smartphone sammple (in ms)
MONITOR_VALUE = "Sample_Mea" # name of the variable with air monitor measurement level
DIST_NAMES = ["NO2_Dist","PM25_Dist"] # names of variables to store distance to air monitors (in meters) 
POLLUTANT_TYPES = ["NO2","PM25"] # names of pollutant types in air monitor shapefile



############### helper functions ##############

# for all records in a shapefile, set the values for a specified attribute
# Inputs:
#    inputFile (string) - filepath and name of the shapefile to update
#    fieldName (string) - name of the attribute field in the shapefile to update
#    inVal (array) - array of values, of the same type as the fieldName
def setVal(inputFile,fieldName,inVal):

            index = 0
            cur = arcpy.UpdateCursor(inputFile)
            
            # for each record in the shapefile, set the value of the attribute specified by the fieldname
            # to the value stored in inVal
            for row in cur:
                        row.setValue(fieldName, inVal[index])
                        cur.updateRow(row)
                        index+=1
            del row, cur


# add a variable to a shapefile. 
# Inputs:
#    inShapefile (string) - filepath to the shapefile 
#    inFieldName (string) - name of the variable to add to the shapefile
#    inType (string) - data type of the added variable (e.g. string, text)
#    inVals (array) - array of variable values
def addAttribute(inShapefile,inFieldName,inType,inVals):
            arcpy.AddField_management(inShapefile,inFieldName,inType) 
            setVal(inShapefile,inFieldName,inVals)    # add the attribute field to the final shapefile             



# add date and hour variables to an input shapefile.  The function transforms time stored in epoch format
# to two time variables; date, stored in Y-m-d format, and hour, stored in H:MM format (rounded to the nearest
# hour).  
# Inputs:
#    inShapefile (string) - filepath to the shapefile 
#    outputShapefile (string) - name of the shapefile with the added date and hour variables
def addDateAndHour(inShapefile,outShapefile):
            
            tempFile = "addHourTemp" # temporary in memory file
            arcpy.MakeFeatureLayer_management(inShapefile,tempFile)
            obsDates = [0]*int(arcpy.GetCount_management(tempFile).getOutput(0))
            dateVector = [0]*len(obsDates)
            hourVector = [0]*len(obsDates)
            index = 0
            # get a list of epoch time stamps and transform into datetime objects
            with arcpy.da.SearchCursor(tempFile, TIME_CATEGORY) as cursor:
                        for row in cursor:
                                    obsDates[index] = datetime.datetime.fromtimestamp(int(row[0]/1000))
                                    index+=1
                                    del row
                        del cursor
            # create date and time variables from epoch time stamps
            for index in range(0,len(obsDates)):
                        dateVector[index] = datetime.datetime.strftime(obsDates[index],"%Y-%m-%d")                      
                        hourVector[index] = datetime.datetime.strftime(obsDates[index] + datetime.timedelta(minutes=30),"%H") + ":00"
                        print(dateVector[0])
                        print(hourVector[0])
            # add date and hour variables to shapefile and store result as an output shapefile
            addAttribute(tempFile,DATE_CATEGORY,"String",dateVector)
            addAttribute(tempFile,HOUR_CATEGORY,"String",hourVector)
            arcpy.CopyFeatures_management(tempFile,outShapefile)
            
            
            
# calculate distance air monitors and sample point, as well as the nearest hourly measruement of the 
# corresponding air monitor, rounded to the nearest hour
# Inputs:
#    inShapefile (string) - name and filepath to the smartphone data shapefile
#    inAirMonitorFile (string) - name and filepath to the air monitor shapefile
#    outputShapefile (string) - name and filepath for the output shapefile
def calcAirMonitorExp(inSampleFile,inAirMonitorFile,outputShapefile):
            tempOutput = "tempOutput"
            addDateAndHour(participantShapefile,tempOutput) # add date and hour variables to the shapefile
            obsDates = [0]*int(arcpy.GetCount_management(tempOutput).getOutput(0)) 
            hourDates = [0]*int(arcpy.GetCount_management(tempOutput).getOutput(0))
            index = 0
            
            # get unique hours and dates of the smartphone dataset
            with arcpy.da.SearchCursor(tempOutput, [DATE_CATEGORY,HOUR_CATEGORY]) as cursor:
                        for row in cursor:
                                    obsDates[index] = row[0]
                                    hourDates[index] = row[1]
                                    index+=1
                                    del row
                        del cursor            
            
            # reduce to unique hours and dates
            obsDates = list(set(obsDates))
            hourDates = list(set(hourDates))
            
            # for each unique hour and date combination, identify nearest air monitor for each pollutant type, calculate distance to nearest
            # air monitor and corresponding air monitor measurement.  
            outerIndex=0            
            allFiles = []
            for obsDay in obsDates:
                        
                        for hour in hourDates:
                                    # subset participant data to points within the unique hour/day combination
                                    whereClause = HOUR_CATEGORY + " = '" + hour + "' AND " + DATE_CATEGORY + " = '" + obsDay  + "'"
                                    tempObs = "tempObs"  + str(outerIndex)
                                    arcpy.MakeFeatureLayer_management(inSampleFile,tempObs,whereClause)
                                    if(hour[0]) == '0':
                                                hour = hour[1:len(hour)]                                       
                                    if(int(arcpy.GetCount_management(tempObs).getOutput(0)) == 0):
                                                print("no datapoints to process for date " + str(obsDay) + " and hour " + str(hour))
                                    else:
                                                # for each pollutant type, subset the air monitor data to the hour/day of the participant data subset
                                                for pollutantType in POLLUTANT_TYPES:
                                                            whereClause = POLLUTANT_CATEGORY + " = '" + pollutantType + "' AND " + HOUR_CATEGORY + " = " + "'" + str(hour) + "'" + " AND " + DATE_CATEGORY + " = date " + "'" + obsDay + " 00:00:00'" 
                                                            tempLayer = "tempLayer" + str(outerIndex)
                                                            arcpy.MakeFeatureLayer_management(inAirMonitorFile,tempLayer,whereClause)
                                                            outerIndex +=1
                                                            tempTable = "nearTable"
                                                            
                                                            # identify nearest air monitor in the subset for each participant data point in the subset
                                                            arcpy.GenerateNearTable_analysis(tempObs,tempLayer,tempTable,closest="CLOSEST",method = "Geodesic")
                                                            nearestMeas = [0]*int(arcpy.GetCount_management(tempObs).getOutput(0))
                                                            nearestDist = [0]*int(arcpy.GetCount_management(tempObs).getOutput(0))
                                                            index = 0
                                                            tempFID = [0]*int(arcpy.GetCount_management(tempLayer).getOutput(0))
                                                            tempConc = [0]*int(arcpy.GetCount_management(tempLayer).getOutput(0))

                                                            with arcpy.da.SearchCursor(tempLayer, ["FID",MONITOR_VALUE]) as cursor:
                                                                        for row in cursor:
                                                                                    tempFID[index] = row[0]
                                                                                    tempConc[index] = row[1]
                                                                                    index+=1
                                                                                    del row
                                                                        del cursor   
                                                            index = 0

                                                            # for each of the nearest air monitor, get the distance to the nearest air monitor
                                                            # and use the air monitor id to find the corresponding air monitor measurement
                                                            with arcpy.da.SearchCursor(tempTable, ["NEAR_DIST","NEAR_FID"]) as cursor:
                                                                        for row in cursor:
                                                                                    nearestMeas[index] = tempConc[tempFID.index(row[1])]
                                                                                    nearestDist[index] = row[0]
                                                                                    index+=1
                                                                                    del row
                                                                        del cursor    
                                                            
                                                            # add the nearest air monitor measurements and distance to nearest air monitor to the 
                                                            # participant subset shapefile
                                                            addAttribute(tempObs,DIST_NAMES[POLLUTANT_TYPES.index(pollutantType)],"DOUBLE",nearestDist)
                                                            addAttribute(tempObs,pollutantType,"DOUBLE",nearestMeas) 
                                                            arcpy.Delete_management(tempLayer)
                                                allFiles.append(tempObs)
            # merge participant subset shapefile to create the final output product
            arcpy.Merge_management(allFiles,outputShapefile)
            print("finished calcAirMonitorExp")
           
                  



# calculate distance between sample points and nearest air monitor stations
# Inputs:
#    inShapefile (string) - filepath and name of the shapefile containing participant data
#    inTriFile (string) - filepath and name of the shapefile containing TRI data
def calcTRIExp(inShapefile,inTriFile):
            
            numTRIs = int(arcpy.GetCount_management(inTriFile).getOutput(0))
            TRI_exp = [0]*numTRIs
            index = 0
            
            # for each TRI site in the TRI shapefile, extract the TRI id and annual air emission values
            with arcpy.da.SearchCursor(inTriFile, ["FID", TRI_AIR]) as cursor:
                        for row in cursor:
                                    TRI_exp[row[0]] = row[1]
                                    index +=1
                                    del row
                        del cursor   
            
            numRows = int(arcpy.GetCount_management(inShapefile).getOutput(0))
            vals = [0]*numRows
            
            # for each FID in the input participant shapefile, calculate the intervese distance exposure
            for FID in range(0,numRows):
                        whereClause = "FID = " + str(FID)
                        arcpy.MakeFeatureLayer_management(inShapefile,tempPoint,whereClause)    
                        arcpy.GenerateNearTable_analysis(tempPoint,inTriFile,tempTable, str(SEARCH_DISTANCE) + " Meters", 'NO_LOCATION', 'NO_ANGLE', "ALL", method = "Geodesic")
                        
                        # for each TRI site within the search radius, add the distance and air emissions to the inverse distance exposure                    
                        with arcpy.da.SearchCursor(tempTable, ["NEAR_FID","NEAR_DIST"]) as cursor:
                                    for row in cursor:
                                                vals[FID] = vals[FID] + TRI_exp[row[0]]/(row[1])
                                                del row
                        del cursor   
            arcpy.AddField_management(inShapefile,TRI_FIELD,"DOUBLE") 
            setVal(inShapefile,TRI_FIELD,vals)
            
            
############################ main function ###############            
            
            
def main():
            calcTRIExp(participantShapefile,TRIShapefile)
            calcAirMonitorExp(participantShapefile,monitorShapefile,resultsShapefile)

main()

################## end of calcTRI.py ##################
