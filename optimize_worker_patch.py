
# This file patches OptimizeWorker to ensure feature names are in the correct order
import sys
import os
import pandas as pd
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QThread

# Get the correct feature order from the model
def get_model_features():
    import pickle
    with open('random_forest_model_final.pkl', 'rb') as f:
        model = pickle.load(f)
    return list(model.feature_names_in_)

# Fixed OptimizeWorker class
class PatchedOptimizeWorker(QObject):
    finished = pyqtSignal(object)
    
    def __init__(self, analytics):
        super().__init__()
        self.analytics = analytics
    
    def run(self):
        try:
            # Call a version of optimize_energy that ensures correct feature order
            result = self.safe_optimize_energy()
            self.finished.emit(result)
        except Exception as e:
            print(f"Error in OptimizeWorker: {e}")
            import traceback
            traceback.print_exc()
            self.finished.emit((0, []))  # Return a default value in case of error
    
    def safe_optimize_energy(self):
        # Get fixed inputs
        try:
            fixed_df = pd.read_excel('Individual_fixed_inputs.xlsx').dropna(axis=1, how='all')
        except:
            fixed_df = pd.DataFrame()
        
        # Get variable bounds from the analytics object
        varbound = np.array([
            [self.analytics.df_vars[c].min(), self.analytics.df_vars[c].max()]
            for c in self.analytics.df_vars.columns
        ])
        
        # Apply fixed values to bounds
        for var in fixed_df.columns:
            if var in self.analytics.df_vars.columns:
                idx = self.analytics.df_vars.columns.get_loc(var)
                val = fixed_df[var].iloc[-1]
                varbound[idx] = [val, val]
        
        # This is the critical part - ensure we use the expected feature order
        def objective(x):
            # Create DataFrame with the expected feature order
            ind = pd.DataFrame([x], columns=self.analytics.expected_features)
            
            # Apply fixed values
            for var in fixed_df.columns:
                if var in ind.columns:
                    ind[var] = fixed_df[var].iloc[-1]
            
            # Make prediction
            return self.analytics.model.predict(ind)[0]
        
        # Run the genetic algorithm
        from geneticalgorithm2 import geneticalgorithm2 as ga
        algorithm_params = {
            'max_num_iteration': 100,
            'population_size': 100,
            'mutation_probability': 0.2,
            'elit_ratio': 0.01,
            'crossover_type': 'uniform',
            'parents_portion': 0.3,
            'max_iteration_without_improv': None
        }
        
        algo = ga(
            function=objective,
            dimension=len(self.analytics.expected_features),
            variable_type='real',
            variable_boundaries=varbound,
            algorithm_parameters=algorithm_params
        )
        
        algo.run(no_plot=True)
        return float(algo.result['score']), list(algo.result['variable'])

# Install the patch by adding code to v2.py that replaces the OptimizeWorker
def apply_patch():
    from importlib import reload
    import v2
    
    # Store the original OptimizeWorker
    if not hasattr(v2, 'OriginalOptimizeWorker'):
        v2.OriginalOptimizeWorker = v2.OptimizeWorker
    
    # Replace with our patched version
    v2.OptimizeWorker = PatchedOptimizeWorker
    
    print("Patch applied successfully!")
    return True

# Apply the patch
if __name__ == "__main__":
    apply_patch()
