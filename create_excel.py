import pandas as pd

# Data with Rwandan Currency Values
data = {
    'Service_Name': [
        'Radiotherapy QA', 
        'Survey Meter Calibration', 
        'TLD Personal Monitoring', 
        'X-Ray Diagnostic QA', 
        'Industrial Sterilization'
    ],
    'Revenue_2025': [4800000, 10200000, 37500000, 20000000, 15750000],
    'Revenue_2024': [4100000, 9000000, 32000000, 18500000, 12000000],
    'Client_Sector': ['Health', 'Safety', 'Health', 'Health', 'Industry']
}

# Ensure you have 'openpyxl' installed: pip install openpyxl
df = pd.DataFrame(data)
df.to_excel("rsb_dosimetry_data.xlsx", index=False)

print("✅ 'rsb_dosimetry_data.xlsx' created with Rwandan currency reference data.")
