import os
import xarray as xr
import sys


def radar_netcdf4_to_csv(file, inputdir, outputdir):
    data = xr.open_dataset(os.path.join(inputdir, file))
    df = data.to_dataframe()

    df = df.dropna(axis=1, how='all')
    df = df.dropna()

    output_filename = file.split(".")[0] + ".csv"
    df.to_csv(os.path.join(outputdir, output_filename))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'usage: {sys.argv[0]} <input directory> <output directory>')
        exit(-1)

    netcdf4_file_directory = sys.argv[1]
    output_csv_directory = sys.argv[2]

    files = os.listdir(netcdf4_file_directory)

    if not os.path.exists(output_csv_directory):
        os.mkdir(output_csv_directory)

    for file in files:
        if file.endswith('.nc'):
            print(f'Processing {file}...')
            radar_netcdf4_to_csv(file, netcdf4_file_directory, output_csv_directory)
