import sys
import os
import glob
import xarray as xr
import pandas as pd
import time
import warnings
warnings.simplefilter("ignore")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'usage: {sys.argv[0]} <input directory> <output directory>')
        exit(-1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    files = glob.glob(input_directory + '/*.nc')
    files.sort()

    for idx in range(1, len(files)-1):
        currentFile = files[idx]
        previousFile = files[idx - 1]
        nextFile = files[idx + 1]

        currentData = xr.open_dataset(currentFile)
        previousData = xr.open_dataset(previousFile)
        nextData = xr.open_dataset(nextFile)

        variables = list(currentData.keys())

        dataset = {}
        variablesDictCurr = {}
        variablesDictPrev = {}
        variablesDictNext = {}

        for variable in variables:
            variablesDictCurr[variable] = currentData[variable].values
            variablesDictPrev[variable] = previousData[variable].values
            variablesDictNext[variable] = nextData[variable].values

        start_time = time.time()

        for k in range(0, len(currentData.coords["time"])):
            for j in range(0, len(currentData.coords["latitude"])):
                for i in range(0, len(currentData.coords["longitude"])):
                    for variable in variables:
                        currentValues = variablesDictCurr[variable][k][j][i]
                        previousValues = variablesDictPrev[variable][k][j][i]
                        nextValues = variablesDictNext[variable][k][j][i]

                        if variable not in dataset:
                            dataset[variable] = [currentValues]
                            dataset[variable + "-1H"] = [previousValues]
                            dataset[variable + "+1H"] = [nextValues]
                        else:
                            dataset[variable].append(currentValues)
                            dataset[variable + "-1H"].append(previousValues)
                            dataset[variable + "+1H"].append(nextValues)

        print("--- %s seconds ---" % (time.time() - start_time))

        df = pd.DataFrame(data=dataset)
        df = df.dropna(axis=0, how='all')
        df = df.dropna()

        output_filename = currentFile.split("/")[-1].split(".")[0] + ".csv"
        df.to_csv(os.path.join(output_directory, output_filename))
