# Importing the file directory navigation libraries:
import os
import sys
import warnings


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

    # Method that queries the directory and returns dfs filepaths based on kwargs:
    def get_client_data(self, client_name, date=None):
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

                # If the client_name is found in the directory path:
                if (client_name in tuple[0]):

                    # Iterating through list of file names building list of dfsu paths:
                    for file_name in tuple[2]:

                        # Adding dfsu file path to main list:
                        if '.dfsu' in file_name:

                            dfs_filepaths.append(os.path.join(tuple[0], file_name))

        # If there is a date value:
        else:

             # Walking through Results dir and extracting data based on date parm:
             for tuple in os.walk(start_path):

                 # If a dir can be found that contains the date format given:
                 if date in tuple[0]:

                     # Now if file contains client name:
                     if client_name in tuple[0]:

                         for file_name in tuple[2]:

                             # Now if file is a dfsu file:
                             if '.dfsu' in file_name:

                                 # Adding filepaths to main list:
                                 dfs_filepaths.append(os.path.join(tuple[0], file_name))

        return dfs_filepaths

    # Method that extracts all the dates in which the client folder is present:
    def get_client_dates(self, client_name):
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

        Returns
        -------
        date_lst : list
            A list containing datetime strings of each date folder that contains
            client specific dfsu files.
        '''
        # Main empty list that will be built:
        date_lst = []

        # Modifying root directory by adding \Results to main path:
        results_dir = self.root_dir + "\\TT_HD\\Results"

        # Iterating through the results_dir and building lists based on dfsu presence:
        for pathname, dir_name_lst, file_name_lst  in os.walk(results_dir):

            # Iterating through each filename searching for dfsu files:
            for file in file_name_lst:

                # Extracting the datetime folder string by brute-force string strip:
                if ".dfsu" in file and client_name in pathname:

                    # Brute force string stripping to modify pathname:
                    timeseries = pathname.replace(f'\\{client_name}', '').replace(f'{results_dir}\\', '')

                    # Conditional tha raises exception if string stripping fails:
                    if len(timeseries) > 10:

                        # Raising Exection and break loop:
                        warnings.warn("String slicing failed to extract exclusive datetime string.\
 Possible Issue with input client_name.")

                        break

                    # Appending timeseries string to the main_list:
                    date_lst.append(timeseries)

        return date_lst



# Scripts for testing:
test = file_query_api("C:\\Users\\teelu\\OneDrive\\Desktop\\test_data\\WaterForecastTT")
#test.get_client_data('BBTT_Cipre', '202004')
print(test.get_client_dates('ALNG_North'))
