# Importing all dfs apis:
# API Imports for production:
from data_api.dfs_file_query_api import file_query_api
from data_api.dfs_ingestion_api import dfs0_ingestion_engine

# Importing path management packages:
import os

# Importing data management packages:
import pandas as pd
from datetime import datetime
import sqlite3

# Object that provides the methods for scheduling ETL processes for dfs0 files:
class dfs0_pipeline(object):
    """
    This is the main object that makes use of all other dfs0 apis. It contains
    all the processes that are necessary for maintaining a data stream of dfs0
    files generated for a specific client.

    This is the main object that contains all the methods that transfer dfs0 data
    between processes in the data pipeline as well as maintain a master dataframe
    of all client data in a single TimeSeries stored in a sqlite database and
    extracted as a dataframe.

    The object is initalized with all the parameters necessary to initalize/interact
    with all of the dfs api methods within the data_api package.

    Parameters
    ----------
    client_name : str
        A string that represents the client name / client project name of the pipeline
        object. This is the client name that will be used by various methods to extract
        dfs0 file paths via the file_query_api.

    root_dir : str
        A path string that represents the path to the root file directory where the
        HD Model output files are stored / written to. This is the root_dir string
        that will be used to initalize the file_query_api method.

    """
    def __init__(self, client_name, root_dir):

        # Declaring instance variables:
        self.client_name = client_name
        self.root_dir = root_dir

        # Initalizing the file query api object as an instance variable:
        self.file_query = file_query_api(self.root_dir)

# <----------------------------7-Day Forecast building methods----------------->

    # Method that builds a dataframe containing 7-Day Forcasting data:
    def build_seven_day_forecast_data(self, date=None):
        '''
        This method makes uses of the get_seven_day_forcast_files() method in the
        file query api to build a pandas dataframe containing the TimeSeries data
        for the seven day forecast.

        The method iterates through the dictionary of dfs0 paths, generates a list
        of those paths within seven days using the date string keys of the dict.
        The method then initalizes all the dfs0 paths using the dfs0 ingestion
        engine and concatinates all the dfs0 dataframes into a single dataframe.

        Parameters
        ----------
        date : tuple
            A tuple that by default is None. If the tuple is input, it must be in
            the form (year, month, day) as integers. It is used to create the
            'current_date' varable that is used as the starting point of the
            seven day file search-concatenation algo. This parameter is mainly
            used for back-testing and development.

        Returns
        -------
        forecast_df : pandas dataframe
            The dataframe containing all the forecasting data. This is generated
            as the result of dataframe list concatenation.

        Raises
        ------
        ValueError : ValueError
            The error that is raised at the end of the method when no dataframes
            are found to be concatinated.
        '''
        # Initalizing the file query api to get seven day forecasting dict:
        forecast_dict = self.file_query.get_seven_day_forcast_files(self.client_name)

        # If a date tuple is given as an input:
        if date != None:

            # Unpacking the tuple:
            (year, month, day) = date

            # Initalizing the datetime object with the tuple parameters:
            current_date = datetime(year, day, month)

        else: # If the date is none:

            # Creating a datetime object of the current date in the format of TimeSeries dates:
            current_date = datetime.today() # Current Date var for Production



        print('[CURRENT DATE USED AS START POINT FOR FILE QUERY]:', current_date)

        # Method that converts date_key string to datetime object w/ error checking:
        def convert_date_key(date_key):
            '''
            A method called by list comprehension to convert a date string to
            the necessary date time object.

            This method not only performs the basic datetime.strptime() method
            on the date but it handels exceptions and is used for error checking
            for each 'date key' as try catches are not possible in list comprehension.

            Parameters
            ----------
            date_key : str
                The string representing the date value to be converted to a datetime
                    object

            Returns
            -------
            date_val : datetime object
                The object that is created as a result of converting the date_key
                    string to a datetime object.
            '''
            # When a new mesh is stared the name of the file includes a tag '-newmesh'
            # that needs to be removed to prevent erroring when converting to datetime.
            if "-newmesh" in date_key:
                date_key = date_key.replace('-newmesh', '')

            # Performing actual string -> datetime converstion:
            date_val = datetime.strptime(date_key, "%Y%m%d%H")

            return date_val

        # Creating a list of datetime object from the forecast_dict keys:
        date_lst = [
            convert_date_key(date_key) for date_key in forecast_dict]
        # Slicing date_lst for date values only seven days ahead of current_date
        # and re-converting them to strings:
        forecast_date_lst = [

            # > 0 to filter out negative values:
            date for date in date_lst if (date - current_date).days <= 10 and
            (date - current_date).days >= 0

            ]

        # Sorting forecast_date_lst to enusre data integrety, not strictly necessary:
        forecast_date_lst.sort()

        # Converting dates in forecast_date_lst to strings to be used as keys:
        forecast_date_lst = [date.strftime("%Y%m%d%H") for date in forecast_date_lst]

        print('[LIST OF TIMESERIES TO BE CONCATINATED FOR FORECAST]:', forecast_date_lst)

        # Creating a list of dfs0 dataframes from paths in forecast_dict:
        forecast_df_lst = [

            # forecaast[date_key] == path to dfs0 file (see file_query_api)
            dfs0_ingestion_engine(forecast_dict[date_key]).main_df for date_key in
            forecast_date_lst
            ]

        # Error handeling:
        try:
            # Concatinating list of dataframes into main df:
            forecast_df = pd.concat(forecast_df_lst)

            return forecast_df

        except ValueError: # If the forecast_df_lst is empty:

            print('\n![NO FILES FOUND CONFORMING TO CONCATINATION SPECIFICATIONS]!')

# <----------------------------File Format Converstion/Export Methods---------->

    # Method that exports a formatted pandas dataframe as a .csv file:
    def write_csv(self, df, file_name):
        '''
        Method that converts a formatted pandas dataframe to a .csv file at a
        specified file path in the root directory based on input file name.

        Parameters
        ----------
        df : pandas dataframe
            The (most likely) concatinated pandas dataframe that the method will
            convert to a .csv file.

        pathname : str
            A string representing the name of the .csv file to be written to the
            file directory. The file_name string is used to build the path string
            that dictates where the file is written.
        '''
        # Building path string to write location:
        csv_path = os.path.join(self.root_dir, f'{file_name}.csv')

        # Try-Catch to deal with df being None type:
        try:
            # Writing the pandas dataframe to csv file:
            df.to_csv(csv_path)

            print(f'\n\n[CSV WRITTEN]: {self.client_name} data written to {csv_path} as csv')

        except:
            print(f'\n![ERROR]: Cannot Write to csv file. Input Parameter is {type(df)}!')
