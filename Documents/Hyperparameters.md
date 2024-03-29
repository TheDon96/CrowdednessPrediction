# Hyperparameter
The files below contain the hyperparameter settings used by the scripts to generate the data. 

## [General Hyperparameters](../ParamSettings/HParams.txt)
In the *HParams.txt* file code spanning all the scripts can be set. 
- *Needed Sensors* (list): Which of the given sensors to include as ground truths in the prediction, given their data is present.
- *gaww-02*/*gaww-03* (list): These include different names for the given sensors. This setting is specific to this project, due to data constraints and may be removed.
- *stations* (list): Which stations to include as features for the predictions, given their data is present.
- *combine_data* (boolean): If **True**, the full dataset needed to train the models is constructed. If **False**, it is assumed this dataset is already present.
- *construct_models* (boolean): if **True**, the predetermined models needed for prediction are constructed (see *reg_models* and *clas_models*). If **False**, it is assumed the models are already constructed and present. 
- *remove_sensor* (boolean): If **True**, the models will be trained to make generalized predictions of unknown locations. If **False**, the models will be trained to predict unknown dates. 
- *sensor_to_remove* (str): If *remove_sensor* is **True**, this sensor will be removed during training and evaluated upon. 
- *reg_models* (list): The regression models bound to the unique ID's present in this given list, are constructed in *make_models*.  
- *clas_models* (list): The classification models bound to the unique ID's present in this given list, are constructed in *make_models*.
- *lon_low", *lon_high*, *lat_low*, *lat_high* (float): These are the coordinate borders for any custom coordinates to make predictions for generalization. This is also used for the events to find borders within the events are relevant. 

## [Input File Locations](../ParamSettings/InputFilePaths.txt)
In *InputFilePaths.txt*, the paths to the input datafiles can be set.
- *sensorData* (str): This file contains project specific ground truths of the crowdedness counts used in this project. Can be omitted from future use if file not present. 
- *coordinateData* (str): This file contains the Longitude and Latitude of t=all the relevant sensors. 
- *blipData* (str): This file contains project specific ground truths of the crowdedness counts used in this project, but in a more standardized format than *sensorData*. 
- *arrData* (str): This file contains the number of passengers that arrive at each station.  
- *deppData* (str): This file contains the number of passengers that depart at each station. 
- *eventData* (str): This file contains the date and locations of all the events in Amsterdam. 

## [Output File Locations](../ParamSettings/OutputFilePaths.txt)
In *OutputFilePaths.txt*, the paths to ouput files can be set. Default, a new dir is constructed for this, so no need to change these. 
- *lon_scaler* (model): Scaler model used for the Longitude.
- *lat_scaler* (model): Scaler model used for the Latitude. 
- *full_df* (str): Path location of where to save the full dataset. 
- *models* (str): Path to dir where all the scaler models are saved. 
- *plots* (str): Path to dir where all the plots need to be saved. 
- *reg_metrics* (str): Path to file where all the regression model results are saved.
- *clas_metrics* (str): Path to file where all the classification model results are saved.
- *gen_reg_metrics* (str): Path to file where all the generalized regression model results are saved.
- *gen_clas_metrics* (str): Path to file where all the generalized classification model results are saved.
- *rfg_model*, *xgbr_model*, *rfc_model*, *xgbc_model*, *lr*, *dc* (str): Where the saved prediction models should be saved. 
- *predictions* (str): Map where all the generated predictions should be saved. 

## [Model Parameters](../ParamSettings/ModelParams.txt)
In *ModelParams.txt*, all the model specific settings can be edited. 
- *trainTest* (float): Size of the train set
- *KFold* (int): Number of cross-validations
- *Unique model ID* (str):
    - *Score* (str): Main evaluation metric
    - *cycles* (int): Number of cycles to do for Hyperparameter testing
    - *params* (dict): Which parameters to tune, with which options, during hyperparameter tuning

## [Prediction Parameters](../ParamSettings/PredParams.txt)
In *PredParams.txt*, the parameters for generating predictions can be set. 
- *model* (str): Which model to use, to generate the predictions.
- *start_date* (str): Start date of the predictions, in the following format --> 'YYYY-MM-DD'.
- *end_date* (str): End date of the predictions, in the following format --> 'YYYY-MM-DD'.
- *add_sensors* (str): The location of the predictions
- *make_plot* (boolean): If **True**, the predictions are plotted. If **False**, the predictions are not plotted
- *generate_df* (boolean): If **True**, the data used for the predictions is generated based on known data. If **False**, the given dataset is used to generate the predictions. 
- *generalized_df* (boolean): If **True**, the model will generate predictions for generalized locations. If **False**, the model will generate predictions at known location for unknown dates. 
- *fig_x*, *fig_y* (int): size of the plot axis (*make_plot*)