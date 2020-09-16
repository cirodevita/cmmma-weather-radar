import os
import xarray as xr
import pandas as pd
from csv import writer
from csv import reader


def radar_netcdf4_to_csv(file,inputdir='',outputdir=''):

    data = xr.open_dataset('TEST.nc')
    df = data.to_dataframe()
    
    
    #print(df.describe())

    df = df.dropna(axis=1, how='all')
    df = df.dropna()


    output_filename = f"DATASET_2.csv"
    df.to_csv(os.path.join(outputdir,output_filename))


if __name__=='__main__':

    netcdf4_file_directory = 'WRF5'
    output_csv_directory = 'CSV'
    
    files = os.listdir(netcdf4_file_directory)

    file_num = len(files)
    file_count = 1;
    for file in files:
        if(file.endswith('.nc')):
            print(f'[{file_count}/{file_num}] Processing {file}...',end='')
            radar_netcdf4_to_csv(file,netcdf4_file_directory,output_csv_directory)
            print('OK!')
            file_count+=1





