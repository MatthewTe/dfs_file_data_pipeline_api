# DHI dfs Data Pipeline API
This repository contains all the methods and packages necessary to construct a data Pipeline designed to move the raw
output of a DHI hydrodynamic model (.dfs mesh files) to a web api that serves an interactive web dashboard that visualizes
the data.

## Table of Contents
* ### [Requirements/Installation Instructions](https://github.com/MatthewTe/dfs_file_data_pipeline_api#requirements)
* ### [Pipelines](https://github.com/MatthewTe/dfs_file_data_pipeline_api#pipeline-designs)
* ### Documentation
  * #### [DFS Visualization API](https://github.com/MatthewTe/dfsu_visualization_pipeline/blob/master/docs/dfs%20file%20visualization.md)
  * #### [DFS File Ingestion API](https://github.com/MatthewTe/dfsu_visualization_pipeline/blob/master/docs/dfs%20file%20ingestion.md)
  * #### [DFS File Query API](https://github.com/MatthewTe/dfsu_visualization_pipeline/blob/master/docs/dfs%20file%20query%20api.md)
  * #### [Pipeline API](https://github.com/MatthewTe/dfs_file_data_pipeline_api/blob/master/docs/dfs%20pipeline%20api.md)

## Requirements
The python package containing the pipeline apis can be installed via the pip package manager using the conventional pip install commands for installing git repositories:

```
pip install git+https://github.com/MatthewTe/dfs_file_data_pipeline_api.git
```
The python setup tools should handle the installation of all associated packages and if not, they can all be manually installed via pip.

The `dfs_ingestion_api.py` script makes heavy use of the [`mikeio` python package](https://github.com/DHI/mikeio). The `mikeio` package calls methods outside of the python application, it interacts with an application called the `MIKE SDK`, a windows based software development application by DHI. This application must be installed as the SDK allows the mikeio python package to open and interact with DHI's propriety file type `dfs`. The MIKE SDK and its installation instructions can be found [here](https://www.mikepoweredbydhi.com/download/mike-2017-sp2/mike-sdk).

## Pipeline Designs
This library was created in order to implement various data pipelines with various end goals. As the library is updated with methods and apis to facilitate more data pipelines they will be added here:

### HD Forecasting Pipeline with DFS0 files
This was the initial pipeline that the library was created for. The goal was to create a series of apis that would allow the output from a DHI Hydrodynamic model to be automatically collected and concatenated in a way that would make it easy to pipe into some visualization library- most likely Dash/Plotly.

The model outputs (accurately) a seven day future-forecast of hydro-data. It writes this data into a file directory with a pre-determined directory structure. The pipeline api object when called, should search the file structure for the appropriate files in the correct order and concatenate all dfs0 files into a single, plottable timeseries in a scheduled batch process (see pipeline_api Documentation for in-depth detail of how this process works). As more real-time dashboards that display model output data are added to the [flask webportal](https://github.com/MatthewTe/cdl_flask_main) this pipeline is repeated for every individual dashboard. 

The abstract structure of this pipeline would be as follows:

![IMAGE NOT FOUND](https://github.com/MatthewTe/dfs_file_data_pipeline_api/blob/master/resources/Individual%20DFS0%20Pipeline.png)  

**Note: These pipelines are not built in this package. This package contains the methods and apis to implement these pipelines. These pipeline descriptions are to give more context to the package as it shows the processes that these scripts were created for.*
