import pandas as pd 
import numpy as np 
import json 
import re 
import os

#Import own functions
from Code.ImportData.constructFullDataset import constructDF
from Code.Models.models import models
from Code.Prediction.Prediction import prediction
from Code.Prediction.minMaxCoordinates import minMaxCoordinates

#Dict with input file paths

def setUp():
    """
    This function imports all needed hyperparameters and sets up the directories for output data
    """
    #Dict with directories needed input data
    with open("ParamSettings/InputFilePaths.txt", "r") as f:
        input_dict = eval(f.read())

    #Dict with directories for output data
    with open("ParamSettings/OutputFilePaths.txt", "r") as f:
        output_dict = eval(f.read())

    #Dict with general hyperparamters
    with open("ParamSettings/HParams.txt", "r") as f:
        params_dict = eval(f.read())

    #Dict with model specific hyperparameters
    with open("ParamSettings/ModelParams.txt", "r") as f:
        models_dict = eval(f.read())
    
    #Dict with prediction specific hyperparameters
    with open("ParamSettings/PredParams.txt", "r") as f:
        pred_dict = eval(f.read())

    #Construct directories for output data
    if os.path.isdir("Output") == False:
        os.makedirs("Output/Datasets")
        os.makedirs("Output/Models")
        os.makedirs("Output/Plots")

    return input_dict, output_dict, params_dict, models_dict, pred_dict

def main():
    """
    This is the main function, that calls on all needed function to generate a crowdedness prediction
    """

    #Import all needed hyperparameter data
    input_dict, output_dict, params_dict, models_dict, pred_dict = setUp()

    #If dataset needs to be constructed
    if params_dict["make_fullDF"]:

        #Construct full dataset
        constructDF(input_dict, output_dict, params_dict)

        if params_dict["gen_borders"]:
            #Import full dataset and set latitude and longitude borders for the custom sensor
            full_df = pd.read_csv(output_dict["full_df"])
            params_dict["lon_max"], params_dict["lon_min"], params_dict["lat_max"], params_dict["lat_min"] = minMaxCoordinates(
                full_df)

            #Save the sensor borders in general parameters
            with open("ParamSettings/HParams.txt", "w") as f:
                f.write(str(params_dict))

    #If models need to be constructed
    if params_dict["make_models"]:

        #Construct models
        models(output_dict, params_dict, models_dict, pred_dict)

    #Generate Predictions
    # prediction(output_dict, params_dict, pred_dict)

if __name__ == '__main__':
    main()