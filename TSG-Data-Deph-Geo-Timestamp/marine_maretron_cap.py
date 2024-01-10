import os
from datetime import datetime, timedelta
from dateutil import parser
import pandas as pd


# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)

start = datetime.now()
data_path = os.getcwd()
#data_path = '/Users/konstantinsalenkov/Downloads/Plastic_Project/Transect 2-Patapsco'
output_csv_name = datetime.now().strftime('%Y%m%dT%H%M%S') + '_processed_MicroTSG.csv'


# Time tolerance in seconds
time_tolerance = pd.Timedelta(seconds=60)


# function to convert DDM to DD and handle North/South
def convert_to_dd(ddm_str, nswe_str):
    ddm = float(ddm_str)
    degrees = int(ddm / 100)
    minutes = ddm - degrees * 100
    dd = degrees + minutes / 60
    if nswe_str in ['S', 'W']:
        dd *= -1  # Negate latitude if South or longitude if West
    return round(dd, 5)


cap_files = [file for file in os.listdir(data_path) if file.endswith('.cap')]
if not cap_files:
    print('No ".cap" files found in the folder. Exiting...')
    exit()

depth_rows = []
gps_rows = []
cap_rows = []

# Create DFs from cap and maretron files
for file in os.listdir(data_path):

    if '.cap' in file:
        print(f'Processing file:{file}')
        with open(file, 'r') as f:
            cap_file_date = datetime.strptime(f.readline().strip().replace('\u200E', '').replace('\u200f', ''), "%A, %B %d, %Y, %H:%M:%S")
            print(type(cap_file_date))
            next(f)
            for line in f:
                line = [element.strip() for element in line.strip().split(',')]
                if line and line[0].replace('.','',1).isdigit():
                    line = [cap_file_date.strftime('%Y%m%dT%H%M%S%f')] + line
                    cap_rows.append(line)
                    cap_file_date += timedelta(seconds=10)

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
                        lat_dd, len_dd = convert_to_dd(line[2], line[3]), convert_to_dd(line[4], line[5])
                        gps_rows.append([line[0], line[2], line[3], line[4], line[5], lat_dd, len_dd])

if gps_rows:
    df_gps = pd.DataFrame(gps_rows, columns=['Timestamp', 'Latitude', 'NS', 'Longitude', 'WE', 'Latitude_DD', 'Longitude_DD'])

if depth_rows:
    df_depth = pd.DataFrame(depth_rows, columns=['Timestamp', 'Depth'])


df_cap = pd.DataFrame(cap_rows, columns=['Timestamp', 'Temperature', 'Conductivity', 'Salinity'])

# Drop duplicated data
df_depth.drop_duplicates(inplace=True)
df_gps.drop_duplicates(inplace=True)
df_cap.drop_duplicates(inplace=True)




# Processed files report
print('Files processed, working with the data collected...')
print(f'Maretron Depth data: {len(df_depth.index)} records')
print(f'Maretron GPS data: {len(df_gps.index)} records')
print(f'MicroTSG data: {len(df_cap.index)} records')
# Preparing Timestamps for processing and Sort all the DFs on a Timestamp
for df in [df_cap, df_depth, df_gps]:

    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y%m%dT%H%M%S%f')
    df.sort_values('Timestamp', inplace=True)
    # df.set_index('Timestamp', inplace=True)

# Merge all the data into one DF
df_out = pd.merge_asof(df_cap, df_depth, on='Timestamp', direction='nearest', tolerance=time_tolerance)
df_out = pd.merge_asof(df_out, df_gps, on='Timestamp', direction='nearest', tolerance=time_tolerance)
df_out['Timestamp'] = df_out['Timestamp'].dt.strftime('%Y%m%dT%H%M%S')

print(df_out)

df_out.drop(['Latitude', 'NS', 'Longitude', 'WE'], axis=1, inplace=True)
df_out = df_out.dropna(subset=['Latitude_DD', 'Longitude_DD'], how='any')

### Save new merged DF to the output CSV ###
# Create new or OVERWRITE existing processed.csv output file
# df_depth_gps.to_csv('processed.csv', index=False)

#Create new output file on every script run
df_out.to_csv(output_csv_name, index=False)

end = datetime.now()
print(f'Done in {end - start}')