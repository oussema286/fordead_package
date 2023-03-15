import pandas as pd
from shapely.geometry import Polygon
import json
import rasterio
import xarray as xr
import geopandas as gp
import pandas as pd
import ast
from pathlib import Path
from scipy.linalg import lstsq
from fordead.masking_vi import get_dict_vi
import numpy as np

from fordead.masking_vi import compute_vegetation_index
from fordead.import_data import TileInfo, get_band_paths, get_raster_metadata

def filter_args(func,param_dict,combs):
    param_filter_list = func.__code__.co_varnames[:func.__code__.co_argcount]
    args = {variable : dict(zip(param_dict.keys(),combs))[variable] for variable in param_filter_list if variable in dict(zip(param_dict.keys(),combs))}
    return args

def already_existing_test(df1,df2):
    common_columns = df2.columns.intersection(df1.columns)

    all_df = pd.merge(df1[common_columns], df2[common_columns], 
                      on=list(common_columns), how='left', indicator='exists')
        
    already_existing_test_ids = df1[all_df["exists"] == "both"]["test_id"]
    if len(already_existing_test_ids) != 0:
        return already_existing_test_ids.values[0]
    else:
        return None

def get_test_id(test_info_path, tile_parameters_dataframe):
    if test_info_path.exists():
        test_info_dataframe = pd.read_csv(test_info_path, dtype = str)
        existing_test_id = already_existing_test(test_info_dataframe, tile_parameters_dataframe)
        if existing_test_id is not None:
            print("Already existing test with the same parameters (test_id : " + str(existing_test_id) + ")\nResults were not copied\n")
            test_id =  None
        else:
            test_id = test_info_dataframe["test_id"].astype(int).max()+1
    else:
        test_id = 1
        
    return test_id
        
def combine_validation_results(data_directory, target_directory):
    
    #Di déjà un fichier, comparer les paramètres, si pas de différence : même test, si on retrouve des IdZone, erreur.
    #rajouter csv avec numéros des tests et paramètres
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()

    state_obs_path = target_directory / 'state_obs.csv'
    pixel_obs_path = target_directory / 'pixel_obs_info.csv'
    test_info_path = target_directory / 'test_info.csv'
    
    tile.add_dirpath("compared_validation", target_directory)

    state_dataframe = pd.read_csv(tile.paths["validation"] / 'state_obs.csv')
    pixel_info_dataframe = pd.read_csv(tile.paths["validation"] / 'pixel_obs_info.csv')
        
    tile_parameters = tile.parameters
    for key in tile_parameters:
        tile_parameters[key] = str(tile_parameters[key])
    del tile.parameters["Overwrite"] #Overwrite ne devrait pas être dans les paramètres
    tile_parameters_dataframe = pd.DataFrame(data=tile_parameters, index=[0])
    
    test_id = get_test_id(test_info_path, tile_parameters_dataframe)
    
    if test_id is not None:
        tile_parameters_dataframe["test_id"] = test_id
        state_dataframe["test_id"] = test_id
        pixel_info_dataframe["test_id"] = test_id

        tile_parameters_dataframe.to_csv(test_info_path, mode='a', index=False,header=not(test_info_path.exists()))
    
            
        state_dataframe.to_csv(state_obs_path, mode='a', index=False,header=not(state_obs_path.exists()))
        pixel_info_dataframe.to_csv(pixel_obs_path, mode='a', index=False,header=not(pixel_obs_path.exists()))
    
# def rasterize_obs(obs_shape, name_column, raster_metadata):
#     obs_shape_json_str = obs_shape.to_json()
#     obs_shape_json_dict = json.loads(obs_shape_json_str)
#     obs_shape_jsonMask = [(feature["geometry"],feature["properties"][name_column]) for feature in obs_shape_json_dict["features"]]
    
#     rasterized_validation_data = rasterio.features.rasterize(obs_shape_jsonMask,out_shape = (raster_metadata["sizes"]["y"],raster_metadata["sizes"]["x"]) ,dtype="int16",transform=raster_metadata['transform'])  

