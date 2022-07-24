import sys
import os
import netCDF4 as nc
import numpy as np
from wrf import getvar
from shapely.geometry import Polygon
from scipy.interpolate import griddata


def interp(srcLons, srcLats, invar2d, dstLons, dstLats, value):
    py = srcLats.flatten()
    px = srcLons.flatten()
    z = np.array(invar2d).flatten()
    z[z == value] = 'nan'
    X, Y = np.meshgrid(dstLons, dstLats)
    outvar2d = griddata((px, py), z, (X, Y), method='nearest', fill_value=value)
    return outvar2d


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'usage: {sys.argv[0]} <input directory> <output directory>')
        exit(-1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    hours = os.listdir(input_dir)

    for hour in hours:
        scan_path = os.path.join(input_dir, hour)
        print(scan_path)
        radar_scan = nc.Dataset(scan_path, 'r')

        scan_lat = radar_scan['lat'][:, 0]
        scan_lon = radar_scan['lon'][0]

        yyyy = hour[3:7]
        mm = hour[8:10]
        dd = hour[11:13]
        hh = hour[14:16]
        wrf = f'http://193.205.230.6:8080/opendap/opendap/wrf5/d03/archive/{yyyy}/{mm}/{dd}/wrf5_d03_{yyyy}{mm}{dd}Z{hh}00.nc'
        model = nc.Dataset(wrf)
        model_lat = model['latitude'][:]
        model_lon = model['longitude'][:]
        time = model["time"][:]

        wrfPolygon = Polygon(zip([model_lat[0], model_lat[-1], model_lat[-1], model_lat[0], model_lat[0]],
                                 [model_lon[0], model_lon[0], model_lon[-1], model_lon[-1], model_lon[0]]))

        radarPolygon = Polygon(zip([scan_lat[0], scan_lat[-1], scan_lat[-1], scan_lat[0], scan_lat[0]],
                                   [scan_lon[0], scan_lon[0], scan_lon[-1], scan_lon[-1], scan_lon[0]]))

        intersection = wrfPolygon.intersection(radarPolygon).exterior.coords.xy

        min_lat = intersection[0][1]
        max_lat = intersection[0][0]
        min_lon = intersection[1][0]
        max_lon = intersection[1][2]

        grid_lat = np.linspace(scan_lat[(np.abs(scan_lat - min_lat)).argmin()],
                               scan_lat[(np.abs(scan_lat - max_lat)).argmin()],
                               (np.abs(scan_lat - max_lat)).argmin() - (np.abs(scan_lat - min_lat)).argmin())
        grid_lon = np.linspace(scan_lon[(np.abs(scan_lon - min_lon)).argmin()],
                               scan_lon[(np.abs(scan_lon - max_lon)).argmin()],
                               (np.abs(scan_lon - max_lon)).argmin() - (np.abs(scan_lon - min_lon)).argmin())
        X, Y = np.meshgrid(grid_lon, grid_lat)

        model_lat = model_lat[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin()]
        model_lon = model_lon[(np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin()]

        # REFLECTIVITY
        reflectivity = radar_scan['reflectivity'][::]
        reflectivity = reflectivity[(np.abs(scan_lat - min_lat)).argmin():(np.abs(scan_lat - max_lat)).argmin(),
                       (np.abs(scan_lon - min_lon)).argmin():(np.abs(scan_lon - max_lon)).argmin()]
        # RAIN RATE
        rainRate = radar_scan['rain_rate'][::]
        rainRate = rainRate[(np.abs(scan_lat - min_lat)).argmin():(np.abs(scan_lat - max_lat)).argmin(),
                   (np.abs(scan_lon - min_lon)).argmin():(np.abs(scan_lon - max_lon)).argmin()]
        # T2C
        T2C = getvar(model, "T2C", meta=False)
        T2C = T2C[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
              (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # RH2
        RH2 = getvar(model, "RH2", meta=False)
        RH2 = RH2[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
              (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # U1000
        U1000 = getvar(model, "U1000", meta=False)
        U1000 = U1000[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # V1000
        V1000 = getvar(model, "V1000", meta=False)
        V1000 = V1000[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # TC1000
        TC1000 = getvar(model, "TC1000", meta=False)
        TC1000 = TC1000[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                 (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # RH1000
        RH1000 = getvar(model, "RH1000", meta=False)
        RH1000 = RH1000[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                 (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # U975
        U975 = getvar(model, "U975", meta=False)
        U975 = U975[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # V975
        V975 = getvar(model, "V975", meta=False)
        V975 = V975[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # TC975
        TC975 = getvar(model, "TC975", meta=False)
        TC975 = TC975[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # RH975
        RH975 = getvar(model, "RH975", meta=False)
        RH975 = RH975[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # U950
        U950 = getvar(model, "U950", meta=False)
        U950 = U950[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # V950
        V950 = getvar(model, "V950", meta=False)
        V950 = V950[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # TC950
        TC950 = getvar(model, "TC950", meta=False)
        TC950 = TC950[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # RH950
        RH950 = getvar(model, "RH950", meta=False)
        RH950 = RH950[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # U925
        U925 = getvar(model, "U925", meta=False)
        U925 = U925[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # V925
        V925 = getvar(model, "V925", meta=False)
        V925 = V925[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # TC925
        TC925 = getvar(model, "TC925", meta=False)
        TC925 = TC925[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # RH925
        RH925 = getvar(model, "RH925", meta=False)
        RH925 = RH925[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # U850
        U850 = getvar(model, "U850", meta=False)
        U850 = U850[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # V850
        V850 = getvar(model, "V850", meta=False)
        V850 = V850[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # TC850
        TC850 = getvar(model, "TC850", meta=False)
        TC850 = TC850[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # RH850
        RH850 = getvar(model, "RH850", meta=False)
        RH850 = RH850[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # U700
        U700 = getvar(model, "U700", meta=False)
        U700 = U700[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # V700
        V700 = getvar(model, "V700", meta=False)
        V700 = V700[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # TC700
        TC700 = getvar(model, "TC700", meta=False)
        TC700 = TC700[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # RH700
        RH700 = getvar(model, "RH700", meta=False)
        RH700 = RH700[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # U500
        U500 = getvar(model, "U500", meta=False)
        U500 = U500[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # V500
        V500 = getvar(model, "V500", meta=False)
        V500 = V500[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # TC500
        TC500 = getvar(model, "TC500", meta=False)
        TC500 = TC500[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # RH500
        RH500 = getvar(model, "RH500", meta=False)
        RH500 = RH500[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # U300
        U300 = getvar(model, "U300", meta=False)
        U300 = U300[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # V300
        V300 = getvar(model, "V300", meta=False)
        V300 = V300[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # TC300
        TC300 = getvar(model, "TC300", meta=False)
        TC300 = TC300[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # RH300
        RH300 = getvar(model, "RH300", meta=False)
        RH300 = RH300[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
                (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # U10M
        U10M = getvar(model, "U10M", meta=False)
        U10M = U10M[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # V10M
        V10M = getvar(model, "V10M", meta=False)
        V10M = V10M[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
               (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]
        # SLP
        SLP = getvar(model, "SLP", meta=False)
        SLP = SLP[(np.abs(model_lat - min_lat)).argmin():(np.abs(model_lat - max_lat)).argmin() + 1,
              (np.abs(model_lon - min_lon)).argmin():(np.abs(model_lon - max_lon)).argmin() + 1]

        X_wrf5, Y_wrf5 = np.meshgrid(model_lon, model_lat)

        T2C = interp(X_wrf5, Y_wrf5, T2C, grid_lon, grid_lat, 1.e+37)
        RH2 = interp(X_wrf5, Y_wrf5, RH2, grid_lon, grid_lat, 1.e+37)
        SLP = interp(X_wrf5, Y_wrf5, SLP, grid_lon, grid_lat, 1.e+37)

        U10M = interp(X_wrf5, Y_wrf5, U10M, grid_lon, grid_lat, 1.e+37)
        V10M = interp(X_wrf5, Y_wrf5, V10M, grid_lon, grid_lat, 1.e+37)

        U1000 = interp(X_wrf5, Y_wrf5, U1000, grid_lon, grid_lat, 1.e+37)
        V1000 = interp(X_wrf5, Y_wrf5, V1000, grid_lon, grid_lat, 1.e+37)
        TC1000 = interp(X_wrf5, Y_wrf5, TC1000, grid_lon, grid_lat, 1.e+37)
        RH1000 = interp(X_wrf5, Y_wrf5, RH1000, grid_lon, grid_lat, 1.e+37)

        U975 = interp(X_wrf5, Y_wrf5, U975, grid_lon, grid_lat, 1.e+37)
        V975 = interp(X_wrf5, Y_wrf5, V975, grid_lon, grid_lat, 1.e+37)
        TC975 = interp(X_wrf5, Y_wrf5, TC975, grid_lon, grid_lat, 1.e+37)
        RH975 = interp(X_wrf5, Y_wrf5, RH975, grid_lon, grid_lat, 1.e+37)

        U950 = interp(X_wrf5, Y_wrf5, U950, grid_lon, grid_lat, 1.e+37)
        V950 = interp(X_wrf5, Y_wrf5, V950, grid_lon, grid_lat, 1.e+37)
        TC950 = interp(X_wrf5, Y_wrf5, TC950, grid_lon, grid_lat, 1.e+37)
        RH950 = interp(X_wrf5, Y_wrf5, RH950, grid_lon, grid_lat, 1.e+37)

        U925 = interp(X_wrf5, Y_wrf5, U925, grid_lon, grid_lat, 1.e+37)
        V925 = interp(X_wrf5, Y_wrf5, V925, grid_lon, grid_lat, 1.e+37)
        TC925 = interp(X_wrf5, Y_wrf5, TC925, grid_lon, grid_lat, 1.e+37)
        RH925 = interp(X_wrf5, Y_wrf5, RH925, grid_lon, grid_lat, 1.e+37)

        U850 = interp(X_wrf5, Y_wrf5, U850, grid_lon, grid_lat, 1.e+37)
        V850 = interp(X_wrf5, Y_wrf5, V850, grid_lon, grid_lat, 1.e+37)
        TC850 = interp(X_wrf5, Y_wrf5, TC850, grid_lon, grid_lat, 1.e+37)
        RH850 = interp(X_wrf5, Y_wrf5, RH850, grid_lon, grid_lat, 1.e+37)

        U700 = interp(X_wrf5, Y_wrf5, U700, grid_lon, grid_lat, 1.e+37)
        V700 = interp(X_wrf5, Y_wrf5, V700, grid_lon, grid_lat, 1.e+37)
        TC700 = interp(X_wrf5, Y_wrf5, TC700, grid_lon, grid_lat, 1.e+37)
        RH700 = interp(X_wrf5, Y_wrf5, RH700, grid_lon, grid_lat, 1.e+37)

        U500 = interp(X_wrf5, Y_wrf5, U500, grid_lon, grid_lat, 1.e+37)
        V500 = interp(X_wrf5, Y_wrf5, V500, grid_lon, grid_lat, 1.e+37)
        TC500 = interp(X_wrf5, Y_wrf5, TC500, grid_lon, grid_lat, 1.e+37)
        RH500 = interp(X_wrf5, Y_wrf5, RH500, grid_lon, grid_lat, 1.e+37)

        U300 = interp(X_wrf5, Y_wrf5, U300, grid_lon, grid_lat, 1.e+37)
        V300 = interp(X_wrf5, Y_wrf5, V300, grid_lon, grid_lat, 1.e+37)
        TC300 = interp(X_wrf5, Y_wrf5, TC300, grid_lon, grid_lat, 1.e+37)
        RH300 = interp(X_wrf5, Y_wrf5, RH300, grid_lon, grid_lat, 1.e+37)

        # SAVE NETCDF TODO: Create function
        outputFile = os.path.join(output_dir, hour)
        ncdstfile = nc.Dataset(outputFile, "w", format="NETCDF4")
        ncdstfile.createDimension("time", size=1)
        ncdstfile.createDimension("latitude", size=len(grid_lat))
        ncdstfile.createDimension("longitude", size=len(grid_lon))

        timeVar = ncdstfile.createVariable("time", "f4", "time")
        timeVar.description = "Time since initialization"
        timeVar.field = "time, scalar, series"
        timeVar.long_name = "julian day (UT)"
        timeVar.standard_name = "time"
        timeVar.calendar = "standard"
        timeVar.units = "days since 1990-01-01 00:00:00"
        timeVar.conventions = "relative julian days with decimal part (as parts of the day )"
        timeVar.axis = "T"

        lonVar = ncdstfile.createVariable("longitude", "f4", "longitude")
        lonVar.description = "Longitude"
        lonVar.long_name = "longitude"
        lonVar.units = "degrees_east"

        latVar = ncdstfile.createVariable("latitude", "f4", "latitude")
        latVar.description = "Latitude"
        latVar.long_name = "latitude"
        latVar.units = "degrees_north"

        T2CVar = ncdstfile.createVariable("T2C", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        T2CVar.description = "Temperature at 2m in Celsius"
        T2CVar.units = "C"

        RH2Var = ncdstfile.createVariable("RH2", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        RH2Var.description = "Relative humidity at 2 meters"
        RH2Var.units = "%"

        SLPVar = ncdstfile.createVariable("SLP", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        SLPVar.description = "Sea level pressure"
        SLPVar.units = "HPa"

        U10MVar = ncdstfile.createVariable("U10M", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        U10MVar.description = "grid rel. x-wind component"
        U10MVar.units = "m s-1"

        V10MVar = ncdstfile.createVariable("V10M", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        V10MVar.description = "grid rel. x-wind component"
        V10MVar.units = "m s-1"

        U1000Var = ncdstfile.createVariable("U1000", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        U1000Var.description = "grid rel. x-wind component at 1000 HPa"
        U1000Var.units = "m s-1"

        V1000Var = ncdstfile.createVariable("V1000", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        V1000Var.description = "grid rel. y-wind component at 1000 HPa"
        V1000Var.units = "m s-1"

        TC1000Var = ncdstfile.createVariable("TC1000", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        TC1000Var.description = "Temperature at 1000 HPa"
        TC1000Var.units = "C"

        RH1000Var = ncdstfile.createVariable("RH1000", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        RH1000Var.description = "Relative humidity at 1000 HPa"
        RH1000Var.units = "%"

        U975Var = ncdstfile.createVariable("U975", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        U975Var.description = "grid rel. x-wind component at 975 HPa"
        U975Var.units = "m s-1"

        V975Var = ncdstfile.createVariable("V975", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        V975Var.description = "grid rel. y-wind component at 975 HPa"
        V975Var.units = "m s-1"

        TC975Var = ncdstfile.createVariable("TC975", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        TC975Var.description = "Temperature at 975 HPa"
        TC975Var.units = "C"

        RH975Var = ncdstfile.createVariable("RH975", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        RH975Var.description = "Relative humidity at 975 HPa"
        RH975Var.units = "%"

        U950Var = ncdstfile.createVariable("U950", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        U950Var.description = "grid rel. x-wind component at 950 HPa"
        U950Var.units = "m s-1"

        V950Var = ncdstfile.createVariable("V950", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        V950Var.description = "grid rel. y-wind component at 950 HPa"
        V950Var.units = "m s-1"

        TC950Var = ncdstfile.createVariable("TC950", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        TC950Var.description = "Temperature at 950 HPa"
        TC950Var.units = "C"

        RH950Var = ncdstfile.createVariable("RH950", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        RH950Var.description = "Relative humidity at 950 HPa"
        RH950Var.units = "%"

        U925Var = ncdstfile.createVariable("U925", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        U925Var.description = "grid rel. x-wind component at 925 HPa"
        U925Var.units = "m s-1"

        V925Var = ncdstfile.createVariable("V925", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        V925Var.description = "grid rel. y-wind component at 925 HPa"
        V925Var.units = "m s-1"

        TC925Var = ncdstfile.createVariable("TC925", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        TC925Var.description = "Temperature at 925 HPa"
        TC925Var.units = "C"

        RH925Var = ncdstfile.createVariable("RH925", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        RH925Var.description = "Relative humidity at 925 HPa"
        RH925Var.units = "%"

        U850Var = ncdstfile.createVariable("U850", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        U850Var.description = "grid rel. x-wind component at 850 HPa"
        U850Var.units = "m s-1"

        V850Var = ncdstfile.createVariable("V850", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        V850Var.description = "grid rel. y-wind component at 850 HPa"
        V850Var.units = "m s-1"

        TC850Var = ncdstfile.createVariable("TC850", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        TC850Var.description = "Temperature at 850 HPa"
        TC850Var.units = "C"

        RH850Var = ncdstfile.createVariable("RH850", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        RH850Var.description = "Relative humidity at 850 HPa"
        RH850Var.units = "%"

        U700Var = ncdstfile.createVariable("U700", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        U700Var.description = "grid rel. x-wind component at 700 HPa"
        U700Var.units = "m s-1"

        V700Var = ncdstfile.createVariable("V700", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        V700Var.description = "grid rel. y-wind component at 700 HPa"
        V700Var.units = "m s-1"

        TC700Var = ncdstfile.createVariable("TC700", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        TC700Var.description = "Temperature at 700 HPa"
        TC700Var.units = "C"

        RH700Var = ncdstfile.createVariable("RH700", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        RH700Var.description = "Relative humidity at 700 HPa"
        RH700Var.units = "%"

        U500Var = ncdstfile.createVariable("U500", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        U500Var.description = "grid rel. x-wind component at 500 HPa"
        U500Var.units = "m s-1"

        V500Var = ncdstfile.createVariable("V500", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        V500Var.description = "grid rel. y-wind component at 500 HPa"
        V500Var.units = "m s-1"

        TC500Var = ncdstfile.createVariable("TC500", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        TC500Var.description = "Temperature at 500 HPa"
        TC500Var.units = "C"

        RH500Var = ncdstfile.createVariable("RH500", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        RH500Var.description = "Relative humidity at 500 HPa"
        RH500Var.units = "%"

        U300Var = ncdstfile.createVariable("U300", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        U300Var.description = "grid rel. x-wind component at 300 HPa"
        U300Var.units = "m s-1"

        V300Var = ncdstfile.createVariable("V300", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        V300Var.description = "grid rel. y-wind component at 300 HPa"
        V300Var.units = "m s-1"

        TC300Var = ncdstfile.createVariable("TC300", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        TC300Var.description = "Temperature at 300 HPa"
        TC300Var.units = "C"

        RH300Var = ncdstfile.createVariable("RH300", "f4", ("time", "latitude", "longitude"), fill_value=1.e+37)
        RH300Var.description = "Relative humidity at 300 HPa"
        RH300Var.units = "%"

        reflectivityVar = ncdstfile.createVariable("reflectivity", "f4", ("time", "latitude", "longitude"), fill_value=-99)
        rainRateVar = ncdstfile.createVariable("rainRate", "f4", ("time", "latitude", "longitude"), fill_value=-99)

        timeVar[:] = time
        lonVar[:] = grid_lon
        latVar[:] = grid_lat
        T2CVar[:] = T2C
        RH2Var[:] = RH2
        SLPVar[:] = SLP
        U10MVar[:] = U10M
        V10MVar[:] = V10M
        U1000Var[:] = U1000
        V1000Var[:] = V1000
        TC1000Var[:] = TC1000
        RH1000Var[:] = RH1000
        U975Var[:] = U975
        V975Var[:] = V975
        TC975Var[:] = TC975
        RH975Var[:] = RH975
        U950Var[:] = U950
        V950Var[:] = V950
        TC950Var[:] = TC950
        RH950Var[:] = RH950
        U925Var[:] = U925
        V925Var[:] = V925
        TC925Var[:] = TC925
        RH925Var[:] = RH925
        U850Var[:] = U850
        V850Var[:] = V850
        TC850Var[:] = TC850
        RH850Var[:] = RH850
        U700Var[:] = U700
        V700Var[:] = V700
        TC700Var[:] = TC700
        RH700Var[:] = RH700
        U500Var[:] = U500
        V500Var[:] = V500
        TC500Var[:] = TC500
        RH500Var[:] = RH500
        U300Var[:] = U300
        V300Var[:] = V300
        TC300Var[:] = TC300
        RH300Var[:] = RH300
        reflectivityVar[:] = reflectivity
        rainRateVar[:] = rainRate

        ncdstfile.close()
