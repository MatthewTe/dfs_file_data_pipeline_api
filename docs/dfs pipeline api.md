# DFS Pipeline API
The script `pipeline_api.py` contains the methods that make use of all other apis and scripts in the package. Its methods are the central methods that are intended to be called by other, external applications to extract structured data in the necessary formats.

## Table of Contents
* ### [`dfs0_pipeline`](placeholder)


## `dfs0_pipeline(client_name, root_dir)`
This is the pipeline object that contains all the methods necessary to maintain a data pipeline of easily plotable Time-Series data from the seven day forecasting HD model outputs. It requires both `client_name` and `root_dir` strings as inputs to be initialized as it mainly makes use of the `file query api`: `get_seven_day_forcast_files()`.

When initialized the pipeline object initializes a `file_query_api object` via the root directory parameter.

### `build_seven_day_forecast_data(self)`
This method when called, returns a pandas dataframe of all available data generated for the seven-day-forecast model by the DHI HD model.

The method does this by using the `file_query_api's get_seven_day_forcast_files()` with the client name used to initalize the pipeline method. This method (see file query documentation) generates a dictionary of TimeSeries strings and associated dfs0 paths. The method then parses this dictionary; extracting the dfs0 path strings that have an associated TimeSeries date string that is greater than the current date the method is run but less than or equal to the date +7 days.

In other words the method builds a list of forecast dfs0 paths ordered by date from 1-day forecast to 7-day forecast using the dfs0 with the date closest to the current date as a starting point. Once this list has been built the method then initializes all these dfs0 paths as pandas dataframes via the `dfs0_ingestion_engine` and concatenates these dataframes into a single dataframe.  

Example:
```python
test = dfs0_pipeline('TT_HD_BPTT_Cypre', "Path to root directory")
test.get_seven_day_forcast_files()

# <-----------------------------------Output----------------------------------->

```