#     return xr.DataArray(rasterized_validation_data,coords={"y" : raster_metadata["coords"]["y"],"x" : raster_metadata["coords"]["x"]}, dims=["y","x"])


# def attribute_area_to_obs(obs_shape, areas, name_column):

#     obs_area_tot = obs_shape[[name_column]]
#     obs_area_tot.insert(1, "area_tot", obs_shape.area)
    
#     obs_shape = obs_shape.merge(obs_area_tot, on= name_column, how='left')
#     obs_intersection = gp.overlay(obs_shape, areas)
    
#     obs_intersection.insert(1, "area_intersect", obs_intersection.area)
#     obs_intersection = obs_intersection[obs_intersection["area_tot"].round(3) == obs_intersection['area_intersect'].round(3)]
    
#     unvalid_obs = obs_shape[~obs_shape[name_column].isin(obs_intersection[name_column])]
#     if len(unvalid_obs) != 0:
#         print("Observations not fitting entirely on one tile found.\nThey are removed from the dataset. \nIds are the following : \n" + ', '.join(map(str, unvalid_obs[name_column])) + " ")
    
#     #Get observations with only one associated tile
#     count_data = pd.DataFrame(obs_intersection[name_column].value_counts().reset_index())
#     count_data.columns = [name_column, 'count']
#     merged = pd.merge(obs_intersection, count_data, on= name_column)
#     one_tile_obs = merged[merged["count"] == 1]
#     one_tile_obs = one_tile_obs[[name_column,"area_name"]]
    
    
#     processed_dataset =  obs_shape[obs_shape[name_column].isin(one_tile_obs[name_column])]
#     processed_dataset = processed_dataset.merge(one_tile_obs, on= name_column, how='left')
    
#     #Get observations with choice in the tile, attributing the most frequent tile
#     count_data2 = pd.DataFrame(processed_dataset["area_name"].value_counts().reset_index())
#     count_data2.columns = ["area_name", 'count']

#     unattributed_obs = obs_intersection[~obs_intersection[name_column].isin(processed_dataset[name_column])]
#     unattributed_obs = unattributed_obs.merge(count_data2, on= "area_name", how='left')
#     unattributed_obs = unattributed_obs[~pd.isnull(unattributed_obs["count"])]
    
#     choice = unattributed_obs.sort_values([name_column,'count'], ascending = False).groupby(name_column, as_index=False).first()[[name_column,"area_name"]]
#     obs_choice =  obs_shape[obs_shape[name_column].isin(choice[name_column])]
#     obs_choice = obs_choice.merge(choice, on= name_column, how='left')
    
#     processed_dataset = pd.concat([processed_dataset,obs_choice])
    
    
#     #Retrieve those with no associated tiles.
#     unattributed_obs = obs_intersection[~obs_intersection[name_column].isin(processed_dataset[name_column])]
#     while len(unattributed_obs)!=0:
#         count_data3 = pd.DataFrame(unattributed_obs["area_name"].value_counts().reset_index())
#         count_data3.columns = ["area_name", 'count']
#         choice = obs_intersection[obs_intersection["area_name"]==count_data3.sort_values(['count'], ascending = False).area_name[0]][[name_column,"area_name"]]
#         obs_choice =  obs_shape[obs_shape[name_column].isin(choice[name_column])]
#         obs_choice = obs_choice.merge(choice, on= name_column, how='left')
#         processed_dataset = pd.concat([processed_dataset,obs_choice])
#         unattributed_obs = obs_intersection[~obs_intersection[name_column].isin(processed_dataset[name_column])]
#     #######
#     processed_dataset = processed_dataset.drop(columns=["area_tot"])
#     return processed_dataset


