# Importing all dfs apis:
from dfs_file_query_api import file_query_api
from dfs_ingestion_api import dfs0_ingestion_engine

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

    database_path : str
        This path string represents the path to a sqlite database file on the system.
        It will either be used to create a sqilte database if none exists and once the
        database doese exist ot establishes a connection object with that database.
        Allowing data to be read and written to the database.
    """
    def __init__(self, client_name, root_dir, database_path):

        # Declaring instance variables:
        self.client_name = client_name
        self.root_dir = root_dir

        # Creating an instance of a sqlite connection and cursor object:
        self.con = sqlite3.connect(database_path)
        self.c = self.con.cursor()

        # Creating the sql table to store meta-data about each dfs0 total concatination:
        self.c.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.client_name}_Dfs0_Dates (
                TimeSeries TEXT Primary Key)""")

        self.con.commit()

        # Initalizing an instance file query api object:
        self.dfs0_directory = file_query_api(self.root_dir)

# <---------------------------Writing Methods---------------------------------->

    # Method that contains the logic that concats all client dfs0's into single TimeSeries:
    def update_client_timeseries(self):
        '''
        This method contains all the logic necessary to maintain the database
        table containing the continuous client timeseries.

        It extracts a list of date strings from the summary database table `Dfs0_Dates`
        that represent the Dfs0 files that have already been concatinated and written
        to the database. The file query api is then called and extracts a list of
        all date strings avalible in the file directory.

        These two lists are compared and every date that has not been previously
        written to the db is then used to extract the corresponding dfs0 file.
        These files are then concatinated into a larger timeseries and written
        to the database, appended to the existing data.
        '''
        # Extracting a list of datetime objects from the sqlite database:
        written_dates = [
            datetime.strptime(date_str[0], "%Y%m%d%H") for date_str in
            self.c.execute(f"SELECT TimeSeries from {self.client_name}_Dfs0_Dates")]

        print(f'[DATES ALREADY WRITTEN]: {written_dates}')

        # Extracting a list of datetime objects from the file query api:
        directory_dates = self.dfs0_directory.get_client_dates(self.client_name, '.dfs0')

        # Creating a list of unique date strings from directory_dates not in written_dates:
        new_dates = [
            date.strftime("%Y%m%d%H") for date in directory_dates
                if date not in written_dates]

        print(f'[NEW DATES]: {new_dates}')

        # Creating an empty dict to be populated with {date_str : dfs0_df}:
        current_dfs0_dict = {}

        # If no new dates are found, output as such and pass concatination:
        if len(new_dates) > 0:

            # Calling file_query_api to extract client dfs0 path strings for new_dates:
            for date in new_dates:

                # Calling file query api:
                dfs0_path  = self.dfs0_directory.get_client_data_paths(self.client_name,
                 date, '.dfs0')

                 # Try catch to initalize each path w/ dfs0_ingestion_engine and build dict:
                try:
                    dfs0_df = dfs0_ingestion_engine(dfs0_path[0]).main_df

                    # Adding key-value pair to dict:
                    current_dfs0_dict[date] = dfs0_df

                except:
                    # TODO: Add Warning
                    pass

            # Building a list of all dataframes from the current_dfs0_dict:
            df_list = [current_dfs0_dict[date] for date in current_dfs0_dict]

            # Concatinating the df_list into a single dataframe:
            concat_df = pd.concat(df_list)

            # Creating a sqlite3 database table

            # Writing the pandas dataframe to the sqlite database:
            concat_df.to_sql(f'{self.client_name}_dfs0', self.con, if_exists='append',
                index=True, index_label='Date')

            print(f'[CLIENT DATA WRITTEN TO DATABASE]: {self.client_name}')

            # Iterating through the lists of dates, writing values to the database:
            for date in new_dates:

                self.c.execute(
                f"""INSERT INTO {self.client_name}_Dfs0_Dates(TimeSeries)
                    VALUES(:date)""", {'date':date})

                print(f'[DATE WRITTEN TO DATABASE]: {date}')

            self.con.commit()


        else:

            print('[NO NEW DATES FOUND]: Concatination Not Avalible')

            return

# <--------------------------Query Methods------------------------------------->

    # Method that returns the whole dataframe of the client data TimeSeries:
    def get_client_data(self):
        '''
        Method that makes use of the pandas sql query api to read the client database
        table to a fully formatted dataframe. This method would primarily be used
        as an api for a visualization method.

        Returns
        -------
        client_df : pandas dataframe
            The dataframe containing data extracted from the client data table via
            the pandas sql api. This dataframe is formatted under the assumption
            of a date index.
        '''
        # Extracting the dataframe from the sqlite table:
        client_df = pd.read_sql(f"SELECT * FROM {self.client_name}_dfs0", self.con)

        # Converting index to datetime index:
        client_df.set_index('Date', inplace=True)

        # Converting index to a datetime index:
        client_df.index = pd.to_datetime(client_df.index)

        return client_df


# Test:
root_dir = "C:\\Users\\teelu\\OneDrive\\Desktop\\test_data\\WaterForecastTT"
database_path = "C:\\Users\\teelu\\OneDrive\\Desktop\\test_data\\WaterForecastTT\\test_db"
test = dfs0_pipeline('BGTT_ALNG_F036', root_dir, database_path)
test.update_client_timeseries()
print(test.get_client_data())
