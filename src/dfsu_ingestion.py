# Importing mikeio package from DHI repo: https://github.com/DHI/mikeio.git
import mikeio as mk
from mikeio import Dfsu
# Importing data management packages:
import pandas as pd
import numpy as np
# Misc Imports
import datetime

ds = Dfsu().read("C:\\Users\\teelu\\Downloads\\concat-10april2019.dfsu")



'''print(ds)
print(ds.names)
print(ds.time)
print(test_var)'''

test_var = ds['Current speed']

current_speed = pd.DataFrame(data=test_var)

current_speed.index = pd.DatetimeIndex(ds.time, freq='infer')

print(ds.names)
print(current_speed)
