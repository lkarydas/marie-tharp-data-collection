# Data Collection for GO-MARIE 2022
Bathymetry for Science onboard the R/V Marie Tharp (more information at the [expedition page](https://www.oceanresearchproject.org/go-marie/)).

<p align="center">
  <img src="images/logo_GoMarie.png" />
</p>

## Main data collection tool
This tool opens a list of serial ports and logs the data to text files.
### Install Python libraries

```bash
pip install absl-py pyserial colorama
```

## Data manipulation tools

### `trim_water_csv.py`
Opens a zip file (passed using the `--input` flag) and looks for a file inside the zip that the filename ends with `_data.txt`. Then opens the file, keeps a subset of the original columns and writes the data to an output CSV file (passed using the `--output` flag).

Example run:

```console
C:\GitHub\marie-tharp-data-collection\tools> python trim_water_csv.py --input="D:\Downloads\204223_20220723_2222_subset.zip" --output="output.csv"
I0730 16:22:59.391295 23524 trim_water_csv.py:42] List of files in D:\Downloads\204223_20220723_2222_subset.zip
I0730 16:22:59.391295 23524 trim_water_csv.py:44] File: 204223_20220723_2222/
I0730 16:22:59.392293 23524 trim_water_csv.py:44] File: 204223_20220723_2222/204223_20220723_2222_annotations_profile.txt
I0730 16:22:59.392293 23524 trim_water_csv.py:44] File: 204223_20220723_2222/204223_20220723_2222_data.txt
I0730 16:22:59.392293 23524 trim_water_csv.py:44] File: 204223_20220723_2222/204223_20220723_2222_events.txt
I0730 16:22:59.392293 23524 trim_water_csv.py:44] File: 204223_20220723_2222/204223_20220723_2222_metadata.txt
I0730 16:22:59.392293 23524 trim_water_csv.py:54] Found input data file: 204223_20220723_2222/204223_20220723_2222_data.txt
I0730 16:22:59.393290 23524 trim_water_csv.py:77] Success!
I0730 16:22:59.393290 23524 trim_water_csv.py:78] Written 5 lines to output.csv.
```

Data from the original file (inside the zip):

| Time                    | Conductivity | Temperature | Pressure   | Chlorophyll a | Temperature | Dissolved O2 concentration | Sea pressure | Depth     | Salinity  | Speed of sound | Specific conductivity | Dissolved O2 saturation | Density anomaly |
| ----------------------- | ------------ | ----------- | ---------- | ------------- | ----------- | -------------------------- | ------------ | --------- | --------- | -------------- | --------------------- | ----------------------- | --------------- |
| 2022-07-23 22:22:03.938 | 0.0034761    | 3.4269714   | 10.1338205 | 5.2486572     | 4.4410000   | 345.8651123                | 0.0013208    | 0.0013101 | 0.0027279 | 1418.9885254   | 5.9121561             | 83.2099991              | -0.0252890      |
| 2022-07-23 22:22:04.000 | 0.0031264    | 3.4262695   | 10.1372709 | 10.5589600    | 4.4410000   | 345.8656921                | 0.0047712    | 0.0047323 | 0.0024951 | 1418.9851074   | 5.3174953             | 83.2084579              | -0.0254670      |
| 2022-07-23 22:22:04.063 | 0.0023884    | 3.4255066   | 10.1346855 | 19.6989746    | 4.4410000   | 345.8668213                | 0.0021858    | 0.0021680 | 0.0020143 | 1418.9807129   | 4.0623426             | 83.2067642              | -0.0258765      |
| 2022-07-23 22:22:04.125 | 0.0036366    | 3.4245911   | 10.1437836 | 23.4371338    | 4.4410000   | 345.8649902                | 0.0112839    | 0.0111919 | 0.0028340 | 1418.9776611   | 6.1855803             | 83.2047729              | -0.0251748      |


Data that the tool outputs:

| Speed of sound | Temperature | Salinity  | Conductivity | Density anomaly | Pressure   |
| -------------- | ----------- | --------- | ------------ | --------------- | ---------- |
| 1418.9885254   | 3.4269714   | 0.0027279 | 0.0034761    | -0.025289       | 10.1338205 |
| 1418.9851074   | 3.4262695   | 0.0024951 | 0.0031264    | -0.025467       | 10.1372709 |
| 1418.9807129   | 3.4255066   | 0.0020143 | 0.0023884    | -0.0258765      | 10.1346855 |
| 1418.9776611   | 3.4245911   | 0.002834  | 0.0036366    | -0.0251748      | 10.1437836 |