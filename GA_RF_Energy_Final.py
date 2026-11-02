# -*- coding: utf-8 -*-
# %%
"""
Created on Wed Dec  4 20:01:29 2024

@author: s_kar
"""

import numpy as np
import pandas as pd
import pickle
from geneticalgorithm2 import geneticalgorithm2 as ga
import matplotlib.pyplot as plt

# Load the Random Forest model
with open('random_forest_model_final_newRange.pkl', 'rb') as f:
    rf_model = pickle.load(f)

# Load variable bounds from an Excel file
filepath = 'Merged_excells_Engy_K2_NewRange.xlsx'
df = pd.read_excel(filepath)
Tot_e = df['ENERGY_TOT_EAF']
df = df.drop(columns=['HEAT', 'DAT_EN', 'ENERGY_TOT_EAF','ENERGY_TOT_EAF_PER_TON', 'HEEL_NO'])
varbound = np.array([[df[col].min(), df[col].max()] for col in df.columns])

# Load fixed inputs from a configuration file
fixed_inputs_df = pd.read_excel("Individual_fixed_inputs.xlsx")  # Columns: "Variable" and "Value"
heel_value = fixed_inputs_df['HEEL_NO'].values
fixed_inputs_df = fixed_inputs_df.dropna(axis=1, how='all')
fixed_inputs_df = fixed_inputs_df.drop(columns=['HEEL_NO'])

# Define the evaluation function
def objective_function(individual):
    # Map the individual to a DataFrame
    inputs = pd.DataFrame([individual], columns=df.columns)
    
    # Apply fixed inputs
    for var in fixed_inputs_df.columns:
        inputs[var] = fixed_inputs_df[var]

    # Predict using the Random Forest model
    return rf_model.predict(inputs)[0]

# Update bounds for fixed inputs
scrap_idx = df.columns.get_loc("SCRAP_WEI_EAF")
for var in fixed_inputs_df.columns:
    idx = df.columns.get_loc(var)  # Find the index of the fixed variable
    varbound[idx] = [fixed_inputs_df[var].iloc[-1], fixed_inputs_df[var].iloc[-1]]  # Set bounds to the fixed value
if heel_value == 0:
    varbound[scrap_idx,:] = [40000, 60000]

elif heel_value == 1:
        varbound[scrap_idx,:] = [0, 0]

# Define the GA model
algorithm_params = {
            'max_num_iteration': 20,
            'population_size': 100,
            'mutation_probability': 0.2,
            'elit_ratio': 0.01,
            'crossover_type':'uniform',
            'parents_portion': 0.3,
            'max_iteration_without_improv': None
}

model = ga(
            function=objective_function,
            dimension=13,
            variable_type='real',
            variable_boundaries=varbound,
            algorithm_parameters=algorithm_params
)

# Run the GA
model.run(no_plot=True)
scores = model.result.last_generation.scores

plt.figure(figsize=(10,6))
plt.plot(scores[::-1], marker='o', markersize=3, linestyle='-')
plt.xlabel('Generation')
plt.ylabel('Fitness Score')
plt.title('Fitness Scores in Generations')
plt.tight_layout()
plt.text(40,110000,'Optimsed energy = '+str(int(model.result['score']))+' (KWh)')

# Output the best solution
print("Best individual:", model.result['variable'])
print("Best fitness (minimized output):", model.result['score'])

best_individual = model.result['variable']
best_fitness = model.result['score']

# Create a DataFrame to save the results
feature_names = df.columns  # Use column names from the original data
result_df = pd.DataFrame([best_individual], columns=feature_names)

# Add a column for the fitness value
result_df["TOT_ENERGY"] = best_fitness

# Save the DataFrame to an Excel file
result_df.to_excel("GA_best_individual.xlsx", index=False)

print("Best individual and fitness saved to 'best_individual.xlsx'")

plt.close()
plt.figure()
y, x = np.histogram(Tot_e, bins=20)
# Correct bin edge placement
x = [(a+x[i+1])/2.0 for i,a in enumerate(x[0:-1])]
hist = pd.Series(y, x)
w = abs(hist.index[1]) - abs(hist.index[0])
plt.bar(hist.index, hist.values, width=w , edgecolor='black', alpha=0.5, align='center')
plt.ylabel('Frequency')
plt.xlabel('Total Energy (KWh)')
plt.axvline(np.mean(Tot_e), c = "k", ls='--',  lw=2, label = f'Mean energy = {np.mean(Tot_e):.0f} (KWh)')
plt.axvline(best_fitness, c = "r", ls='-.', lw=2, label = f'Optimized energy = {best_fitness:.0f} (KWh)')
# plt.xlim(40000,160000)
plt.legend()
text_kwargs = dict(ha='center')
plt.text(120000,300, f'Relative Optimization\n{(np.mean(Tot_e)-best_fitness)/np.mean(Tot_e)*100:.2f}%',
         **text_kwargs)

# %%
