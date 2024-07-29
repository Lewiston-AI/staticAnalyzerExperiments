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

import saDefs
import pandas as pd

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

def get_points():
    ptSource = 'R'
    ptSourceQuery = PIPointQuery(PICommonPointAttributes.PointSource, AFSearchOperator.Equal, ptSource )
    return find_points(ptSourceQuery)

def find_points(query: PIPointQuery) -> list:
    ptSource = 'R'
    ptSourceQuery = PIPointQuery(PICommonPointAttributes.PointSource, AFSearchOperator.Equal, ptSource )
    attributesToLoad = Array[str](len(saDefs.attrs))
    i = 0
    for attr in saDefs.attrs:
        attributesToLoad[i] = attr
        i = i + 1
    queries = Array[PIPointQuery](1)
    queries[0] = query

    points = PIPoint.FindPIPoints(piServer, queries, attributesToLoad)
    listOfPts = convert_pts_to_df(points, saDefs.attrs)

    return listOfPts


def convert_pts_to_df(points: Array[PIPoint], attrs: list) -> list:
    listOfPts = list()
    currentTime = AFTime('*')
    for pt in points:
        snapShot = pt.Snapshot()
        ptDict = convert_pt_to_dict(pt, saDefs.attrs)
        ptDict['snapshot'] = snapShot.Value
        ptDict['snapshot time'] = snapShot.Timestamp.UtcSeconds
        ptDict['snapshot IsGood'] = snapShot.IsGood
        dt = int(currentTime.UtcSeconds - snapShot.Timestamp.UtcSeconds)
        ptDict['snapshot DT'] = dt
        listOfPts.append(ptDict)
    return listOfPts

def convert_pt_to_dict(pt: PIPoint, attrs: list) -> dict:
    print(pt)
    retDict = dict()
    for attr in attrs:
        attrValue = pt.GetAttribute(attr)
        retDict[attr] = attrValue
    return retDict

