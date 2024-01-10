import os
import numpy as np
from datetime import datetime
import pandas as pd


# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)

start = datetime.now()
data_path = os.getcwd()



# Time_tolerance - how many seconds allowed between data sets( between DPT and LL)
time_tolerance = pd.Timedelta(seconds=1)

# timelimit seconds - what is the time interval between files with data. To exclude distance covered between sessions
time_limit = 1000

# Distance_limit - distance limit between sessions.
distance_limit = 1000

# Speed_limit - calculated speed in m/s. If the limit is exceeded - data most likely is incorrect, so dropped.
speed_limit = 5


# function to convert DDM to DD and handle North/South
def convert_to_dd(ddm_str, nswe_str):
    ddm = float(ddm_str)
    degrees = int(ddm / 100)
    minutes = ddm - degrees * 100
    dd = degrees + minutes / 60
    if nswe_str in ['S', 'W']:
        dd *= -1  # Negate latitude if South or longitude if West
    return round(dd, 5)


# Function to calculate distance between two coordinates on sphere
def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = np.radians([lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    earth_radius_km = 6371.0
    return earth_radius_km * c * 1000


depth_rows = []
gps_rows = []
files_cnt = 0


for file in os.listdir(data_path):
    if '_maretron_nmea_gateway.dat' in file:
        files_cnt += 1
        print(f'Processing file: {file}')
        full_path = os.path.join(data_path, file)

        with open(full_path, 'r') as f:
            for line in f:
                if '$IIDPT' in line:
                    parts = line.strip().split(',')
                    if len(parts) >= 3 and parts[2]:
                        depth_rows.append([parts[0], parts[2]])

                elif '$IIGLL' in line:
                    parts = line.strip().split(',')
                    if len(parts) >= 6 and parts[2] and parts[3] and parts[4] and parts[5]:
                        lat_dd, lon_dd = convert_to_dd(parts[2], parts[3]), convert_to_dd(parts[4], parts[5])
                        gps_rows.append([parts[0], parts[2], parts[3], parts[4], parts[5], lat_dd, lon_dd])


if gps_rows:
    df_gps = pd.DataFrame(gps_rows, columns=['Timestamp', 'Latitude', 'NS', 'Longitude', 'WE', 'Latitude_DD', 'Longitude_DD'])

if depth_rows:
    df_depth = pd.DataFrame(depth_rows, columns=['Timestamp', 'Depth'])


# Drop duplicated data
df_depth.drop_duplicates(inplace=True)
df_gps.drop_duplicates(inplace=True)

# Processed files report
print(f'Files processed: {files_cnt} in {datetime.now() - start}, working with the data collected...')
print(f'Maretron Depth data: {len(df_depth.index)} records')
print(f'Maretron GPS data: {len(df_gps.index)} records')

# Preparing Timestamps for processing and Sort all the DFs on a Timestamp
print('Processing the data...')
for df in  [df_depth, df_gps]:
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y%m%dT%H%M%S%f')
    df.sort_values('Timestamp', inplace=True)


# Merge all the data
df_depth_gps = pd.merge_asof(df_depth, df_gps, on='Timestamp', direction='nearest', tolerance=time_tolerance)
df_depth_gps = df_depth_gps.dropna()
df_depth_gps.reset_index(drop=True, inplace=True)
# df_depth_gps.at[0, 'Distance'] = 0

# Calculate distances
df_depth_gps['Distance'] = (haversine_distance(df_depth_gps['Latitude_DD'].shift(), df_depth_gps['Longitude_DD'].shift(), df_depth_gps['Latitude_DD'], df_depth_gps['Longitude_DD'])).round(2)
df_depth_gps.at[0, 'Distance'] = 0

# Calculate time delta between timestamps
df_depth_gps['Time_delta'] = df_depth_gps['Timestamp'].diff().dt.total_seconds().round()
df_depth_gps.at[0, 'Time_delta'] = 0

# Calculate avg speed
df_depth_gps['Avg Speed'] = (df_depth_gps['Distance'] / df_depth_gps['Time_delta']).round(2)

# Drop rows where calculated speed is exceeded avg speed, distance or time limit
df_depth_gps = df_depth_gps[(df_depth_gps['Avg Speed'] < speed_limit) & (df_depth_gps['Avg Speed'] != 0)].reset_index(drop=True)
df_depth_gps = df_depth_gps[(df_depth_gps['Distance'] < distance_limit) & (df_depth_gps['Time_delta'] < time_limit)].reset_index(drop=True)

# Format the DF
df_depth_gps['Date(Y-m-d)'] = df_depth_gps['Timestamp'].dt.strftime('%Y-%m-%d')
df_depth_gps['Time'] = df_depth_gps['Timestamp'].dt.strftime('%H:%M:%S')
df_depth_gps['Timestamp'] = df_depth_gps['Timestamp'].dt.strftime('%Y%m%dT%H%M%S')

# Calculate total distance
total_distance = round(df_depth_gps['Distance'].sum(), 3)

# Write calculated total distance to file
with open (datetime.now().strftime('%Y%m%dT%H%M%S') + '_distance_travelled.txt', 'w') as f:
    if total_distance >=1000:
        f.write(f'{total_distance / 1000:.1f} km')
    else:
        f.write(f'{total_distance} m')

print(f'Calculated distance travelled: {round(total_distance/1000, 2)} km')


# Reordering the DF columns, drop service columns
output_columns = [
    'Date(Y-m-d)',
    'Time',
    'Latitude_DD',
    'Longitude_DD',
    'Depth',
    # 'Distance',
    # 'Time_delta',
    # 'Avg Speed',
]
df_depth_gps =  df_depth_gps[output_columns]


### Save the DF to the output CSV ###
# Create new or OVERWRITE existing processed.csv output file
# df_depth_gps.to_csv('processed.csv', index=False)

output_csv_name = datetime.now().strftime('%Y%m%dT%H%M%S') + '_processed.csv'
#Create new output file on every script run
df_depth_gps.to_csv(output_csv_name, index=False)

end = datetime.now()
print(f'Done in {end - start}')