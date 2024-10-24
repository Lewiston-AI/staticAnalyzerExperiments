import numpy as np
import pandas as pd
import math
def is_string(x):
    return isinstance(x, str)

def add_arc_summary(arcDF: pd.DataFrame, ptData: dict):
    #print(arcDF.head())
    set_fields(ptData)
    try:
        t = arcDF['time'].to_numpy()
        v = arcDF['value'].to_numpy()
        g = arcDF['isgood'].to_numpy()
        dt = arcDF['DT'].to_numpy()
        dv = arcDF['DV'].to_numpy()
        tmp = arcDF['DV/Span']
        dvspan = arcDF['DV/Span'].to_numpy()
    except Exception as ex:
        print(f'\tadd_arc_summary Error: {ex}')

    totalTime = 0
    if len(t) > 2:
        totalTime = t[len(t)-1] - t[0]
    # remove the bad values
    t = t[g]
    v = v[g]
    v.sort()
    dt = dt[g]
    dt = dt[dt >= 0.0]  # remove -1 that may have been set as placeholders
    dt.sort()
    dv = dv[g]
    dv = dv[dv >= 0.0] # remove -1 that may have been set as placeholders
    dv.sort()
    dvspan = dvspan[g]
    dvspan = dvspan[dvspan >= 0.0] # remove -1 that may have been set as placeholders
    dvspan.sort()
    # make sure we have enough data
    if len(t) < 5 or len(v) < 5 or len(dt) < 2 or len(dv) < 2:
        print('not enough samples')
        return

    #mask = np.vectorize(is_string)(dv) if needed we can use this to remove strings from the array
    #dv = dv[~mask]

    # We need to calculate the following from the above arrays:
    # observed zero
    # observed span
    obsZero = v.min()
    ptData['obsZero'] = obsZero
    obsSpan = v.max() - obsZero
    ptData['obsSpan'] = obsSpan
    # 99% zero
    # 99% span
    obsZero99 = np.percentile(v, 1.0)
    ptData['99% obsZero'] = obsZero99
    obsSpan99 = np.percentile(v, 99.0) - obsZero99
    ptData['99% obsSpan'] = obsSpan99
    # sample count
    samples = len(t)
    ptData['samples'] = samples
    # sample period
    totalT = dt.sum()
    samplePer = totalT/samples
    ptData['samplePer'] = samplePer
    # percent good
    percentGood = (totalT/totalTime) * 100
    ptData['percent good'] = percentGood
    # minimum delta time (while good)
    minDT = dt.min()
    ptData['minDT'] = minDT
    ptData['ln(minDT)'] = np.log(minDT)
    minDT1 = np.percentile(dt, 1.0)
    ptData['1% minDT'] = minDT1
    ptData['ln(1% minDT)'] = np.log(minDT1)
    # minimum delta value
    minDV = dv.min()
    ptData['minDV'] = minDV
    ptData['normalized minDV'] = 100*(minDV/obsSpan)
    minDV1 = np.percentile(dv, 1.0)
    ptData['1% minDV'] = minDV1
    ptData['normalized 1% minDV'] = 100*(minDV1/obsSpan99)
    # maximum delta time (while good)
    ptData['maxDT'] = dt.max()
    # maximum delta value (while good)
    ptData['maxDV'] = dv.max()
    ptData['normalized maxDV'] = 100*(dv.max()/obsSpan)
    # 99% zero normalized to zero attribute
    # 99% span normalized to span attribute
    print(ptData)

def set_fields(d: dict):
    d['obsZero'] = ''
    d['obsSpan'] = ''
    d['99% obsSpan'] = ''
    d['99% obsZero'] = ''
    d['samples'] = ''
    d['samplePer'] = ''
    d['percent good'] = ''
    d['minDT'] = ''
    d['minDV'] = ''
    d['normalized minDV'] = ''
    d['maxDT'] = ''
    d['maxDV'] = ''
    d['normalized maxDV'] = ''
    d['1% minDT'] = ''
    d['ln(1% minDT)'] = ''
    d['1% minDV'] = ''
    d['normalized 1% minDV'] = ''