import pandas as pd
import numpy as np

# خواندن فایل اکسل
excel_file = 'Merged_excells_Engy_Ct_K2_Sf_Nf_Tf.xlsx'
df = pd.read_excel(excel_file)

# نمایش تعداد سطرها
num_samples = len(df)
print(f"num_samples = {num_samples}  # تعداد سطرهای داده")

# لیست ستون‌های مورد نیاز
needed_columns = [
    'POWER_ON_TAP', 'DRI_EAF', 'ANTHRACITE_EAF', 'GAS_MEATN_EAF', 'COFE_COKE_EAF',
    'HEEL_NO', 'LIME_EAF', 'OXCYGEN_EAF', 'CARBON_EAF', 'TAP_TO_TAP_SS',
    'GRAPHIT_LANCE_EAF', 'DOLOMIT_LIME_EAF', 'C_CLOX_EAF', 'FIRST_TEMP_EAF',
    'POWER_OFF_TAP', 'TAP_WEI_TON', 'TAP_TEMP_EAF', 'ARIV_O2_PPM',
    'GRAPHIT_EAF', 'SCRAP_WEI_EAF', 'PDWR_LIME', 'COKE_EAF',
    'HEAT', 'DAT_EN', 'ENERGY_TOT_EAF'
]

# ایجاد یک فایل برای ذخیره خروجی
with open('excel_data_for_v2.py', 'w', encoding='utf-8') as f:
    f.write("# کد تولید شده برای استفاده در v2.py\n")
    f.write("# این کد را در محل مناسب در فایل v2.py جایگزین کنید\n\n")
    
    f.write(f"# تعداد سطرهای داده در فایل اکسل\n")
    f.write(f"num_samples = {num_samples}\n\n")
    
    f.write("# داده‌های واقعی از فایل اکسل\n")
    f.write("data = {\n")
    
    # برای هر ستون، مقادیر را استخراج کرده و به شکل لیست پایتون ذخیره می‌کنیم
    for column in needed_columns:
        if column in df.columns:
            # تبدیل ستون به لیست و حذف NaN ها
            values = df[column].fillna(0).tolist()
            f.write(f"    '{column}': {values},\n")
        else:
            f.write(f"    # '{column}' در فایل اکسل یافت نشد\n")
    
    f.write("}\n\n")
    f.write("# ایجاد DataFrame از دیکشنری داده‌ها\n")
    f.write("df = pd.DataFrame(data)\n")

print("\nفایل 'excel_data_for_v2.py' با موفقیت ایجاد شد.")
print("این فایل شامل کد پایتون است که می‌توانید در v2.py جایگزین کنید.")
print("دستورالعمل‌های استفاده:")
print("1. کد زیر را در v2.py حذف کنید:")
print("""
# Instead of loading from Excel file, create the necessary data structures directly
# Create embedded data for the dataset that was previously loaded from Excel

# Sample data values - REPLACE THESE WITH YOUR ACTUAL DATA FROM THE EXCEL FILE
# These are synthetic values just to demonstrate the approach
num_samples = 200  # Adjust to match your actual data size

# Create a dictionary to hold the data
data = {}

# Add columns for all expected features with random values within valid ranges
for feat in self.expected_features:
    label = self.feature_map.get(feat)
    if label in self.input_ranges:
        min_val, max_val = self.input_ranges[label]
        data[feat] = np.random.uniform(min_val, max_val, num_samples)
    else:
        # Default range if not specified
        data[feat] = np.random.uniform(0, 1000, num_samples)

# Add additional required columns that were in the Excel
data['HEAT'] = np.arange(1, num_samples + 1)
data['DAT_EN'] = np.random.uniform(0, 100, num_samples)

# Generate synthetic Total Energy values for demonstration
# In a real implementation, replace this with actual values from your Excel
data['ENERGY_TOT_EAF'] = np.random.uniform(300000, 700000, num_samples)
""")
print("2. کد موجود در فایل 'excel_data_for_v2.py' را جایگزین آن کنید.")
print("3. مطمئن شوید کد 'df = pd.DataFrame(data)' را نیز حفظ کرده‌اید.")