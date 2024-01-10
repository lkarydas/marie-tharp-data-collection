import os
from datetime import datetime
import pandas as pd


# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)

start = datetime.now()
data_path = os.getcwd()
proq_file = 'ProQ_Logdata.csv'
output_csv_name = datetime.now().strftime('%Y%m%dT%H%M%S') + '_processed.csv'

# Time tolerance in seconds
time_tolerance = pd.Timedelta(seconds=60)

# Create empty DF
df_flow = pd.DataFrame(columns=['Timestamp', 'Flow'])


# Create DF from ProQ_logdata
df_water = pd.read_csv(proq_file, parse_dates=['Date'], date_format='%y/%m/%d')
df_water['Timestamp'] = df_water['Date'].dt.strftime('%Y%m%d') + 'T' + pd.to_datetime(df_water['Time'], format='%H:%M:%S').dt.strftime('%H%M%S%f')


depth_rows = []
gps_rows = []

# Create DFs from flowmweter and maretron files
for file in os.listdir(data_path):
    if '_flowmeter.dat' in file:
        print(f'Processing file:{file}')
        df_flow = pd.concat([df_flow, pd.read_csv(file, names=['Timestamp', 'Flow'])])

    elif '_maretron_nmea_gateway.dat' in file:
        print(f'Processing file:{file}')
        with open(file, 'r') as f:
            # Find the lines that contain '$IIDPT' or '$IIGLL' and store them to lists
            for line in f:
                if '$IIDPT' in line:
                    line = line.split(',')
                    if line[2]:
                        depth_rows.append([line[0], line[2]])

                elif '$IIGLL' in line:
                    line = line.split(',')
                    if line[2]:
                        gps_rows.append([line[0], line[2], line[3], line[4], line[5]])

if gps_rows:
    df_gps = pd.DataFrame(gps_rows, columns=['Timestamp', 'Latitude', 'NS', 'Longitude', 'WE'])

if depth_rows:
    df_depth = pd.DataFrame(depth_rows, columns=['Timestamp', 'Depth'])


# Drop duplicated data
df_depth.drop_duplicates(inplace=True)
df_gps.drop_duplicates(inplace=True)
df_flow.drop_duplicates(inplace=True)

# Processed files report
print('Files processed, working with the data collected...')
print(f'ProQ data: {len(df_water.index)} records')
print(f'Flowmeter data: {len(df_flow.index)} records')
print(f'Maretron Depth data: {len(df_depth.index)} records')
print(f'Maretron GPS data: {len(df_gps.index)} records')

# Preparing Timestamps for processing and Sort all the DFs on a Timestamp
for df in  [df_water, df_flow, df_depth, df_gps]:
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y%m%dT%H%M%S%f')
    df.sort_values('Timestamp', inplace=True)

# Merge all the data into one DF
df_new_water = pd.merge_asof(df_water, df_flow, on='Timestamp', direction='nearest', tolerance=time_tolerance)
df_new_water = pd.merge_asof(df_new_water, df_depth, on='Timestamp', direction='nearest', tolerance=time_tolerance)
df_new_water = pd.merge_asof(df_new_water, df_gps, on='Timestamp', direction='nearest', tolerance=time_tolerance)
df_new_water['Timestamp'] = df_new_water['Timestamp'].dt.strftime('%Y%m%dT%H%M%S')

# Remove column Timestamp if needed
# df_new_water.drop(['Timestamp'], axis=1, inplace=True)

### Save new merged DF to the output CSV ###
# Create new or OVERWRITE existing processed.csv output file
# df_new_water.to_csv('processed.csv', index=False)

#Create new output file on every script run
df_new_water.to_csv(output_csv_name, index=False)

end = datetime.now()
print(f'Done in {end - start}')