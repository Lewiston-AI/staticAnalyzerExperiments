import sys
sys.path.append('C:\\Program Files (x86)\\PIPC\\AF\\PublicAssemblies\\4.0\\')
import clr
clr.AddReference('OSIsoft.AFSDK')

from OSIsoft.AF.PI import *
from OSIsoft.AF.Search import *
from OSIsoft.AF.Asset import *
from OSIsoft.AF.Data import *
from OSIsoft.AF.Time import *

attrs = [
        PICommonPointAttributes.Archiving,
        PICommonPointAttributes.Compressing,
        PICommonPointAttributes.CompressionDeviation,
        PICommonPointAttributes.CompressionMaximum,
        PICommonPointAttributes.CompressionMinimum,
        PICommonPointAttributes.CompressionPercentage,
        PICommonPointAttributes.Descriptor,
        PICommonPointAttributes.EngineeringUnits,
        PICommonPointAttributes.ExceptionDeviation,
        PICommonPointAttributes.ExceptionMaximum,
        PICommonPointAttributes.ExceptionMinimum,
        PICommonPointAttributes.ExceptionPercentage,
        PICommonPointAttributes.ExtendedDescriptor,
        PICommonPointAttributes.InstrumentTag,
        PICommonPointAttributes.Location1,
        PICommonPointAttributes.Location4,
        PICommonPointAttributes.PointID,
        PICommonPointAttributes.PointSource,
        PICommonPointAttributes.PointType,
        PICommonPointAttributes.SourcePointID,
        PICommonPointAttributes.Span,
        PICommonPointAttributes.Step,
        PICommonPointAttributes.Tag,
        PICommonPointAttributes.Zero,
    ]

defaultPoint: dict = {'archiving': 1, 'compressing': 1, 'compdev': 2.0, 'compmax': 28800, 'compmin': 0, 'compdevpercent': 2.0,
                'descriptor': '', 'engunits': '', 'excdev': 1.0, 'excmax': 600, 'excmin': 0, 'excdevpercent': 1.0,
                'exdesc': '', 'instrumenttag': '', 'location1': 0, 'location4': 0, 'pointid': 21993, 'pointsource': 'Lab',
                'pointtype': 12, 'srcptid': 0, 'span': 100.0, 'step': 0, 'tag': 'DefaultClassicTag', 'zero': 0.0}

def evaluate_for_defaults(point: dict) -> dict:
    defaults = dict()
    if point['compressing'] == defaultPoint['compressing'] and point['compdevpercent'] == defaultPoint['compdevpercent'] and \
            point['compmin'] == defaultPoint['compmin'] and point['compmax'] == defaultPoint['compmax']:
        defaults['compDefs'] = 1
    else:
        defaults['compDefs'] = 0
    if point['excdevpercent'] == defaultPoint['excdevpercent'] and \
            point['excmin'] == defaultPoint['excmin'] and point['excmax'] == defaultPoint['excmax']:
        defaults['excDefs'] = 1
    else:
        defaults['excDefs'] = 0
    if point['zero'] == defaultPoint['zero'] and point['span'] == defaultPoint['span']:
        defaults['zeroSpanDefs'] = 1
    else:
        defaults['zeroSpanDefs'] = 0
    return defaults

def update_defaults (point: dict):
    defs = evaluate_for_defaults(point)
    for name,value in defs.items():
        point[name] = value
