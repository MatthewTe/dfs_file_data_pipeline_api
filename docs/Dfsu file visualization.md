# Data Visualization Tools
The data visualization package is written mainly using the plotly graphics library to create interactive plots on a web based application. Such as a Flask Dash application. The methods in the visualization script can be invoked to produce ready-made complicated plots based on the configuration of the methods.

## Table of Contents
* ### [dashboard()](placeholder)

## `dashboard(filepath)`
The object used to generate ready-made dashboards us the `dashboard()` object. This object inherits from its parent class: the `dfsu_ingestion_engine()` and uses the dfsu_ingestion_engine API to call data from unstructured dfsu files. It then uses its methods to plot various dashboards.
**Note: These dashboard plotting methods such as `plot_node_data()` are static methods.**
 For the most part they are non-configurable via input parameters as to the data that they display or how they display it. The point of these methods are to be easily callable in a web application and as such, simplicity has been HEAVILY prioritized over customization from a display perspective. If specific custom plots are to be made they should be made by changing the source code of these methods. They have been written in such a way as to make them easily editable.
