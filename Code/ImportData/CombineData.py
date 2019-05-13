#Imports
import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.preprocessing import StandardScaler

def strToTimestamp(df, format):
    """
    This function converts a pandas.df column to Timestamp object

    Parameters:
    - df (df[col]): Needs to be converted to pd.Timestamp
    - format (str): format of the date as it's given

    Returns: DF[col] with al dates as pd.Timestamps
    """

    return pd.to_datetime(df, format=format)

def startEndDate(df1, df2=df1):
    """
    This function returns the min date of a given df column and the max date of a given df column

    Parameters:
    - df1 (df[col]): From which the min date has to be returned
    - df2 (df[col]) (optional): From which the max date has to be returned
        - Optional: If this parameter is not given, the value of df1 will be used
        - Useful if max and min date are not in the same df[col]
    
    Returns: Min and Max date if given column(s)
    """

    return df1.min(), df2.max()

def importData(sensor_df, gvb_df, event_df):
    """
    This function converts the date from str to pd.Timestamp object 
    
    Parameters:
    - sensor_df (df): sensor data
    - gvb_df (df): gvb data
    - event_df (df): event data

    Returns: Returns all Df's with pd.Timestamp objects
    """

    #Variables
    
    #Format Datetime
    date_format = "%Y-%m-%d"

    #List all df's
    df_list = [sensor_df, gvb_df, event_df]

    #################################################################################

    #Loop over all given DF's and transform str to timestamp
    for df in df_list:
        df["Date"] = strToTimestamp(df["Date"], date_format)

    return sensor_df, gvb_df, event_df

def changeStartEndDate(sensor_df, gvb_df, event_df):
    """
    This function selects rows of df's based on generated start and end dates
    
    Parameters:
    - sensor_df (df): sensor data
    - gvb_df (df): gvb data
    - event_df (df): event data

    Returns: Returns all DF's within given start and end dates
    """

    #Variables

    #Select start and end date
    start_date, end_date = startEndDate(sensor_df["Date"], gvb_df["Date"])

    #List all df's
    df_list = [sensor_df, gvb_df, event_df]

    #################################################################################

    #Loop over all given DF's and select rows based on start and end date
    for df in df_list:
        df = df[(df["Date"] >= start_date) & (
            df["Date"] <= end_date)].reset_index().drop(columns=["index"])

    return sensor_df, gvb_df, event_df

def calculateWeights(stations, df, station_scaler_filename):
    """
    This function returns a dict with scaled rbk kernels, representing the distance between each station and sensor. 

    Parameters:
    - stations (list): all relevant stations
    - df (df): where the latitudes and longitudes of each station and sensor are stored
    - station_scaler_filename (str): where the scalar for station weights should be stored

    Returns: Dict with all scaled weights per sensor, per station
    """

    #Variables

    #List all sensors present in full dataset
    sensors = df["Sensor"].unique()

    #List where the rbf kernels of all stations, in relation to the sensor, will be saved
    weights = []

    #Scaler for station kernel data
    scaler = StandardScaler()

    #Dict for rbf weight positions in the weights list
    weights_dict = {}

    #################################################################################

    #Loop over all the sensors
    for sensor in sensors:

        #Make an array with the latitude and longitude of the sensor
        y = np.array([df[df["Sensor"] == sensor].reset_index()["SensorLatitude"][0],
                      df[df["Sensor"] == sensor].reset_index()["SensorLongitude"][0]]).reshape(1, -1)

        #Dict where the rbf kernels of all stations, in relation to the sensor, will be saved
        stations_dict = {}

        #Loop over all stations
        for station in stations:

            #Make an array with the latitude and longitude of the station
            x = np.array([df[station + " Lat"][0],
                          df[station + " Lon"][0]]).reshape(1, -1)

            #Save the resulting weight of the RBF kernel between the y(sensor) and x(station) coordinates
            weights.append(rbf_kernel(x, y)[0, 0])

            #Save the position of the weight in the list
            stations_dict[station] = len(weights) - 1

        #Save all te rbf kernel weights positions of the list
        weights_dict[sensor] = stations_dict

    #################################################################################

    #Convert list to np array and reshape the array
    weights = np.asarray(weights)
    weights = weights.reshape(-1, 1)

    #Scale the weights and save the scaler for later use
    weights = scaler.fit_transform(weights)
    pickle.dump(scaler, open(station_scaler_filename, 'wb'))

    #################################################################################

    #Loop over weights dict and replace the rbf weights positions with the actual weights
    for k, v in weights_dict.items():
        for station in stations:
            v[station] = weights[v[station]]

    return weights_dict