#tested_parameters / tested_parameters_source?
def get_params(params_to_test):    # params_to_test = {}
    
    if isinstance(params_to_test, dict):
        return params_to_test
    #     #Check that variables all exist in process_tile
    elif isinstance(params_to_test, pd.DataFrame):
        param_dict = params_to_test #faux
        return param_dict
    #     #Check that variables (columns names) all exist in process_tile
    elif isinstance(params_to_test, str):
        #Check if all columns or all first rows exist
        #If not in both cases, return problematic variables là où il y en a le moins
        if Path(params_to_test).exists():
            param_dict = {}
            with open(params_to_test, 'r') as f:
                
                for line in f:
                    list_line = line.split()
                    try:
                        param_dict[list_line[0]] = [ast.literal_eval(list_line[1:][i].rstrip('\n')) for i in range(len(list_line[1:]))]
                    except:
                        param_dict[list_line[0]] = list_line[1:]
            return param_dict
        else:
            raise Exception("Text file " + params_to_test + " not found.")
    else:
        raise Exception("Unrecognized params_to_test parameter")
        
        
        
        
        
        
        
# def detect_soil(soil_data, soil_anomaly, invalid, date_index):
#     soil_data["count"]=xr.where(~invalid & soil_anomaly,soil_data["count"]+1,soil_data["count"])
#     soil_data["count"]=xr.where(~invalid & ~soil_anomaly,0,soil_data["count"])
#     soil_data["state"] = xr.where(soil_data["count"] == 3, True, soil_data["state"])
#     soil_data["first_date"] = xr.where(~invalid & (soil_data["count"] == 1) & ~soil_data["state"],date_index,soil_data["first_date"]) #Keeps index of first soil detection
    
#     return soil_data



def get_pre_masks_dataframe(reflect, list_bands):
    soil_anomaly = compute_vegetation_index(reflect, formula = "(B11 > 1250) & (B2 < 600) & ((B3 + B4) > 800)")
    shadows = (reflect[list_bands]==0).any(axis=1)
    outside_swath = reflect[list_bands[0]]<0
    invalid = shadows | outside_swath | (reflect["B2"] >= 600)
    return soil_anomaly, shadows, outside_swath, invalid

def detect_soil(data_frame, invalid, name_column):
    
    data_frame = data_frame[~invalid].reset_index()
    data_frame["group"] = ((data_frame.soil_anomaly != data_frame.soil_anomaly.shift()).cumsum())
    
    consecutive_soil = data_frame[data_frame["soil_anomaly"]].groupby(by = ["id_pixel", "group"]).size()
    soil_detect_groups = consecutive_soil[consecutive_soil >= 3].reset_index().groupby("id_pixel").first()
    int_df = pd.merge(data_frame, soil_detect_groups, how='inner', on=['id_pixel', 'group']).groupby("id_pixel").first().reset_index()[["area_name",name_column,"id_pixel","Date"]]
    return int_df

def detect_clouds_dataframe(data_frame):
    NG = compute_vegetation_index(data_frame, formula = "B3/(B8A+B4+B3)")
    cond1 = NG > 0.15
    cond2 = data_frame["B2"] > 400
    cond3 = data_frame["B2"] > 700
    cond4 =  ~(data_frame["bare_ground"] | data_frame["soil_anomaly"]) #Not detected as soil
    
    clouds = cond4 & (cond3 | (cond1 & cond2))   
    return clouds

def compute_and_apply_mask(data_frame, soil_detection, formula_mask, list_bands, apply_source_mask, sentinel_source, name_column):
 
    if soil_detection:
        mask, bare_ground = compute_masks_dataframe(data_frame, list_bands, name_column)
        data_frame["bare_ground"] = bare_ground.to_numpy()
    else:
        mask = compute_user_mask_dataframe(data_frame, formula_mask, list_bands)
        
    data_frame = data_frame[~mask.to_numpy()]
    
    if apply_source_mask:
        data_frame = data_frame[~source_mask_dataframe(data_frame["Mask"], sentinel_source)]
        
    return data_frame

def compute_user_mask_dataframe(data_frame, formula_mask, list_bands):
    shadows = (data_frame[list_bands]==0).any(axis=1)
    outside_swath = data_frame[list_bands[0]]<0
    user_mask = compute_vegetation_index(data_frame, formula = formula_mask)
    mask = shadows | outside_swath | user_mask
    return mask

