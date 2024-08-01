import numpy as np
import pandas as pd
import math
def is_string(x):
    return isinstance(x, str)

def add_arc_summary(arcDF: pd.DataFrame, ptData: dict):
    ptData['obsZero'] = ''
    ptData['obsSpan'] = ''
    ptData['samples'] = ''
    ptData['samplePer'] = ''
    ptData['minDT'] = ''
    ptData['minDV'] = ''
    ptData['normalized minDV'] = ''
    ptData['maxDT'] = ''
    ptData['maxDV'] = ''
    ptData['normalized maxDV'] = ''
    t = arcDF['time'].to_numpy()
    v = arcDF['value'].to_numpy()
    g = arcDF['isgood'].to_numpy()
    if len(g) < 2:
        return
    dt = arcDF['DT'].to_numpy()
    dv = arcDF['DV'].to_numpy()
    # remove the bad values
    t = t[g]
    if len(t) < 2:
        return
    v = v[g]
    if len(v) < 2:
        return
    v.sort()
    dt = dt[g]
    dt = dt[dt != '']
    if len(dt) < 2:
        return
    dv = dv[g]
    if len(dv) < 2:
        return
    #mask = np.vectorize(is_string)(dv)
    #float_arr = dv[~mask]
    #dv = float_arr
    #dv = np.delete(dv, [0]) # get rid of the nan
    dt = dt[dt >= 0]
    dt.sort()
    dv = dv[dv >= 0.0] #not sure why this does not work
    dv.sort() #crashed with a string value

    # We need to calculate the following from the above arrays:
    # observed zero
    obsZero = v.min()
    ptData['obsZero'] = obsZero
    # observed span
    obsSpan = v.max() - obsZero
    ptData['obsSpan'] = obsSpan
    # 95% zero
    # 95% span
    # sample count
    samples = len(t)
    ptData['samples'] = samples
    # sample period
    totalT = dt.sum()
    samplePer = totalT/samples
    ptData['samplePer'] = samplePer
    # percent good
    # minimum delta time (while good)
    ptData['minDT'] = dt.min()
    ptData['ln(minDT)'] = np.log(dt.min())
    # minimum delta value
    ptData['minDV'] = dv.min()
    ptData['normalized minDV'] = 100*(dv.min()/obsSpan)
    # maximum delta time (while good)
    ptData['maxDT'] = dt.max()
    # maximum delta value (while good)
    ptData['maxDV'] = dv.max()
    ptData['normalized maxDV'] = 100*(dv.max()/obsSpan)
    # 95% zero normalized to zero attribute
    # 95% span normalized to span attribute

    print(ptData)