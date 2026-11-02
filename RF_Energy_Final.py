# -*- coding: utf-8 -*-
# %%
"""
Created on Wed Sep 18 19:56:41 2024

@author: s.karimpouli
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import pickle

filepath = 'Merged_excells_Engy_Ct_K2_Sf_Nf_Tf.xlsx'
df = pd.read_excel(filepath)
df = df.drop(columns=[])#'GAS_MEATN_EAF', 'HEEL_NO'

# Splitting the dataframe into input X and output y
X = df.iloc[:, :-1]
print(X)
y = df.iloc[:, -1]

# Split the data into training, validation, and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=40)
Heat_num_test = X_test["HEAT"]
X_train, X_test = X_train.iloc[:,2:], X_test.iloc[:,2:] # Removing heat number

# Random Forest Regressor
rf = RandomForestRegressor(n_estimators=100, random_state=42)

# Train the model
rf.fit(X_train, y_train)

# Save the model
# dump(rf, 'random_forest_model.joblib')
# with open('random_forest_model_final.pkl', 'wb') as f:
#     pickle.dump(rf, f)

# Load the model
# rf = load('random_forest_model.joblib')
# with open('random_forest_model.pkl', 'wb') as f:
#     pickle.dump(rf, f)

# Evaluate the model on the test set
y_test_pred = rf.predict(X_test)

test_mse = mean_squared_error(y_test, y_test_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)
# print(f"Test MSE: {test_mse}, Test MAE: {test_mae}")
plt.plot(y_test, y_test_pred,'.')
plt.plot([np.min(y_test),np.max(y_test)],[np.min(y_test),np.max(y_test)],'--k')
plt.text(0.4*(np.max(y_test)+np.min(y_test)),0.6*(np.max(y_test_pred)+np.min(y_test_pred)),
         '$R^2$ = '+str(np.round(r2_score(y_test, y_test_pred)*100, decimals=2)))
plt.xlabel('True Total Energy (KWh)')
plt.ylabel('Predicted Total Energy (KWh)')
plt.tight_layout()

importances = rf.feature_importances_
feature_names = df.columns[2:-1]

mdi_importances = pd.Series(
    rf[-1].feature_importances_, index=feature_names
).sort_values(ascending=True)
plt.figure()
ax = mdi_importances.plot.barh()
ax.set_title("Random Forest Feature Importances")
ax.figure.tight_layout()

plt.figure()
df_y = pd.DataFrame({"HEAT_NUMBER": Heat_num_test, "y_test": y_test, "y_pred": y_test_pred})
df_y = df_y.sort_values(by=['HEAT_NUMBER'])

plt.plot(df_y['HEAT_NUMBER'], df_y['y_test'], "-o", label="True")
plt.plot(df_y['HEAT_NUMBER'], df_y['y_pred'], "-o",label="Predicted")
plt.xlim(321050, 321450)
plt.ylim(80000,130000)
plt.xlabel('Heat number (furnace: 2, year: 1403)')
plt.ylabel('Total Energy (KWh)')
plt.legend()
plt.tight_layout()
plt.show()

# %%