def compute_masks_dataframe(data_frame, list_bands, name_column):
    
    data_frame["soil_anomaly"], shadows, outside_swath, invalid = get_pre_masks_dataframe(data_frame, list_bands)
    
    soil_data = detect_soil(data_frame, invalid, name_column)
    
    soil_data["bare_ground"] = True
    data_frame = data_frame.merge(soil_data, on=["area_name", name_column, "id_pixel","Date"], how='left')
    
    # data_frame["bare_ground"].sum()
    
    data_frame["bare_ground"] = data_frame.groupby("id_pixel").bare_ground.ffill().fillna(False)

    clouds = detect_clouds_dataframe(data_frame)
    
    # mask = shadows | clouds | outside_swath | data_frame["bare_ground"] | data_frame["soil_anomaly"]
    mask = shadows | clouds | outside_swath | (data_frame["soil_anomaly"] & ~data_frame["bare_ground"])

    # mask = shadows | clouds | outside_swath | data_frame["bare_ground"] | data_frame["soil_anomaly"]

    return mask, data_frame["bare_ground"]
  
        
def source_mask_dataframe(source_mask, sentinel_source):
    if sentinel_source=="THEIA":
        source_mask = source_mask>0
    elif sentinel_source=="Scihub" or sentinel_source=="PEPS":
        source_mask = ~source_mask.isin([4,5])
    return source_mask
        
        
def get_last_training_date_dataframe(data_frame, min_last_date_training, max_last_date_training, nb_min_date=10):
   
    
    last_training_date = data_frame[(data_frame["Date"] < min_last_date_training) & (data_frame.groupby("id_pixel").cumcount()+1 >= nb_min_date)].groupby("id_pixel").last().reset_index() #Keeping date just before min_last_date_training if enough acquisitions
    data_frame = data_frame[~data_frame["id_pixel"].isin(last_training_date["id_pixel"])]
    
    last_training_date = pd.concat([last_training_date, data_frame[(data_frame["Date"] <= max_last_date_training) & (data_frame.groupby("id_pixel").cumcount()+1 == nb_min_date)]]) # Adding pixels with nb_min_date reach before max_last_training_date
    last_training_date = last_training_date.rename(columns = {"Date" : "last_date_training"})
    
    return last_training_date[["id_pixel","last_date_training"]]

def compute_HarmonicTerms(DateAsNumber):
    return np.array([1,np.sin(2*np.pi*DateAsNumber/365.25), np.cos(2*np.pi*DateAsNumber/365.25),np.sin(2*2*np.pi*DateAsNumber/365.25),np.cos(2*2*np.pi*DateAsNumber/365.25)])

def model(date_as_number, vi, id_pixel):
    harmonic_terms = np.array([[1]*len(date_as_number), np.sin(2*np.pi*np.array(date_as_number)/365.25), np.cos(2*np.pi*np.array(date_as_number)/365.25), np.sin(2*2*np.pi*np.array(date_as_number)/365.25), np.cos(2*2*np.pi*np.array(date_as_number)/365.25)]).T
    p, _, _, _ = lstsq(harmonic_terms, vi)

    return p

def model_vi_dataframe(data_frame):
    data_frame = data_frame[data_frame["Date"] <= data_frame["last_date_training"]].reset_index()
    
    data_frame['Date'] = pd.to_datetime(data_frame['Date'])
    data_frame["date_as_number"] = (data_frame['Date'] - pd.to_datetime("2015-01-01")).dt.days
  
    coeff_vi = data_frame.groupby('id_pixel').apply(lambda x: model(x.date_as_number, x.vi, x.id_pixel)).reset_index()

    coeff_vi.columns = ["id_pixel","coeff"]
    # p, _, _, _ = lstsq(HarmonicTerms[~stack_masks][0], stack_vi.where(~stack_masks,drop=True))
    
    return coeff_vi

