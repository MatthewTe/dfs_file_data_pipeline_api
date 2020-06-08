# Importing mikeio package from DHI repo: https://github.com/DHI/mikeio.git
import mikeio
# Importing data management packages:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
# Misc Imports
import datetime

class dfs0_ingestion_engine(mikeio.Dfs0):
    '''
    This is the object that ingests a dfs0 file based on a file path and provides
    a series of APIs that allows data to be queried and retrieved. The base for all
    of the method APIs comes from the Dfs0 object inherited from the mikeio software
    library.

    Parameters
    ----------
    filepath : str
        A string representing the path to the dfs0 file that is going to be parsed
    '''
    def __init__(self, filepath):

        # Declaring Instance variable:
        self.filepath = filepath

        # Initalizing the mikeio.Dfs0 object with the parameter filepath:
        super().__init__()

        # Creating a dataframe from the dfs0 file and declaring it as an instace var:
        self.main_df = self.to_dataframe(self.filepath)
        print(self.main_df.columns)
        # TODO: Communicate with Ami about how data should be extracted from dataframe.

# test =  dfs0_ingestion_engine("C:\\Users\\teelu\\OneDrive\\Desktop\\test_data\\TT_HD_BPTT_Cypre_F120.dfs0")


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

        '''
        # WARNING: The data categories that have been assigned by the mikeio Dfsu()
        method are incorrect. Instead of modifying the actual data assignment method
        in the Dfsu library the data columns are re-mapped using a dict internally.

        Edit this dict based on the re-mapping that needs to take place. Current
        column re-mapping includes:

        - Temperature (Degrees Celsius) --> Salinity (PSU)
        - Density (kg/m^3) ---------------> Temperature (Degrees Celsius)
        - Current Direction (radians) ----> Density (kg/m^3)
        - Current Speed (m/s) ------------> Current Direction (radians)
        - W Velocity (m/s) ---------------> Current Speed (m/s)
        - Z coordinate -------------------> U Velocity (m/s)
        '''

        # Declaring the re-mapping dict: {'Data we want':'Data from Dfsu() Dataset'}
        self.map_dict = {'Salinity':'Temperature',
                    'Temperature':'Density',
                    'Density':'Current direction (Horizontal)',
                    'Current direction':'Current speed',
                    'Current speed':'W velocity',
                    'W velocity':'V velocity',
                    'U velocity':'Z coordinate'
                    }


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
        self.extract_data() : pandas dataframe
            The method calls and returns the method .extract_data() which slices
            the main dataset, builds a dataframe based on said sliced data and
            returns a dataframe.
        '''

        # Extracting the index value of the data segement that corresponds to the cords:
        element_index = self.find_closest_element_index(long, lat, depth)

        # extracting data based on the data category and index as a dataframe:
        return self.extract_data(cat_name, element_index)

    # Method that extracts data from a single category for an whole layer:
    def get_node_layers(self, long, lat):
        '''
        Method extracts all the index values associated with a single long/lat point.
        Unlike .get_node_data this method extracts the data for said category at
        all elevation levels (at all z-values) associated with the long/lat point.

        Parameters
        ----------
        long : float
            The longnitude value for the node that is being extracted

        lat : float
            The latitude value for the node that is being extracted

        Returns
        -------
        layers_dict : dict
            A dictionary containing key-value pairs of z-value determined layers
            and the index values indicating the location of the data containing
            the relevant data at each layer. Each element in the dict can be
            represented as a dataframe using the self.extract_data() method.
        '''
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

            # Adding key-value pair to layers_dict and iterating layers int for next loop:
            layer = node[2]
            layers_dict[layer] = node_index

        # data stored in layers_dict can be extracted from the datset via self.extract_data()
        return layers_dict

    # Method that extracts data in the appropriate format to be input into a polar plot:
    def get_node_polar_coords(self, long, lat, depth):
        '''
        Method calls existing data slicing methods to extract data pertaining to
        Speed and Horizontal Direction of currents at a single node (long,lat,depth)

        The method then transforms the radial directional data into degrees that
        can be plotted onto a polar coordinate system.

        - Assumes polar coordinate format (r, theta).
        - Collects data based on Dataset['Current speed'] &
            Dataset['Current direction']

        Parameters
        ----------
        long : float
            The longnitude value of the location point

        lat : float
            The latitude value of the location point

        depth : float
            The depth value of the location point

        Returns
        --------
        polar_df : pandas dataframe
            A two column dataframe containing all the time series data for
            Current speeds and Current direction that can be expressed by a polar
            coordinate system as (r=Currnet speeds, theta=Current direction)
        '''

        # Slicing and extracting speed and directional data from the main dataset:
        r = self.get_node_data(long, lat, depth, 'Current speed')
        theta = self.get_node_data(long, lat, depth, 'Current direction')

        # Creating a new dataframe that contains polar coordinate data columns:
        polar_df = pd.concat([r, theta], axis=1)
        polar_df.rename(columns={'Current speed': 'r', 'Current direction': 'theta'},
         inplace=True)

        return polar_df

    # Method generates a dataframe based on the sliced  dataset and the specific index:
    def extract_data(self, data_category, element_index):
        '''
        Method that extracts the data from the main .dfsu dataset by slicing said
        dataset by both category and by slice determined index.

        Parameters
        ----------
        data_category : str
            The data category (type) that will be used slice the dataframe based on
            different data types

        index : int
            An integer representing the index location of the data in the dataset.
            This will be used to perform another slice on the dataset.

        Returns
        --------
        slice_df : pandas dataframe
            A dataframe that is generated and formatted based on the dataset
            sliced via data_category and index.
        '''

        # Slicing the dataset based on the category:
        category_slice = self.dataset[self.map_dict[data_category]]
        #print(self.map_dict[data_category])

        # Slicing the dataset based on the input index:
        index_slice = category_slice[:, element_index]

        # Generating a pandas DataFrame based on the index_slice data:
        slice_df = pd.DataFrame(data=index_slice, index=self.dataset.time,
        columns=[data_category])

        return slice_df
