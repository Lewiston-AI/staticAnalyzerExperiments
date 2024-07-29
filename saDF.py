import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def sa_histogram(df: pd.DataFrame, attr: str):
    l = np.array(df[attr])
    max = np.percentile(l, 95.0)
    vals = list()
    for n in l:
        if n <= max:
            vals.append(int(n))
    min = np.min(vals)
    max = np.max(vals)
    vals = np.array(vals)
    plt.hist(vals, bins=10, color='orange', alpha=0.7, edgecolor='black', range=(min, max), cumulative=False,
             density=True)
    plt.title('Histogram of Snapshot DT')
    plt.xlabel('Snapshot DT')
    plt.ylabel('Frequency')
    plt.show()