def prediction_vegetation_index_dataframe(data_frame):
    
    data_frame['Date'] = pd.to_datetime(data_frame['Date'])
    date_as_number = (data_frame['Date'] - pd.to_datetime("2015-01-01")).dt.days
    
    # data_frame["coeff_model"].to_numpy()
    coeff_model = np.stack(data_frame["coeff"].values)
    harmonic_terms = np.array([[1]*len(date_as_number), np.sin(2*np.pi*np.array(date_as_number)/365.25), np.cos(2*np.pi*np.array(date_as_number)/365.25), np.sin(2*2*np.pi*np.array(date_as_number)/365.25), np.cos(2*2*np.pi*np.array(date_as_number)/365.25)]).T

    # predicted_vi = prediction_vegetation_index_dataframe(coeff_model,[date])
    
    predicted_vi = np.sum(coeff_model * harmonic_terms,axis = 1)
    return predicted_vi

                                
def detection_anomalies_dataframe(data_frame, threshold_anomaly, vi, path_dict_vi):
    
    dict_vi = get_dict_vi(path_dict_vi)
    
    if dict_vi[vi]["dieback_change_direction"] == "+":
        diff_vi = data_frame["vi"] - data_frame["predicted_vi"]
    elif dict_vi[vi]["dieback_change_direction"] == "-":
        diff_vi = data_frame["predicted_vi"] - data_frame["vi"]
    else:
        raise Exception("Unrecognized dieback_change_direction in " + path_dict_vi + " for vegetation index " + vi)
    
    anomalies = diff_vi > threshold_anomaly
    
    return anomalies, diff_vi


# def get_conf_index(data_frame, dieback):
#     periods = dieback[dieback.id_pixel == data_frame["id_pixel"].iloc[0]]

    
#     stress_index_list = []
#     for index, period in periods.iterrows():      
#         data_period = data_frame[(data_frame["Date"] >= period['start_date']) & (data_frame["Date"] < period['end_date'])]
#         stress_index_list += [(data_period.diff_vi*range(1,len(data_period)+1)).sum()/(len(data_period)*(len(data_period)+1)/2)]

#     # id_pixel stress_period_id start_date end_date stress_index
#     periods["stress_index"] = stress_index_list
    
    
#     return periods.drop(columns=['id_pixel'])
    
    
    
def get_stress_index(data_frame, stress_periods):
    # stress_periods = stress_periods.reset_index()
    
    periods = stress_periods[stress_periods.id_pixel == data_frame["id_pixel"].iloc[0]]

    
    stress_index_list = []
    for index, period in periods.iterrows():      
        data_period = data_frame[(data_frame["Date"] >= period['start_date']) & (data_frame["Date"] < period['end_date'])]
        stress_index_list += [(data_period.diff_vi*range(1,len(data_period)+1)).sum()/(len(data_period)*(len(data_period)+1)/2)]

    # id_pixel stress_period_id start_date end_date stress_index
    periods["stress_index"] = stress_index_list
    
    
    return periods.drop(columns=['id_pixel'])
        
    # data_frame[]


def get_dated_changes(data_frame, name_column):
    
    data_frame["group"] = ((data_frame.anomaly != data_frame.anomaly.shift()).cumsum()) #Group successive rows with same anomaly value
    consecutive_anomaly = data_frame.groupby(by = [name_column,"id_pixel","group", "anomaly"]).size().reset_index(name = "size")     #Count successive rows with same anomaly value

    consecutive_anomaly = consecutive_anomaly[consecutive_anomaly["size"] >= 3]
    
    consecutive_anomaly["group2"] = ((consecutive_anomaly.anomaly != consecutive_anomaly.anomaly.shift()).cumsum())
    
    changes = consecutive_anomaly.groupby(by = [name_column,"id_pixel","group2", "anomaly"]).first().reset_index()#.drop(columns=['group2', 'size']) #Remove successive rows with same anomaly value
    # keep first date and get size at the same time could be more efficient
    
    # changes = changes[(changes.groupby("id_pixel").cumcount() !=0) | (changes.anomaly)] #Remove first group of successive false values which is not a change
    
    first_dates = data_frame.groupby(by = [name_column,"id_pixel","group"]).first().reset_index()[["id_pixel","group","Date"]]
    
    dated_changes = changes.merge(first_dates, on=["id_pixel","group"], how='left') #Rajouter la première date du groupe, perdue pendant le goup_by
    
    sizes = dated_changes.groupby(by = [name_column,"id_pixel"]).size()
    dated_changes["state"] = [item for n in sizes for item in ["start_date", "end_date"]*int((n - n % 2)/2) + ["dieback"] * (n % 2) ]
    
    return dated_changes

