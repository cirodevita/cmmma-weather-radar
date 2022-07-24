import pickle
import sys

import numpy as np
import xarray as xr
from datetime import datetime, timedelta


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'usage: {sys.argv[0]} <modelFilename> <iDate>')
        exit(-1)

    modelFilename = sys.argv[1]
    loaded_model = pickle.load(open(modelFilename, 'rb'))

    iDate = sys.argv[2]
    prev_hour = datetime.strptime(iDate, '%Y%m%dZ%H') - timedelta(hours=1)
    curr_hour = datetime.strptime(iDate, '%Y%m%dZ%H')
    next_hour = datetime.strptime(iDate, '%Y%m%dZ%H') + timedelta(hours=1)

    print(prev_hour, curr_hour, next_hour)

    print("Loading wrf...")
    urlWrfPrev = f'http://193.205.230.6:8080/opendap/opendap/wrf5/d03/archive/{prev_hour.year}/{prev_hour.month:02}/{prev_hour.day:02}/wrf5_d03_{prev_hour.year}{prev_hour.month:02}{prev_hour.day:02}Z{prev_hour.hour:02}00.nc'
    urlWrfCurr = f'http://193.205.230.6:8080/opendap/opendap/wrf5/d03/archive/{curr_hour.year}/{curr_hour.month:02}/{curr_hour.day:02}/wrf5_d03_{curr_hour.year}{curr_hour.month:02}{curr_hour.day:02}Z{curr_hour.hour:02}00.nc'
    urlWrfNext = f'http://193.205.230.6:8080/opendap/opendap/wrf5/d03/archive/{prev_hour.year}/{prev_hour.month:02}/{prev_hour.day:02}/wrf5_d03_{prev_hour.year}{prev_hour.month:02}{prev_hour.day:02}Z{prev_hour.hour:02}00.nc'
    prevData = xr.open_dataset(urlWrfPrev)
    currData = xr.open_dataset(urlWrfCurr)
    nextData = xr.open_dataset(urlWrfNext)
    print("Loaded wrf!")

    variables = ['T2C', 'RH2', 'SLP', 'U10M', 'V10M', 'U1000', 'V1000', 'TC1000', 'RH1000', 'U975', 'V975', 'TC975',
                 'RH975', 'U950', 'V950', 'TC950', 'RH950', 'U925', 'V925', 'TC925', 'RH925', 'U850', 'V850', 'TC850',
                 'RH850', 'U700', 'V700', 'TC700', 'RH700', 'U500', 'V500', 'TC500', 'RH500', 'U300', 'V300', 'TC300',
                 'RH300']

    variablesDictCurr = {}
    variablesDictPrev = {}
    variablesDictNext = {}

    for variable in variables:
        print(variable)
        variablesDictCurr[variable] = currData[variable].values
        variablesDictPrev[variable] = prevData[variable].values
        variablesDictNext[variable] = nextData[variable].values

    rain_rate = np.zeros((len(currData.coords["time"]), len(currData.coords["latitude"]), len(currData.coords["longitude"])))

    for k in range(0, len(currData.coords["time"])):
        for j in range(0, len(currData.coords["latitude"])):
            for i in range(0, len(currData.coords["longitude"])):
                features = []
                for variable in variables:
                    features.append(variablesDictCurr[variable][k][j][i])
                    features.append(variablesDictPrev[variable][k][j][i])
                    features.append(variablesDictNext[variable][k][j][i])

                features = np.array(features).reshape(1, -1)
                if not np.isnan(features).any():
                    y_pred = loaded_model.predict(features)
                    rain_rate[k, j, i] = y_pred

    currData['rain_rate'] = xr.DataArray(rain_rate, dims=('time', 'latitude', 'longitude'))
    # currData.to_netcdf('output.nc')
