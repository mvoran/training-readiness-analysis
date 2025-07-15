import pandas as pd
from datetime import datetime

# Read the Excel file
input_file = '../../source_data/raw/TrainingPeaksExport_2023_2025.xlsx'
df = pd.read_excel(input_file)

# Clean the data
df['Title'] = df['Title'].fillna('Workout')
df['Rpe'] = df['Rpe'].fillna(5)

# Apply RPE rules
bike_workouts = ['Bike', 'MTB']
df['Rpe'] = df.apply(lambda row: 
    8 if row['WorkoutType'] in bike_workouts and row['IF'] >= 0.85
    else 7 if row['WorkoutType'] in bike_workouts and row['IF'] >= 0.8 
    else 6 if row['WorkoutType'] in bike_workouts and row['IF'] >= 0.75
    else 5 if row['WorkoutType'] in bike_workouts and row['IF'] >= 0.7   
    else 4 if row['WorkoutType'] in bike_workouts and row['IF'] >= 0.65
    else 3 if row['WorkoutType'] in bike_workouts and row['IF'] >= 0.6
    else 2 if row['WorkoutType'] in bike_workouts and row['IF'] < 0.6
    else 7 if row['WorkoutType'] == 'Strength' and row['HeartRateAverage'] >= 125
    else 6 if row['WorkoutType'] == 'Strength' and row['HeartRateAverage'] >= 105
    else 5 if row['WorkoutType'] == 'Strength'
    else row['Rpe'], axis=1)

# Build timestamp for output file
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
outfile = f'../../source_data/cleaned/TrainingPeaksExport_2023_2025_cleaned_{ts}.xlsx'

# Write to new Excel file
df.to_excel(outfile, index=False)
print(f"Wrote cleaned data to: {outfile}") 