def stress_detection(data_frame, dated_changes, max_nb_stress_periods, name_column):
    stress = dated_changes[dated_changes["state"] != "dieback"].reset_index()

    stress["stress_period_id"] = [item for stress_id in range(0, int(len(stress) / 2)) for item in [stress_id,stress_id]]

    spread_stress = stress.pivot_table(values = "Date", index = [name_column,'id_pixel',"stress_period_id"], columns = ['state']).reset_index()
    
    # stress_data = data_frame.groupby(by = [name_column,"id_pixel"]).apply(lambda x: get_stress_index(x, spread_stress)).reset_index()
    # dieback_data = data_frame.groupby(by = [name_column,"id_pixel"]).apply(lambda x: get_conf_index(x, dieback)).reset_index()
    
    stress_data_list = []
    for i in range(max_nb_stress_periods):
        # print(i)
        stress_period = spread_stress.groupby([name_column,'id_pixel']).nth(i)
        filtered_period_dataframe = data_frame.merge(stress_period, on=[name_column,"id_pixel"], how='left') #Rajouter la première date du groupe, perdue pendant le goup_by
        filtered_period_dataframe = filtered_period_dataframe[(filtered_period_dataframe["Date"] >= filtered_period_dataframe["start_date"]) & (filtered_period_dataframe["Date"] < filtered_period_dataframe["end_date"])]
        stress_period["stress_index"] = filtered_period_dataframe.groupby(by = [name_column,"id_pixel"]).apply(lambda x : (x.diff_vi * range(1,len(x)+1)).sum()/(len(x)*(len(x)+1)/2)).to_numpy()
        stress_period["stress_period_id"] = i+1
        stress_data_list += [stress_period.reset_index()]

    stress_data = pd.concat(stress_data_list)
    stress_data = stress_data[[name_column,"id_pixel","stress_period_id","start_date","end_date", "stress_index"]]

    return stress_data

def dieback_detection(data_frame, dated_changes, name_column):
    dieback = dated_changes[dated_changes["state"] == "dieback"].drop(columns=["group2","anomaly","group","size","state"]).rename(columns = {"Date" : "first_date"})
    # dieback = dated_changes[dated_changes["state"] == "dieback"].rename(columns = {"Date" : "first_date"})[[]]
    dieback_data = data_frame.merge(dieback, on=[name_column,"id_pixel"], how='left') #Rajouter la première date du groupe, perdue pendant le goup_by
    dieback_data = dieback_data[dieback_data["Date"] >= dieback_data["first_date"]]
    
    dieback["conf_index"] = dieback_data.groupby(by = [name_column,"id_pixel"]).apply(lambda x : (x.diff_vi * range(1,len(x)+1)).sum()/(len(x)*(len(x)+1)/2)).to_numpy()

    return dieback
    # consecutive_anomaly = data_frame.groupby(by = [name_column,"id_pixel","group2", "anomaly"]).size().reset_index(name = "size")

    # consecutive_anomaly[consecutive_anomaly >= 3].groupby(by = [name_column,"id_pixel","group", "anomaly"]).size()
    # anomaly_detect_groups = consecutive_anomaly[consecutive_anomaly >= 3].reset_index().groupby("id_pixel").first()
    # int_df = pd.merge(data_frame, anomaly_detect_groups, how='inner', on=['id_pixel', 'group']).groupby("id_pixel").first().reset_index()[["id_pixel","Date"]]
