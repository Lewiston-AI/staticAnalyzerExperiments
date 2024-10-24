import sys
sys.path.append('C:\\Program Files (x86)\\PIPC\\AF\\PublicAssemblies\\4.0\\')
import clr
clr.AddReference('OSIsoft.AFSDK')

from OSIsoft.AF.PI import *
from OSIsoft.AF.Search import *
from OSIsoft.AF.Asset import *
from OSIsoft.AF.Data import *
from OSIsoft.AF.Time import *

from System import Array
from System import Type

import numpy as np
import saDefs
import pandas as pd
import math
import time

def connect_to_Server(serverName):
    piServers = PIServers()
    global piServer
    piServer = piServers[serverName]
    if piServer != None:
        piServer.Connect(False)
    else:
        print("unable to connect to: {serverName}")

def get_tag_snapshot(tagname):
    tag = PIPoint.FindPIPoint(piServer, tagname)
    lastData = tag.Snapshot()
    return lastData.Value, lastData.Timestamp

def get_def_point() -> list:
    tag = 'DefaultClassicTag'
    query = PIPointQuery(PICommonPointAttributes.Tag, AFSearchOperator.Equal, tag)
    defPt = find_points(query)
    return defPt

def get_reports1() -> (list, list):
    print('get_reports1')
    ptSource1 = 'R'
    ptSourceQuery1 = PIPointQuery(PICommonPointAttributes.PointSource, AFSearchOperator.Equal, ptSource1 )
    ptSource2 = '9'
    ptSourceQuery2 = PIPointQuery(PICommonPointAttributes.PointSource, AFSearchOperator.Equal, ptSource2 )
    ptSource3 = 'C'
    ptSourceQuery3 = PIPointQuery(PICommonPointAttributes.PointSource, AFSearchOperator.Equal, ptSource3 )
    q1 = build_points_reports([ptSourceQuery1])
    q2 = build_points_reports([ptSourceQuery2])
    q3 = build_points_reports([ptSourceQuery3])
    metaDatasReport = q1[0] + q2[0] + q3[0]
    q1[1].update(q2[1])
    q1[1].update(q3[1])

    #print_tags(q3)
    return (metaDatasReport, q1[1])

def get_reports2():
    print('get_reports2')
    tag = '*'
    tagQuery1 = PIPointQuery(PICommonPointAttributes.Tag, AFSearchOperator.Equal, tag )
    q1 = build_points_report([tagQuery1,])
    return q1

def get_reports3() -> (list, list):
    print('get_reports3')
    ptSource1 = 'R'
    ptSourceQuery1 = PIPointQuery(PICommonPointAttributes.PointSource, AFSearchOperator.Equal, ptSource1 )
    q1 = build_points_reports([ptSourceQuery1])

    #print_tags(q3)
    return q1

def print_tags(l: list):
    print('print_tags')
    for p in l:
        print(f'\"{p[PICommonPointAttributes.Tag]}\",')

def build_points_reports(query: [PIPointQuery]) -> (list, dict):
    print('build_points_reports')
    ptSource = 'R'
    ptSourceQuery = PIPointQuery(PICommonPointAttributes.PointSource, AFSearchOperator.Equal, ptSource )
    attributesToLoad = Array[str](len(saDefs.attrs))
    i = 0
    for attr in saDefs.attrs:
        attributesToLoad[i] = attr
        i = i + 1
    queries = Array[PIPointQuery](len(query))
    i = 0
    for q in query:
        queries[i] = q
        i = i + 1

    points1 = PIPoint.FindPIPoints(piServer, queries, attributesToLoad)
    metatDataReport = points_meta_data_report(points1, saDefs.attrs)

    #calling this again because I cannot figure out how to reset the IEnumerable points1, so getting a new one
    points2 = PIPoint.FindPIPoints(piServer, queries, attributesToLoad)
    archiveReport = points_archive_report(points2)

    return (metatDataReport, archiveReport)

def points_archive_report (points: Array[PIPoint]) -> dict:
    # if we get too many points in the Array, we would need to chunk the calls
    end = 'y'
    start = 'y-31d'
    timeRange = AFTimeRange(start, end)
    boundaryType: AFBoundaryType = 0
    filterExpression = ''
    includeFilteredValues = False
    pageSize = 100000
    pagingConfig = PIPagingConfiguration(PIPageType.TagCount, pageSize);
    maxCount = 0
#public AFValues RecordedValues(AFTimeRange timeRange, AFBoundaryType boundaryType, string filterExpression,
#   bool includeFilteredValues, int maxCount = 0);
    values: AFValues
    dictOfTables = dict()
    for pt in points:
        tag = pt.GetAttribute(PICommonPointAttributes.Tag)
        print(f'Getting RecordedValues for: {tag}')
        try:
            st1 = time.time()
            values = pt.RecordedValues(timeRange, AFBoundaryType.Outside, '', False)
            et1 = time.time()
            st2 = et1
            ptType = pt.GetAttribute(PICommonPointAttributes.PointType)
            table = archive_values_to_list1(values, ptType, pt.GetAttribute(PICommonPointAttributes.Span))
            et2 = time.time()
            dictOfTables[tag] = table

            print(f'Got RecordedValues for: {tag} in {et1 - st1} sec. Converted in {et2 - st2} {values.Count}')
        except Exception as ex:
            print(f'\tRecordedValues Error: {tag} {ex}')
            dictOfTables[tag] = list() # empty list means unable to get data

    return dictOfTables

