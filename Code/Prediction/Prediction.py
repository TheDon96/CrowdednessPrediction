import pandas as pd
import numpy as np
import random

import Code.Prediction.GenerateData as pg 
import Code.Prediction.importModels as im 

import matplotlib.pyplot as plt


def generatePredictions(model, stations, lat_scaler, lon_scaler, full_df, xgb_model,
                        output_dict, pred_dict, params_dict):
    """
    This function generates crowdedness predictions for specified sensors and dates

    Parameters:
    - sensors (list): all given sensors
    - model (model): desired model to generate predictions with
    - stations (list): all given stations
    - lat_scaler (model): trained scaler to transform given latitude
    - lon_scaler (model): trained scaler to transform given longitude
    - station_scaler (model): trained scaler transform the stations weights and scores
    - full_df (df): full dataset
    - xgb_model (boolean): check whether model == xgbr
    - passenger_df (df): average passenger counts
    - output_dict (dict): all paths of output files
    - pred_dict (dict): hyperparameters prediction

    Returns:
    - Df with all crowdedness predictions and input prediction data
    """

    #Dict to save all data in
    predict_dict = {}

    #Generate all possible dates between start and end date
    dates = pg.generateDates(pd.to_datetime(
        pred_dict["start_date"]), pd.to_datetime(pred_dict["end_date"]))

    if pred_dict["generate_df"]:
        #Construct dicts with longitude and latitude given sensors and stations
        sensor_dict = pg.defineCoordinates(pred_dict["add_sensors"], full_df)
        
        #Construct df with all needed input data to generate predictions
        df = pg.combineData(dates, pred_dict["add_sensors"], sensor_dict,
                            stations, lat_scaler, lon_scaler, full_df)
    
    elif pred_dict["generalized_df"]:
        df = full_df[full_df["Sensor"] == params_dict["sensor_to_remove"]]
    
    else:
        df = full_df[(full_df["Date"].isin(dates)) & (
            full_df["Sensor"] == pred_dict["add_sensors"])]
        
    #Remove features that are not needed for the model to generate predictions
    input_df = df.drop(
        columns={"hour", "Sensor", "Date", "SensorLongitude", "SensorLatitude"}).copy()

    #Save needed features for visualization and understanding
    predict_dict["Date"] = df["Date"].copy()
    predict_dict["Hour"] = df["hour"].copy()
    predict_dict["Sensor"] = df["Sensor"].copy()
    predict_dict["SensorLongitude"] = df["SensorLongitude"].copy()
    predict_dict["SensorLatitude"] = df["SensorLatitude"].copy()

    #Generate crowdedness predictions
    if xgb_model:
        predict_dict["CrowdednessCount"] = model.predict(
            input_df.values)
    else:
        predict_dict["CrowdednessCount"] = model.predict(input_df)

    #Convert dict to DF
    predict_df = pd.DataFrame.from_dict(predict_dict)
    
    return predict_df

def prediction(output_dict, params_dict, pred_dict):
    """
    This function calls all function needed to return predictions crowdedness

    Parameters:
    - output_dict (dict): all paths of output files
    - params_dict (dict): general hyperparameters
    - pred_dict (dict): hyperparameters prediction
    """

    #Import needed csv files
    full_df = pd.read_csv(output_dict["full_df"])
    #Save needed stations
    stations = params_dict["stations"]

    #Import needed models
    model, lat_scaler, lon_scaler, xgb_model = im.importModels(
        pred_dict["model"], output_dict)

    #Construct DF with generated predictions and needed input data for those predictions
    df = generatePredictions(model, stations, lat_scaler, lon_scaler, full_df, xgb_model,
                                output_dict, pred_dict, params_dict)

    #Save prediction data to CSV
    df.to_csv(output_dict["predictions"] +
                "{0}_Predictions.csv".format(pred_dict["model"]), index=False)