def constructFullDF(sensor_df, gvb_df, event_df, stations, station_scaler_filename):
    """
    This function combines all the previously constructed DF's and merges them into one. In addition, time is transformed into a cyclic continuous feature.

    Parameters:
    - sensor_df (df): sensor data
    - gvb_df (df): gvb data
    - event_df (df): event data
    - station_scaler_filename (str): where the scalar for station weights should be stored

    Returns: Full GVB that contains all relevant data
    """

    #Combine DF's
    gvb_sensor_df = pd.merge(gvb_df, sensor_df, on=[
                            "Date", "Hour", "weekday"], how="outer")
    full_df = pd.merge(gvb_sensor_df, event_df, on=["Date"], how="outer")

    #################################################################################

    #Sort keys on date
    full_df = full_df.sort_values(
        by=["Date"]).reset_index().drop(columns=["index"])

    #Fill NaN values with 0.0
    full_df = full_df.fillna(0.0)

    #Add columns for the cos and sin of month, day and year
    full_df = full_df.assign(Year=0, month_sin=0, month_cos=0,
                             day_sin=0, day_cos=0, hour_sin=0, hour_cos=0)

    for station in stations:
        full_df[station + " score"] = 0
        full_df[station + " weight"] = 0

    #################################################################################

    #Construct dict with station weigths
    station_weights = calculateWeights(stations, full_df, station_scaler_filename)

    #################################################################################

    #Transform DF to Dict
    time_dict = full_df.to_dict("index")

    #Transform Date to seperate year, month, day and hour. And transform month, day, hour to cos/sin to make it circular
    for k, v in time_dict.items():
        v["Year"] = v["Date"].year

        v["month_sin"] = np.sin(2 * np.pi * v["Date"].month / 12)
        v["month_cos"] = np.cos(2 * np.pi * v["Date"].month / 12)

        v["day_sin"] = np.sin(2 * np.pi * v["Date"].day / 365)
        v["day_cos"] = np.cos(2 * np.pi * v["Date"].day / 365)

        v["hour_sin"] = np.sin(2 * np.pi * v["Hour"] / 2400)
        v["hour_cos"] = np.cos(2 * np.pi * v["Hour"] / 2400)

        #Loop over all stations
        for station in stations:

            #Add a station score, which is the weight multiplied with total passengers
            v[station + " score"] = float(station_weights[v["Sensor"]][station] * (
                v[station + " Arrivals"] + v[station + " Departures"]))

            #Add station weight 
            v[station +
                " weight"] = float(station_weights[v["Sensor"]][station])

    #Transform dict back to DF
    full_df = pd.DataFrame.from_dict(
        time_dict, orient="index").reset_index().drop(columns="index")

    #################################################################################

    #Drop nonrelevant columns
    for station in stations:
        full_df.drop(columns={station + " Arrivals",
                              station + " Departures"}, inplace=True)

    return full_df


def fullDF(sensor_df, gvb_df, event_df, station_scaler_filename):
    """
    This functions constructs the full DF by combining previously constructed DF's

    Parameters:
    - sensor_df (df): sensor data
    - gvb_df (df): gvb data
    - event_df (df): event data
    - station_scaler_filename (str): where the scalar for station weights should be stored

    Returns: Full DF with all relevant data
    """

    #Import the needed CSV files
    sensor_df, gvb_df, event_df = importData(sensor_df, gvb_df, event_df)

    #Change start and end date of DF's
    sensor_df, gvb_df, event_df = changeStartEndDate(
        sensor_df, gvb_df, event_df)

    #Form full DF
    full_df = constructFullDF(
        sensor_df, gvb_df, event_df, station_scaler_filename)

    return full_df