def is_numeric(val: PIPointType):
    if (val == PIPointType.Float32) or (val == PIPointType.Float64) or (val == PIPointType.Int16) or (val == PIPointType.Int32):
        return True
    else:
        return False

def archive_values_to_list1(values: AFValues, ptType: PIPointType, span: float) -> list():
    table = list() # list of dictionaries (dict for each value)
    try:
        isNum = is_numeric(ptType)
        prevVal: AFValue = None
        for val in values:
            try:
                row = dict()
                row['value'] = val.Value
                row['time'] = val.Timestamp.UtcSeconds
                row['isgood'] = val.IsGood
                if prevVal != None:
                    dt = int(val.Timestamp.UtcSeconds - prevVal.Timestamp.UtcSeconds)
                    row['DT'] = dt
                    if val.IsGood and prevVal.IsGood and isNum:
                        dv = np.abs(prevVal.Value - val.Value)
                        row['DV'] = dv
                        row['DV/Span'] = dv / (span)
                    else:
                        row['DV'] = -1.0               # -1.0 that we can remove later, but make sure the table does not have missing fields
                        row['DV/Span'] = -1.0
                else:
                    row['DT'] = -1.0
                    row['DV'] = -1.0  # -1.0 that we can remove later, but make sure the table does not have missing fields
                    row['DV/Span'] = -1.0
                prevVal = val
                table.append(row)
            except Exception as ex:
                print(f'Converting AFValues error {ex}')
    except Exception as ex:
        print (f'Converting AFValues error {ex}')
    return table

def archive_values_to_list2(afValues: AFValues, ptType: PIPointType, span: float) -> list():
    try:
        ct = afValues.Count
        keys = ['value', 'time', 'isgood', 'DT', 'DV', 'DV/SPAN']
        #values = np.empty(ct, dtype=np.double)
        values = list()
        #times = np.empty(ct, dtype=np.double)
        times  = list()
        #isgoods = np.empty(ct, dtype=np.bool)
        isgoods = list()
        #dts = np.empty(ct, dtype=np.double)
        dts = list()
        #dvs = np.empty(ct, dtype=np.double)
        dvs = list()
        #dvspans = np.empty(ct, dtype=np.double)
        dvspans = list()
        isNum = is_numeric(ptType)
        prevVal: AFValue = None
        i = 0
        for val in afValues:
            #if val.IsGood:
            values.append(val.Value)
            #else:
            #    if i > 0:
            #        values[i] = values[1] # this does not matter except for later zero and span calcs
            #    else:
            #        values[i] = 0.0 # this could throw off zero/span calcs, we can get fancier for a replacement later
            times.append(val.Timestamp.UtcSeconds)
            isgoods.append(val.IsGood)
            if prevVal != None:
                dt = int(val.Timestamp.UtcSeconds - prevVal.Timestamp.UtcSeconds)
                dts.append(dt)
                if val.IsGood and prevVal.IsGood and isNum:
                    dv = np.abs(prevVal.Value - val.Value)
                    dvs.append(dv)
                    dvspans.append(dv / (span))
                else:
                    dvs.append(-1.0)              # -1.0 that we can remove later, but make sure the table does not have missing fields
                    dvspans.append(-1.0)
            else:
                dts.append(-1.0)  # TODO:
                dvs.append(-1.0)
                dvspans.append(-1.0)
            prevVal = val
            i = i + 1
    except Exception as ex:
        print (f'Converting AFValues error {ex}')
    parallelArrays = [values, times, isgoods, dts, dvs, dvspans]
    table = [dict(zip(keys, parallelArrays)) for parallelArrays in zip(*parallelArrays)]
    return table

def points_meta_data_report(points: Array[PIPoint], attrs: list) -> list:
    listOfPts = []
    currentTime = AFTime('*')
    for pt in points:
        #snapShot = pt.Snapshot()
        snapShot = pt.CurrentValue()
        ptDict = convert_pt_to_dict(pt, attrs)
        ptDict['snapshot'] = snapShot.Value
        ptDict['snapshot time'] = snapShot.Timestamp.UtcSeconds
        ptDict['snapshot IsGood'] = snapShot.IsGood
        dt = int(currentTime.UtcSeconds - snapShot.Timestamp.UtcSeconds)
        ptDict['snapshot DT'] = dt
        try:
            ptDict['snapshot ln(DT)'] = np.log(dt)  # np.log is the natural log
        except Exception as ex:
            ptDict['snapshot ln(DT)'] = -1
            print(f"unsupported dt {dt} {ex}")
        listOfPts.append(ptDict)
    return listOfPts

def convert_pt_to_dict(pt: PIPoint, attrs: list) -> dict:
    #print(pt)
    retDict = dict()
    for attr in attrs:
        try:
            attrValue = pt.GetAttribute(attr)
            retDict[attr] = attrValue
        except Exception as ex:
            print(f'converstion error {ex}')
            retDict[attr] = ''
    return retDict

