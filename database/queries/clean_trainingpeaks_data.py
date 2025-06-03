import pandas as pd
from datetime import datetime

# Read the Excel file
input_file = '../../source_data/raw/TrainingPeaksExport_2023_2025.xlsx'
df = pd.read_excel(input_file)

# Clean the data
df['Title'] = df['Title'].fillna('Workout')
df['Rpe'] = df['Rpe'].fillna(5)

# Apply RPE rules
df['Rpe'] = df.apply(lambda row: 
    8 if row['IF'] >= 0.85
    else 7 if row['IF'] >= 0.8
    else 6 if (row['WorkoutType'] == 'MTB' and row['IF'] < 0.8)
    else 6 if row['WorkoutType'] == 'Strength' and row['Rpe'] < 6
    else row['Rpe'], axis=1)

# Build timestamp for output file
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
outfile = f'../../source_data/cleaned/TrainingPeaksExport_2023_2025_cleaned_{ts}.xlsx'

# Write to new Excel file
df.to_excel(outfile, index=False)
print(f"Wrote cleaned data to: {outfile}") 