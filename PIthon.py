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

import numpy as np
import saDefs
import pandas as pd
import math

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
    tag = '*'
    tagQuery1 = PIPointQuery(PICommonPointAttributes.Tag, AFSearchOperator.Equal, tag )
    q1 = build_points_report([tagQuery1,])
    return q1

def get_reports3() -> (list, list):
    ptSource1 = 'R'
    ptSourceQuery1 = PIPointQuery(PICommonPointAttributes.PointSource, AFSearchOperator.Equal, ptSource1 )
    q1 = build_points_reports([ptSourceQuery1])

    #print_tags(q3)
    return q1

def print_tags(l: list):
    for p in l:
        print(f'\"{p[PICommonPointAttributes.Tag]}\",')

def build_points_reports(query: [PIPointQuery]) -> (list, dict):
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
        print(f'RecordedValues Error: {tag}')
        try:
            values = pt.RecordedValues(timeRange, AFBoundaryType.Outside, '', False)
            table = archive_values_to_list(values, pt.GetAttribute(PICommonPointAttributes.Span))
            dictOfTables[tag] = table
        except:
            print(f'\tRecordedValues Error: {tag}')
            dictOfTables[tag] = list() # empty list means unable to get data

    return dictOfTables

def archive_values_to_list(values: AFValues, span: float) -> list():
    table = list() # list of dictionaries (dict for each value)
    prevVal: AFValue = None
    for val in values:
        row = dict()
        row['value'] = val.Value
        row['time'] = val.Timestamp.UtcSeconds
        row['isgood'] = val.IsGood
        if prevVal != None:
            dt = int(val.Timestamp.UtcSeconds - prevVal.Timestamp.UtcSeconds)
            row['DT'] = dt
            if val.IsGood and prevVal.IsGood:
                dv = np.abs(prevVal.Value - val.Value)
                row['DV'] = dv
                row['DV/Span'] = dv / (span)
            else:
                row['DV'] = -1.0
                row['DV/Span'] = -1.0
        else:
            row['DT'] = -1.0
        prevVal = val
        table.append(row)
    return table

def points_meta_data_report(points: Array[PIPoint], attrs: list) -> list:
    listOfPts = list()
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
        except:
            ptDict['snapshot ln(DT)'] = -1
            print(f"unsupported dt {dt}")
        listOfPts.append(ptDict)
    return listOfPts

def convert_pt_to_dict(pt: PIPoint, attrs: list) -> dict:
    #print(pt)
    retDict = dict()
    for attr in attrs:
        try:
            attrValue = pt.GetAttribute(attr)
            retDict[attr] = attrValue
        except:
            retDict[attr] = ''
    return retDict

