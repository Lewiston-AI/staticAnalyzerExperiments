import pandas as pd
import numpy as np
import plotly.express as px


def sa_histogram(df: pd.DataFrame, attr: str, bins):
    #l = np.array(df[attr])
    #max = np.percentile(l, 95.0)
    #vals = list()
    #for n in l:
    #    if n <= max:
    #        vals.append(int(n))
    #min = np.min(vals)
    #max = np.max(vals)
    #vals = np.array(vals)
    fig = px.histogram(df, x=attr, nbins=bins)#, range_x=[min, max])
    fig.show()

def sa_save_csv(df: pd.DataFrame, path: str):
    df.to_csv(path_or_buf=path)
