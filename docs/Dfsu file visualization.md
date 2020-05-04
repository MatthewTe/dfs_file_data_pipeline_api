# Data Visualization Tools
The data visualization package is written mainly using the plotly graphics library to create interactive plots on a web based application. Such as a Flask Dash application. The methods in the visualization script can be invoked to produce ready-made complicated plots based on the configuration of the methods.

## Table of Contents
* ### [dashboard()](https://github.com/MatthewTe/dfsu_visualization_pipeline/blob/master/docs/Dfsu%20file%20visualization.md#dashboardfilepath)
* #### [plot_node_data()](https://github.com/MatthewTe/dfsu_visualization_pipeline/blob/master/docs/Dfsu%20file%20visualization.md#plot_node_dataself-long-lat-depth)
* #### [create_timeseries()](https://github.com/MatthewTe/dfsu_visualization_pipeline/blob/master/docs/Dfsu%20file%20visualization.md#create_timeseriesself-long-lat-depth-plot_name)
* #### [create_polar_plot()](https://github.com/MatthewTe/dfsu_visualization_pipeline/blob/master/docs/Dfsu%20file%20visualization.md#create_polar_plotselflonglatdepthr_columntheta_column)

## `dashboard(filepath)`
The object used to generate ready-made dashboards us the `dashboard()` object. This object inherits from its parent class: the `dfsu_ingestion_engine()` and uses the dfsu_ingestion_engine API to call data from unstructured dfsu files. It then uses its methods to plot various dashboards.

**Note: These dashboard plotting methods such as `plot_node_data()` are static methods. For the most part they are non-configurable via input parameters as to the data that they display or how they display it. The point of these methods are to be easily callable in a web application and as such, simplicity has been HEAVILY prioritized over customization from a display perspective. If specific custom plots are to be made they should be made by changing the source code of these methods. They have been written in such a way as to make them easily editable.**

Once the file path to the .dfsu file has been input and the ingestion engine has been initialized there are several methods that can be called to visualize data from the dfsu files.

## `plot_node_data(self, long, lat, depth)`
This is the main method that is used to generate a dashboard for a single point (long, lat, depth). It is generated as a plotly subplot with the figures inserted into each subplot coming from various other plot methods such as `create_timeseries()`

The dashboard contains the following data on a single node:
- Current Speed (m/s)
- Water Density (kg/m^3)
- Water Temperature (Degrees Celsius)
- Water Salinity (PSU)
- Current Direction (radians)

The Water Salinity, Density, Temperature and Current Speed are plotted as a time series using the `create_timeseries()` method.
```python
# Example of how a timeseries is added to the dashboard subplots:
fig.add_trace(self.create_timeseries(long,lat,depth,'Temperature'),row=2,col=1)
```
The dashboard method also plots a polar bar graph meant to highlight the current direction of each data point. The current speed was plotted as the r value and the current direction was naturally the theta. It was added to the subplot via the `create_polar_plot()` method.
```python
# How the polar bar plot was added to the main dashboard subplot:
fig.add_trace(self.create_polar_plot(long,lat,depth,'Current speed','Current direction',row=1, col=2))
```
Naturally this method only invokes various plotly figure creating methods such as `create_timeseries()` and `create_polar_plot()` and inserting them into pre-formatted subplots.

## `create_timeseries(self, long, lat, depth, plot_name)`
This method generates and returns a plotly.graph_object of a timeseries. The data that is used to plot the graph as well as the formatting for the said graph is determined by a dictionary containing key-value pairs that contained all the necessary formatting strings and strings to call the data API.

For Example:
```python
# Creating the timeseries plot and formatting it based on timeseries_format:
timeseries_plot = go.Scatter(x=timeseries_data.index,
    y=timeseries_data[self.timeseries_format[plot_name]['df_column']],
    name= self.timeseries_format[plot_name]['title'])
```
The parameters passed into the `go.Scatter()` are determined by the following dictionary:
```python
# Key-Value store of config information for each time series plot:
    self.timeseries_format = {
        'Salinity': {'df_column': 'Salinity', 'title':'Water Salinity','units':'PSU'},
        'Temperature' : {'df_column':'Temperature', 'title':'Water Temperature', 'units':'Degrees Celsius'},
        'Density' : {'df_column':'Density', 'title':'Water Density', 'units':'kg/m^3'},
        'Current direction' : {'df_column':'Current direction', 'title':'Current Direction', 'units':'Radians'},
        'Current speed' : {'df_column':'Current speed', 'title':'Current Speed', 'units': 'm/s'},
                            }
```
This allows Scatter plot's titles, formatting and data requests to be modified easily by editing the formatting dict associated with each plot_name string.

## `create_polar_plot(self,long,lat,depth,r_column,theta_column)`
Like the `create_timeseries()` method, `create_polar_plot()` produces a polar plot based on input r and theta values. Again with this method, everything from the data called from the API to the formatting and labeling of the polar plot is done based on the corresponding key-value pair of `"r_column"`/`'theta_column'` to the formatting dictionary in `self.timeseries_format`
```python
barpolar_plot = go.Barpolar(
        r=r[self.timeseries_format[r_column]['df_column']],
        theta=theta[self.timeseries_format[theta_column]['df_column']],
        width=7.0,
        opacity=0.8,
        marker=dict(
            color=r[self.timeseries_format[r_column]['df_column']],
            colorscale="Viridis",
            colorbar=dict(
                title=self.timeseries_format[r_column]['units']
                )
            )
        )
```
