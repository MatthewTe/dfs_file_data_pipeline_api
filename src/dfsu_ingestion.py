# Importing mikeio package from DHI repo: https://github.com/DHI/mikeio.git
import mikeio
# Importing data management packages:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
# Misc Imports
import datetime

'''dfsu = Dfsu()
data = dfsu.read("C:\\Users\\teelu\\Downloads\\concat-10april2019.dfsu")
idx = dfsu.get_node_coords()
test = dfsu.find_closest_element_index(idx[0][0],idx[0][1], idx[0][2])'''



class dfsu_ingestion_engine(mikeio.Dfsu):
    '''
    The ingestion engine ingests a dfsu file path and provides a series of APIs
    directly based off of the mikeio DHI library to query and extract Dfsu data
    in a simplified form

    Parameters
    ----------
    filepath: str
        The filepath of the .dfsu file.
    '''

    def __init__(self, filepath):

        # Instance Variables:
        self.filepath = filepath

        # Invoking mikeio parent to initalize Dfsu():
        super().__init__()

        # Reading core data from .dfsu file:
        self.dataset = self.read(filepath)

        # Conditional to ensure that the dfsu file contains long/lat mesh:
        if self.is_geo is True:

            # Once long/lat mesh confirmed, initalizing other data:
            self.nodes = self.get_node_coords() # (long, lat, z-value) of each node

        else:
            # if there is no long/lat mesh error out w custom error msg:
            # TODO: Write custom error msg.
            pass

    # Method that extracts all data from a single category for a single point:
    def get_node_data(self, long, lat, depth, cat_name):
        '''
        Method takes locational data and a category name and produces a
        dataframe containing all data for the category at a particular node
        given the locational data.

        Parameters
        ----------
        long : float
            The longnitude value of the location point

        lat : float
            The latitude value of the location point

        depth : float : Default = None
            The depth value of the location point

        cat_name : str
            The string that is used to slice the main array to extract
            only the data pertaining to that category

        Returns
        -------
        node_df : pandas dataframe
            A dataframe that contains all the category specific data of the
            selected node, indexed by the timeseries provided by the .dfsu
            file
        '''
        # Slicing the main list data based on the input category name:
        category_data = self.dataset[cat_name]

        # Extracting the index value of the data segement that corresponds to the cords:
        element_index = self.find_closest_element_index(long, lat, depth)
        #print(element_index)

        # Further slicing the array based on the element_index value:
        dataset_slice = category_data[:, element_index]

        # Constructing a pandas dataframe of the dataset_slice indexed by datetime:
        node_df = pd.DataFrame(data=dataset_slice, index=self.dataset.time, columns=[cat_name])

        return node_df

    # Method that extracts data from a single category for an whole layer:
    def get_node_layers(self, long, lat, cat_name):
        '''
        Method extracts all the data associated with a single data category given
        a single long/lat point. Unlike .get_node_data this method extracts the
        data for said category at all elevation levels (at all z-values) associated
        with the long/lat point.

        Parameters
        ----------
        long : float
            The longnitude value for the node that is being extracted

        lat : float
            The latitude value for the node that is being extracted

        cat_name : str
            The name of the category of data that will be extracted from the dataset

        Returns
        -------
        layers_dict : dict
            A dictionary containing key-value pairs of z-value determined layers
            and pandas dataframes containing the relevant data at each layer
        '''
        # Slicing dataset based on category:
        cat_slice = self.dataset[cat_name]

        # Empty list that will by populated by all coord_lst values of the layer:
        layer_coords = []

        # Iterating through all node coords building custom list of coords:
        for coord_lst in self.nodes:

            # Once first long/lat match is found, all depth layers are extracted:
            if math.isclose(coord_lst[0], long) is True and math.isclose(coord_lst[1], lat) is True:

                    # If the z-value is close to 1, at top of layer so append and
                    # break loop for efficency:
                    if math.isclose(coord_lst[2], 1) is True:

                        layer_coords.append(coord_lst)
                        break

                    # If z-value is not close to 1, continue to itterate and append:
                    else:
                        layer_coords.append(coord_lst)
                        continue

            else:
                continue

        # Creating the main dict to store all the layers and their subsequent df:
        layers_dict = {}

        # Iterating over each point in layer_coords and creating key-value pairs:
        for node in layer_coords:

            # Getting index for node:
            node_index = self.find_closest_element_index(*node)

            # Further slicing cat_slice by the node_index:
            dataset_slice = cat_slice[:, node_index]

            # Creating a dataframe of values for the dataset_slice:
            df = pd.DataFrame(data=dataset_slice, index=self.dataset.time, columns=[cat_name])

            # Adding key-value pair to layers_dict and iterating layers int for next loop:
            layer = node[2]
            layers_dict[layer] = df

        return layers_dict

test = dfsu_ingestion_engine("C:\\Users\\teelu\\Downloads\\concat-10april2019.dfsu")
#print(test.get_node_data(-63.08325873, 11.29754091, -2.322656, 'Temperature'))
#print(test.get_node_layers(-63.08325873, 11.29754091, 'Temperature'))

'''
# TODO:
- Create a method that generates a dataframe from an extracted sub-index and
    a modify both .get_node_data and .get_node_layers methods to utilize this for increased
    performance

    - Critcal change is in .get_node_layers(). Instead of returning {z-value : dataframe for z-value}
    it returns {z-value : index corresponding to z-value}. Change should improve
    currently horrific performance issues w method.

    - Write method that then utilizes the sub-index to dataframe method  to generate
    a dataframe from each {.get_node_layers} key-value pair as needed.

- Once overall data structure is approved, write documentation for said structure and
    methods
'''
