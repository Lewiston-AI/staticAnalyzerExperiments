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

def get_tags():
    ptSource = 'R'
    ptSourceQuery = PIPointQuery(PICommonPointAttributes.PointSource, AFSearchOperator.Equal, ptSource )
    q2 = {ptSourceQuery,}
    aToL2 = {PICommonPointAttributes.Archiving,}
    attributesToLoad = Array[str](1)
    attributesToLoad[0] = PICommonPointAttributes.Archiving
    queries = Array[PIPointQuery](1)
    queries[0] = ptSourceQuery

    points = PIPoint.FindPIPoints(piServer, queries, attributesToLoad)
    for pt in points:
        print(pt)
    return points