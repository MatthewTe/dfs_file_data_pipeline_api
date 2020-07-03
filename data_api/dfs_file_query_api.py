# Importing the file directory navigation libraries:
import os
import sys
import warnings

# Importing the dfs ingestion api: # NOTE: For Production
from * import dfs_ingestion_api.dfs0_ingestion_engine as dfs0_ingestion_engine
#from dfs_ingestion_api import dfs0_ingestion_engine # NOTE: For development

# Importing data management packages:
from datetime import datetime

# An object that is means to represent the file diectory containing dfs files:
class file_query_api(object):
    """
    This object is used to contain all the variables and methods necessary to
    explore the CDL file structure of the DHI HD Model's output. It serves as an
    api to access and explore said directory and, more importantly, to extract
    file paths of dfs files given input parameters.

    The object is designed mainly to be called in order to provide fil path data
    for the data ingestion engine to access stored DFS files.

    This API assumes a very strict directory structure outlined in the documentation
    and will not function otherwise.

    Parameters
    ----------
    root_dir : str
        A filepath string representing the root or highest level DHI directory.
        This is root dir is outlined in the API's documentation.
    """

    def __init__(self, root_dir):

        # Path of the root diretory:
        self.root_dir = root_dir

        # Path of the results sub-directory:
        self.results_dir = self.root_dir + "\\TT_HD\\Results"

# <-------------------------------General File Query Methods------------------->

    # Method that queries the directory and returns dfs filepaths based on kwargs:
    def get_client_data_paths(self, client_name, date=None, file_type='.dfsu'):
        '''
        Method that searches the CDL directory structure for dfs files based on the
        client name parameter. The search can be further specified by the optional
        parameters.

        Parameters
        ----------
        client_name : str
            The name of the client for which the dfs filepaths will be returned.
            This string will dictate the search that is performed and as such it
            is important that this string is equal to the folder name given to
            the client in the CDL file directory. See Docs

        date : str
            A string used to specify the date from which the dfsu file paths
            will be queried. The date given must correspond to the date format
            of the file structure: yyyymmddhh. The level of specificity of the
            date will determine the breath of the file path search. See Docs

        file_type : str : default = '.dfsu'
            A string that provides the method with the type of file extension
            that will be retrieved. This is by default a dfsu file with the extension
            '.dfsu' and theoretically could be any file extension but is primarily
            designed to be used to extract DFS file paths such as '.dfsu' and '.dfs0'

        Return
        ------
        dfs_filepaths : list
            A list of filepath strings that were extracted based on the search
            parameters specified by the method.
        '''
        # Empty list of filepaths to be built:
        dfs_filepaths = []

        # Building start path for os.walk:
        start_path = os.path.join(self.root_dir, "TT_HD\\Results")

        # Conditional that seperates query based on if a date was input:
        if date == None:

            # Walking through Results dir and extracting all relevant data:
            for tuple in os.walk(start_path):

                # If a "Timeseries" sub-directory is found in the directory path:
                if ('TimeSeries' in tuple[0]):

                    # Iterating through list of file names building list of dfsu paths:
                    for file_name in tuple[2]:

                        # Adding file path to main list:
                        if file_type in file_name and client_name in file_name:

                            dfs_filepaths.append(os.path.join(tuple[0], file_name))

        # If there is a date value:
        else:

             # Walking through Results dir and extracting data based on date parm:
             for tuple in os.walk(start_path):

                 # If a dir can be found that contains the date format given
                 # and contains a "TimeSeries" sub folder:
                 if date in tuple[0] and 'TimeSeries' in tuple[0]:

                     # Iterating through list of file paths:
                     for file_name in tuple[2]:

                         # Now if file is the correct file type and contains client_name:
                         if file_type in file_name and client_name in file_name:

                             # Adding filepaths to main list:
                             dfs_filepaths.append(os.path.join(tuple[0], file_name))

        return dfs_filepaths

    # Method that extracts all the dates in which the client folder is present:
    def get_client_dates(self, client_name, file_type='.dfsu'):
        '''
        This method uses the os.walk method to iterate through the list of all
        yyyymmddhh file directories and builds a list of datetimes in which the
        client_name sub-folder contains dfsu files. The end goal of this method
        is to provide a means of creating an ordered timeseries of dfsu files.

        Parameters
        ----------
        client_name : str
            A string representing the name of the client of which the files are
            being searched. It is critical that the client_name string be equal to
            the flie name for the client sub-folder. See Docs for more info.

        file_type : str : default = '.dfsu'
            A string that provides the method with the type of file extension
            that the algorithm will use to search for date values. This is by
            default a dfsu file with the extension '.dfsu' and theoretically could
            be any file extension but is primarily designed to be used to extract
            DFS file paths such as '.dfsu' and '.dfs0'

        Returns
        -------
        date_lst : list
            A list containing datetime strings of each date folder that contains
            client specific files.

        Raises
        ------
        Exception : Exception
            An error that occurs if a client name string is not correctly defined.
            Halts the building of the date_lst as brute-force string slicing is no
            longer possible.
        '''
        # Main empty list that will be built:
        date_lst = []

        # Modifying root directory by adding \Results to main path:
        results_dir = self.root_dir + "\\TT_HD\\Results"

        # Iterating through the results_dir and building lists based on dfs presence:
        for pathname, dir_name_lst, file_name_lst  in os.walk(results_dir):

            # If the date folder contains a "TimeSeries" sub-folder:
            if "TimeSeries" in pathname:

                # Iterating through list of files searching for filenames:
                for file_name in file_name_lst:

                    # If the client file is found with correct file type:
                    if client_name in file_name and file_type in file_name:

                        # Stripping pathname of all other elements via brute-force:
                        date_str = pathname.replace(f"{results_dir}\\", '').replace(f"\\TimeSeries", "")

                        # Appending all dates to the date_list lst:
                        date_lst.append(date_str)

        # Converting date_lst to a set to extract unique values. Re-converting set
        # to list gives only unique strings:
        dates_unique = list(set(date_lst))

        # Converting list of unique date strings to datetime objects using list comprehension:
        dates_unique = [
            datetime.strptime(date_str, "%Y%m%d%H") for date_str in dates_unique
            ]

        # Sorting the list of datetime objects by recency:
        dates_unique.sort()

        return dates_unique

    # Method that iterates through the list generated by get_client_data_paths and
    # initalizes each list element as a dfs0 file object from the ingestion_api:
    def get_dfs0_list(self, client_name):
        '''
        This method iterates through the list of dfs0 file paths generated from the
        self.get_client_data_paths(), initalizes these paths as dfs0_ingestion objects
        and builds and returns a key-value dict of {'timeseries': dfs0 dataframe}.
        The dfs0 dataframe is the self.main_df dataframe extracted from the ingestion
        object.

        Parameters
        ----------
        client_name : str
            The name of the client for which the dfs filepaths will be generated.
            Via the self.get_client_data_paths(client_name).

        Returns
        -------
        path_dict : dict
            A key value dictionary that contains all the key-value pairs of format
            {datetime : dataframe} from the client data path list.
        '''
        # Initalizing the list of dfs0 paths:
        file_type = '.dfs0'
        dfs_list = self.get_client_data_paths(client_name, file_type=file_type)

        # Creating empty dictionary to be populated:
        path_dict = {}

        # Building the start path to be stripped from path value:
        start_path = os.path.join(self.root_dir, "TT_HD\\Results\\")

        # Iterating through the list of dfs0 paths and building the dictionary:
        for path in dfs_list:

            # Initalizing dfs0 file via the dfs0 ingestion engine:
            dfs0 = dfs0_ingestion_engine(path)

            # Brute force slicing the path string for date value:
            df_date = path.replace(start_path, '').replace('\\TimeSeries', '')
            df_date = df_date.replace(f"\\TT_HD_{client_name}{file_type}", '')

            # Attempting to convert the df_date string to a datetime object:
            df_date = datetime.strptime(df_date, "%Y%m%d%H")

            # Extracting dataframe from the dfs0 file:
            dfs0_df = dfs0.main_df

            # Adding datetime object-dataframe, key-value pair to the path_dict:
            path_dict[df_date] = dfs0_df

        return path_dict

