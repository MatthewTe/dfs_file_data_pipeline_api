# DHI dfsu Pipeline
This repository contains all the methods and packages necessary to construct an ETL Pipeline designed to move the raw
output of a DHI hydrodynamic model (.dfsu mesh files) to a web api that serves an interactive web dashboard that visualizes
the data.

## Table of Contents
* [Raw Data Ingestion](placeholder)

## Raw Data Ingestion
The data generated from the DHI model is represented as a 3-D mesh, meant to be plotted onto a GIS visualization tool such as
MIKE ZERO. Using the DHI python library [mikeio](placeholder) dfsu files are able to be read in as a series of nested arrays.

Data ingestion is done via the `dfsu_ingestion_engine()` object which inherits from the mikeio Dfsu() class and provides several
methods of extracting data in formats that are easily readable in a non-GIS context.

Data extracted by these methods via the input of longitude, latitude and a depth value (z-value) in some cases.  

### `extract_data(data_category, element_index)`
Most if not all data extraction methods in `dfsu_ingestion_engine()` make use of the `.extract_data()`
method. The method copies and transforms the main dfsu dataset and slices it twice:

- First according to the category of data indicated by the data_category string
- Second according to the dataset index indicated by the element_index integer.

It then converts this sliced dataset into a formatted dataframe.

This method is invoked in many of the other data extraction methods as other methods operate around
extracting index values based on various input conditions and rely on the `extract_data()` method to
convert it into a simplified format.  

### `get_node_data(long, lat, depth, cat_name)`
`.get_node_data()` is a straightforward method that invokes the mikeio method `.find_closest_element_index()` to extract the index values for single points in the dfsu file indicated by the 3-point Coordinate system (long, lat, depth).

Once it extracts the index value it calls `extract_data()` and returns the resulting dataframe.

### `get_node_layers(long, lat)`
`.get_node_layers()` is a slightly more complicated method. Instead of extracting all the data gathered at a single point, it generates a dictionary that contains a key-value pair of:
`{depth_value : index corresponding to (long,lat,depth_value)}` for the entire dataset, not
from a category slice.

It does this by iterating over the main data array and extracting only the [coord_lst] that have
long and lat data that correspond to the input long and lat values:

```python
# Iterating through all node coords building custom list of coords:
for coord_lst in self.nodes:

  # Once first long/lat match is found, all depth layers are extracted:
  if math.isclose(coord_lst[0], long) is True and math.isclose(coord_lst[1], lat) is True:

    # If the z-value is close to 1, at top of layer so append and break loop for efficiency:
    if math.isclose(coord_lst[2], 1) is True:

        layer_coords.append(coord_lst)
        break

    # If z-value is not close to 1, continue to iterate and append:
    else:
      layer_coords.append(coord_lst)
      continue

  else:
    continue
```
It then uses these values to build the main dictionary:
```python
# Iterating over each point in layer_coords and creating key-value pairs:
for node in layer_coords:
  # Getting index for node:
  node_index = self.find_closest_element_index(*node)

  # Adding key-value pair to layers_dict and iterating layers int for next loop:
  layer = node[2]
  layers_dict[layer] = node_index
```
The method returns this dictionary. If data from this dict needs to be extracted into a dataframe
then the `extract_data()` method would need to be invoked to construct a pandas dataframe from data
based on the index value specified in the dictionary and an input data category string. 
