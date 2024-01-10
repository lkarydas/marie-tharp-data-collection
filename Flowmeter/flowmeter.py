import os
from datetime import datetime
import pandas as pd
from openpyxl.styles import Font

# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)

start = datetime.now()
data_path = os.getcwd()
# data_path = '/Users/yuri/Library/CloudStorage/Dropbox/PycharmProjects/marine/Files/2023/'

flow_rows = []

# Create DF from flowmweter.dat
for file in os.listdir(data_path):
    if '_flowmeter.dat' in file:
        file_path = os.path.join(data_path, file)
        print(f'Processing file:{file_path}')
        with open(file_path, 'r') as f:
            flow_rows.extend(line.strip().split(',') for line in f)
        if flow_rows:
            df_flow = pd.DataFrame(flow_rows, columns=['Timestamp', 'Flow'])
            df_flow.drop_duplicates(inplace=True)
            df_flow['Flow'] = pd.to_numeric(df_flow['Flow'])
            df_flow = df_flow[df_flow['Flow'] != 0]
        else:
            continue



        # Processed files report
        print(f'Flowmeter data: {len(df_flow.index)} records')

        # Preparing Timestamps for processing and Sort
        df_flow['Timestamp'] = pd.to_datetime(df_flow['Timestamp'], format='%Y%m%dT%H%M%S%f')
        df_flow.sort_values('Timestamp', inplace=True)

        first_timestamp = df_flow['Timestamp'].iloc[0]
        last_timestamp = df_flow['Timestamp'].iloc[-1]

        # Calculate values
        time_difference = round((last_timestamp - first_timestamp).total_seconds() / 60, 2)
        avg_flow = round(df_flow['Flow'].mean(), 2)
        total_flow_liters = round(time_difference * avg_flow, 2)
        total_flow_cbm = round(total_flow_liters/1000, 2)


        # print(f'Time of Transect Start: {first_timestamp} ')
        # print(f'Time of Transect End: {last_timestamp} ')
        # print(f'Duration of Transect in minutes : {time_difference}')
        # print(f'Average liters per min: {avg_flow}')
        # print(f'Total Volume of Water in Liters: {total_flow_liters}')
        # print(f'Total Volume of Water in Cubical Meters: {total_flow_cbm}')

        summary_data = pd.DataFrame({
            'Variable Name': [
                'Time of Transect Start',
                'Time of Transect End',
                'Duration of Transect in minutes',
                'Average liters per min',
                'Total Volume of Water in Liters',
                'Total Volume of Water in Cubical Meters',
                'Number of Particles detected in the Total Volume',
                'Number of Particles in a Cubical Meter'
            ],
            'Value': [
                first_timestamp,
                last_timestamp,
                time_difference,
                avg_flow,
                total_flow_liters,
                total_flow_cbm,
                None,
                '=ROUND(B7/B6,2)'
            ]
        })

        with pd.ExcelWriter(file_path.replace('.dat','.xlsx'), engine='openpyxl') as writer:
            summary_data.to_excel(writer, index=False, header=False)

            # Get the workbook and active sheet
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']  # Replace 'Sheet1' with the actual sheet name

            # Apply Bold to the 'A' column
            for cell in worksheet['A']:
                cell.font = Font(bold=True)

            # Apply auto width to columns
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in worksheet[column_letter]:
                    cell_length = len(str(cell.value))
                    max_length = max(max_length, cell_length)

                # Set the column width
                worksheet.column_dimensions[column_letter].width = max_length + 2


end = datetime.now()
print(f'Done in {end - start}')