# <-----------------------------Specific File Search Algorithms---------------->

    # Method that performs the file search for 7-day forcecasting data:
    def get_seven_day_forcast_files(self, client_name):
        '''
        This method implements the Seven Day Forecasting File search algorithm to
        buid a dictionary of the most recent 7-day forcasting dfs0 data for a
        client in the CDL file directory. See Documentation for full description.

        Parameters
        ----------
        client_name : str
            This is the client name string that will be used to search the file
            directory for client_specific dfs0 files.

        Returns
        -------
        forecast_dict : dict
            A dictionary containing all the forecasting data for the client within the
            7-day period. It is stored as key-value pairs of
            {'TimeSeries value': 'dfs0 File Path'}.
        '''
        # Creating the empty forecast_dict to be built {TimeSeries: dfs0 path}:
        forecast_dict = {}

        # Iterating through the results directory using os.walk:
        for pathname, dir_name_lst, file_name_lst in os.walk(self.results_dir):

            # Building a list of dfs0 file names for a specific client:
            client_name_lst = [
                path_name for path_name in file_name_lst if client_name in path_name]

            # If the client_name_lst > 0 then continue logic:
            if len(client_name_lst) > 0:

                f_values = [
                    # Stripping the file name string and extracting f-value as int:
                    int(file_name.replace('.dfs0','')[-3:]) for file_name in
                        client_name_lst
                        ]

                # Creating an indicator dict to create searchable key-value pairs
                # of {F-Value int: path string}:
                f_val_dict = dict(zip(f_values, client_name_lst))
                lowest_f_val = min(f_values)

                # Using the f_val_dict to extract the path of the smallest F-Value:
                f_val_name = f_val_dict[lowest_f_val]

                # Debug print:
                print(f'[MOST RECENT F-VALUE]: {lowest_f_val}')
                print(f'[MOST RECENT FILE]: {f_val_name}\n')

                if "TimeSeries" in pathname:
                    # Extracting TimeSeries string value from pathname:
                    date_val = pathname.replace(f"{self.results_dir}\\", '').replace(f"\\TimeSeries", "")

                    # Building the path to the dfs0 file:
                    f_val_path = os.path.join(pathname, f_val_name)

                    # Building key-values in the Forecast Dictionary:
                    forecast_dict[date_val] = f_val_path

            else: pass

        return forecast_dict
