Code 1: Fjord surface water quality code (5 minute interval)

combine three datastreams by the datetimestamp. 
Each datastream has a different logging frequency so we need to combine at the datastream that
logs the least frequent the 3) YSI datastream logs every 5 minutes. 
By combining the 3 datastreams we will know at A) how to combine our ship lab flow-through system flowrate of water being
continously sampled with the realtime geographic position and then we can pair that to the nearest in time water quality variable of interest from so far just one device (3.YSI instrument) (dissolved oxygen, salinity, temperature, pH....).

One python code that combines all 3 files to build one new dataset that can be saved to .csv. Then I can open that up in my GIS software to easily analyze spatially.

Note: All timestamps are in UTC time, military time.

1)Ship geographic position - Ship DGPS device
file format: .dat, 20230629T133220_maretron_nmea_gateway.dat 
Note: The format of the GLL position string is Degrees Decimal Minutes (DDM). See example below

"20230629T133256448539,$IIGLL,6204.4375,N,04851.61363,W,,V,N*66"

2) flowrate - Arduino flowmeter device in units of ml/sec, see sample below
file format: .dat, 20230629T133220_flowmeter.dat

"20230629T143857486951,2.16"

time range: I think every second

3) YSI water quality data (data point every 5 minutes) sample dataset below.
file format: .csv, ProQ_Logdata.csv,  see sample data header and row below

Date	Time	DataID	Temp(C)	Pressure(mmHg)	DO(%)	DO(mg/L)	SPC(uS/cm)	SAL(ppt)	pH	NO3-N(mg/L)
23/06/29	13:53:00	specialfjord	7.2	755.2	111	11.44	38705	24.4	8.26	
