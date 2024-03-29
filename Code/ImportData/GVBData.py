#Imports
import json
import pandas as pd
import re


def stationData(arr_df, dep_df, stations):
    """
    This function construct the passenger GVB DF, by summing the arrivals and departures per stattion, per hour, per date. 

    Parameters: 
    - arr_df(csv): Arrival Df (reisdata GVB).
    - dep_df(csv): Departure DF (reisdata GVB).
    - stations(list): Which stations to include in the df.

    Returns: DF with all passenger data
    """
    #Variables 

    #Dict to save arrival data in
    arr_dict = {}

    #Dict to save departure data in
    dep_dict = {}

    #Dict to save the coordinates of each station
    coordinate_dict = {}

    #################################################################################

    #for each of the given stations, construct a custom temp df
    for station in stations:

        #Arrivals

        #From the arrival df, select all rows that contain the given station as arrival
        temp_arr_df = arr_df[arr_df["AankomstHalteNaam"] == station]

        #Select the usable columns and rename them
        temp_arr_df = temp_arr_df.rename(index=str, columns={"AantalReizen": station + " Arrivals",
                                                             "UurgroepOmschrijving (van aankomst)": "Hour", "Datum": "Date"})

        #Sum the arrivals to the total number of arrivas on an hourly basis
        temp_arr_df = temp_arr_df.groupby(["Date", "Hour"]).agg(
            {station + " Arrivals": 'sum'}).reset_index()

        #Save the Longitude and Latitude of the given station in dict (consistency)
        coordinate_dict[station + " Lat"] = arr_df[arr_df["AankomstHalteNaam"]
                                               == station].reset_index()["AankomstLon"][0]
        coordinate_dict[station + " Lon"] = arr_df[arr_df["AankomstHalteNaam"]
                                               == station].reset_index()["AankomstLat"][0]

        #################################################################################

        #Departures

        #From the departures df, select all rows that contain the given station as departure
        temp_dep_df = dep_df[dep_df["VertrekHalteNaam"] == station]

        #Select usable columns and rename them
        temp_dep_df = temp_dep_df.rename(
            index=str, columns={"AantalReizen": station + " Departures", "UurgroepOmschrijving (van vertrek)": "Hour",
                                "Datum": "Date"})

        #Aggregate the number of departures on an hourly basis
        temp_dep_df = temp_dep_df.groupby(["Date", "Hour"]).agg(
            {station + " Departures": 'sum'}).reset_index()

        #################################################################################

        #Save the temp df's in arrival and departure dict respectively
        arr_dict["{0}".format(station)] = temp_arr_df
        dep_dict["{0}".format(station)] = temp_dep_df

        #################################################################################

    #Merge all the arrivals in one DF and all the departures in on DF
    for i in range(len(stations)-1):

        #Merge the current df with the next df on date and hour. Each each row contains data of all stations
        arr_dict[stations[i+1]] = pd.merge(arr_dict[stations[i]],
                                           arr_dict[stations[i+1]], on=["Date", "Hour"], how="outer")

        dep_dict[stations[i+1]] = pd.merge(dep_dict[stations[i]],
                                           dep_dict[stations[i+1]], on=["Date", "Hour"], how="outer")

    #Merge the arrivals and departures in one df
    df = pd.merge(arr_dict[stations[-1]], dep_dict[stations[-1]],
                       on=["Date", "Hour"], how="outer")

    #################################################################################

    #Make all coordinates of each station the same value (consistency)
    for k, v in coordinate_dict.items():
        df[k] = v
        
    return df


def transformDate(df, stations):
    """
    This function transforms the date related objects in the given DF in the following ways:
    - The date is saved in a consistent format.
    - The hour is transformed to a multiple of 100 (so 01:00 becomes 100).
    - The weekday number of the date is saved.
    - Whether it's weekend is saved (no normal situation).
    
    Parameters:
    - df(pandas df): The passenger DF
    - stations(list): What stations were included
    
    Returns: Fully constructed GVB DF
    """

    #Variables
    
    #Possible data formats that the given df contains
    date_format_1 = '%m/%d/%Y %H:%M:%S'
    date_format_2 = '%m/%d/%Y %H:%M:%S'

    #################################################################################

    #Fill NaN values with 0
    df = df.fillna(0.0)

    #Add column day numbers
    df["weekday"] = 99

    #Add whether column to indicate whether it is weekend
    df["is_weekend"] = 0

    #################################################################################

    #Dataframe to Dict
    df_dict = df.to_dict("index")

    #Loop over dict
    for k, v in df_dict.items():

        #Replace time string with time blok
        time_blok = v["Hour"][:5]
        time_blok = re.sub('[:]', '', time_blok)
        v["Hour"] = int(time_blok)

        #Replace 00:00 with 24:00 
        if v["Hour"] == 0:
            v["Hour"] = 2400

        #Remove AM/PM from string
        v["Date"] = v["Date"][:-3]

        try:
            #Transform the date string to datatime.date object
            date = pd.Timestamp.strptime(v["Date"], date_format_1)

            #Transfrom date to weekday number
            v["weekday"] = date.weekday()
        except:
            #Transform the date string to datatime.date object
            date = pd.Timestamp.strptime(v["Date"], date_format_2)

            #Transfrom date to weekday number
            v["weekday"] = date.weekday()

        #Transform Date string to datetime object
        v["Date"] = date.date()

        #Check if weekday is in the weekend
        if date.weekday() == 5 or date.weekday() == 6:
            v["is_weekend"] = 1

        #Save the date object in the data column
        v["Date"] = date.date()

    return pd.DataFrame.from_dict(df_dict, orient="index")


def gvbDF(path_to_arr_data, path_to_dep_data, stations):
    """
    This function constructs the full GVB dataset, by calling on all needed functions

    Parameters:
    - path_to_arr_data(str): Path the arrival DF
    - path_to_dep_data(str): Path to dep df
    - stations(list): which stations to included in the DF

    Returns: Full GVB DF
    """

    #Import needed data
    arr_df = pd.read_csv(path_to_arr_data, sep=";")
    dep_df = pd.read_csv(path_to_dep_data, sep=";")

    #Construct DF with passenger data per date on an hourly basis
    df = stationData(arr_df, dep_df, stations)

    #Transform the date objects of the DF to a consistent format
    df = transformDate(df, stations)

    return df