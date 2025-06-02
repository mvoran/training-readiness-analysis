import pandas as pd
from datetime import datetime

# Read the Excel file
input_file = '../../source_data/TrainingPeaksExport_2023_2025.xlsx'
df = pd.read_excel(input_file)

# Clean the data
df['title'] = df['title'].fillna('Workout')

# Apply RPE rules
df['rpe'] = df.apply(lambda row: 
    8 if row['if'] >= 0.85
    else 7 if row['if'] >= 0.8
    else 6 if (row['workouttype'] == 'MTB' and row['if'] < 0.8)
    else 6 if row['workouttype'] == 'Strength'
    else row['rpe'], axis=1)

# Build timestamp for output file
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
outfile = f'../../source_data/TrainingPeaksExport_2023_2025_cleaned_{ts}.xlsx'

# Write to new Excel file
df.to_excel(outfile, index=False)
print(f"Wrote cleaned data to: {outfile}") 