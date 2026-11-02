import pickle
import pandas as pd

# Load the model
try:
    with open('random_forest_model_final.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully")
    print("Feature names in model:", model.feature_names_in_)
    
    # Load the data
    try:
        df = pd.read_excel('Merged_excells_Engy_Ct_K2_Sf_Nf_Tf - Copy.xlsx')
        print("\nData loaded successfully")
        print("Columns in data:", df.columns.tolist())
        
        # Check for feature name mismatches
        data_columns = df.drop(columns=['HEAT', 'DAT_EN', 'ENERGY_TOT_EAF']).columns.tolist()
        model_features = model.feature_names_in_.tolist()
        
        print("\nComparing features:")
        print("Data columns (excluding HEAT, DAT_EN, ENERGY_TOT_EAF):", len(data_columns))
        print("Model features:", len(model_features))
        
        # Check if there are any differences
        in_data_not_model = set(data_columns) - set(model_features)
        in_model_not_data = set(model_features) - set(data_columns)
        
        if in_data_not_model:
            print("\nFeatures in data but not in model:", in_data_not_model)
        if in_model_not_data:
            print("\nFeatures in model but not in data:", in_model_not_data)
            
        # Check order
        if data_columns != model_features:
            print("\nWARNING: Feature order doesn't match!")
            print("Data columns order:", data_columns)
            print("Model features order:", model_features)
        else:
            print("\nFeature order matches.")
            
    except Exception as e:
        print("Error loading data:", e)
except Exception as e:
    print("Error loading model:", e) 