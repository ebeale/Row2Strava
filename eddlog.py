#!/usr/bin/env python
#Copyright (c) 2011, Sam Gambrell
#Licensed under the Simplified BSD License.

#This is an example file to show how to make use of pyrow
#Have the rowing machine on and plugged into the computer before starting the program
#The program will record Time, Distance, SPM, Pace, and Force Data for each
#stroke and save it to 'workout.csv'

# NOTE: This code has not been thoroughly tested and may not function as advertised.
# Please report and findings to the author so that they may be addressed in a stable release.

# import os
# import sys
# sys.path.insert(0, os.path.abspath('..'))
from pyrow import pyrow
from rowingdata.rowingdata import rowingdata as rowingdataclass
import rowingdata

import time

def wait_for_workout_start(erg):
    #Loop until workout has begun
    workout = erg.get_workout()
    print("wait_for_workout_start: workout['state'] = " + str(workout['state']))
    while workout['state'] == 0:
        time.sleep(0.4)
        workout = erg.get_workout()
        #print("wait_for_workout_start: workout['state'] = " + str(workout['state']))
    print("wait_for_workout_start: Workout has begun")

def wait_for_stroke_start(erg):
    forceplot = erg.get_forceplot()
    workout = erg.get_workout()
    print("wait_for_stroke_start: forceplot['strokestate'] = " + str(forceplot['strokestate']) + " workout['state'] = " + str(workout['state']))
    #Loop while waiting for stroke
    while forceplot['strokestate'] != 2 and workout['state'] == 1:
        time.sleep(0.2)
        forceplot = erg.get_forceplot()
        workout = erg.get_workout()
        print("wait_for_stroke_start: forceplot['strokestate'] = " + str(forceplot['strokestate']) + " workout['state'] = " + str(workout['state']))
    print("wait_for_stroke_start: Starting Stroke")


def wait_for_stroke_end(erg):
    forceplot = erg.get_forceplot()
    workout = erg.get_workout()
    print("wait_for_stroke_end: forceplot['strokestate'] = " + str(forceplot['strokestate']) + " workout['state'] = " + str(workout['state']))
    #Loop during stroke
    while forceplot['strokestate'] == 2:
        time.sleep(0.2)
        forceplot = erg.get_forceplot() 
        workout = erg.get_workout()
        print("wait_for_stroke_end: forceplot['strokestate'] = " + str(forceplot['strokestate']) + " workout['state'] = " + str(workout['state']))
    print("wait_for_stroke_end: Done Stroke")


def write_file_header(write_file):
    #Write data to write_file
    write_file.write('index,TimeStamp (sec), Horizontal (meters), Cadence (stokes/min), Stroke500mPace (sec/500m), Power (watts), HRCur (bpm), ElapsedTime (sec)\n')

def write_file_row(erg, rowindex, write_file):
    monitor = erg.get_monitor() #get monitor data to output
    #Write data to write_file
    workoutdata = str(rowindex) + "," + str(time.time() + monitor['time']) + "," + str(monitor['distance']) + "," + str(monitor['spm']) + ","  + \
        str(monitor['pace']) + "," + str(monitor['power']) + "," + str(monitor['heartrate']) + "," + str(monitor['time'])

    print("Writing: " + str(workoutdata))
    write_file.write(workoutdata + '\n')


def main():
    rowerFile="defaultrower.txt"
    rower=rowingdata.getrower(rowerFile)

    #Connecting to erg
    ergs = list(pyrow.find())
    if len(ergs) == 0:
        exit("No ergs found.")

    erg = pyrow.PyErg(ergs[0])
    print("Connected to erg.")

    while True:

        wait_for_workout_start(erg=erg)

        # Now open and prepare csv file with current timestamp
        filename = "workout_" + str(time.time())
        filename_csv = filename + ".csv"
        write_file = open(filename_csv, 'w')

        write_file_header(write_file=write_file)

        index = 0
        rows_written = False

        # Get initial workout state
        workout = erg.get_workout()

        #Loop until workout ends
        while workout['state'] == 1:

            write_file_row(erg=erg, rowindex=index, write_file=write_file) # write out the row
            rows_written = True

            wait_for_stroke_start(erg=erg)

            wait_for_stroke_end(erg=erg)

            # Get workout state
            workout = erg.get_workout()
            index = index + 1
        
        print("Workout has ended")
        write_file.close()

        if rows_written == True:
            # Now use rowingdata to convert this to TCX
            res=rowingdata.rowingdata(filename_csv,rowtype="Indoor Rower",
                                    rower=rower)
            filename_tcx=filename+".tcx"
            res.exporttotcx(filename_tcx)


if __name__ == '__main__':
    main()
