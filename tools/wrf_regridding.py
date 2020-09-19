import netCDF4 as nc
import numpy as np
import os


def build_url(yyyy,mm,dd,hh):
    return f'http://193.205.230.6:8080/opendap/opendap/wrf5/d03/archive/{yyyy}/{mm}/{dd}/wrf5_d03_{yyyy}{mm}{dd}Z{hh}00.nc'


def read_netcdf4_files(wrf,scan):
    try:
        model = nc.Dataset(wrf)
        radar_scan = nc.Dataset(scan,'r')
    except OSError:
        print("File non trovato")
        return None,None
    return model,radar_scan


def regridding(model,radar_scan,output):
    scan_lat = radar_scan['lat'][:,0]
    scan_lon = radar_scan['lon'][0]

    model_lat = model['latitude'][:]
    model_lon = model['longitude'][:]

    CLDFRA_TOTAL_VALUES = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    DAILY_RAIN_VALUES   = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    DELTA_RAIN_VALUES   = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    DELTA_WDIR10_VALUES = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    DELTA_WSPD10_VALUES = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    GPH500_VALUES       = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    GPH850_VALUES       = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    HOURLY_SWE_VALUES   = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    MCAPE_VALUES        = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    RH2_VALUES          = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    RH300_VALUES        = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    RH500_VALUES        = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    RH700_VALUES        = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    RH850_VALUES        = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    RH950_VALUES        = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    SLP_VALUES          = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    T2C_VALUES          = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    TC500_VALUES        = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    TC850_VALUES        = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    U10M_VALUES         = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    U300_VALUES         = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    U500_VALUES         = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    U700_VALUES         = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    U850_VALUES         = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    U950_VALUES         = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    WDIR10_VALUES       = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)
    WSPD10_VALUES       = np.full([len(scan_lat),len(scan_lon)],-999,dtype=np.float32)

    MODEL_CLDFRA_TOTAL = model['CLDFRA_TOTAL'][::]
    MODEL_DAILY_RAIN = model['DAILY_RAIN'][::]
    MODEL_DELTA_RAIN = model['DELTA_RAIN'][::]
    MODEL_DELTA_WDIR10 = model['DELTA_WDIR10'][::]
    MODEL_DELTA_WSPD10 = model['DELTA_WSPD10'][::]
    MODEL_GPH500 = model['GPH500'][::]
    MODEL_GPH850 = model['GPH850'][::]
    MODEL_HOURLY_SWE = model['HOURLY_SWE'][::]
    MODEL_MCAPE =model['MCAPE'][::]
    MODEL_RH2 = model['RH2'][::]
    MODEL_RH300 = model['RH300'][::]
    MODEL_RH500 = model['RH500'][::]
    MODEL_RH700 = model['RH700'][::]
    MODEL_RH850 = model['RH850'][::]
    MODEL_RH950 = model['RH950'][::]
    MODEL_SLP = model['SLP'][::]
    MODEL_T2C = model['T2C'][::]
    MODEL_TC500 = model['TC500'][::]
    MODEL_TC850 = model['TC850'][::]
    MODEL_U10M = model['U10M'][::]
    MODEL_U300 = model['U300'][::]
    MODEL_U500 = model['U500'][::]
    MODEL_U700 = model['U700'][::]
    MODEL_U850 = model['U850'][::]
    MODEL_U950 = model['U950'][::]
    MODEL_WDIR10 = model['WDIR10'][::]
    MODEL_WSPD10 = model['WSPD10'][::]

    for i in range(len(scan_lat)):
        for j in range(len(scan_lon)):

            _lat = scan_lat[i]
            _lon = scan_lon[j]


            if _lat > model_lat[len(model_lat)-1] or _lat < model_lat[0]:
                continue
            
            if _lon < model_lon[0] or _lon > model_lon[len(model_lon)-1]:
                continue
            
            if radar_scan['reflectivity'][i,j] == -999 :
                continue

            opt_i = (np.abs(model_lat-_lat)).argmin()
            opt_j = (np.abs(model_lon-_lon)).argmin()

            CLDFRA_TOTAL_VALUES[i,j] = MODEL_CLDFRA_TOTAL[0,opt_i,opt_j]
            DAILY_RAIN_VALUES[i,j] = MODEL_DAILY_RAIN[0,opt_i,opt_j]
            DELTA_RAIN_VALUES[i,j] = MODEL_DELTA_RAIN[0,opt_i,opt_j]
            DELTA_WDIR10_VALUES[i,j] = MODEL_DELTA_WDIR10[0,opt_i,opt_j]
            DELTA_WSPD10_VALUES[i,j] = MODEL_DELTA_WSPD10[0,opt_i,opt_j]
            GPH500_VALUES[i,j] = MODEL_GPH500[0,opt_i,opt_j]
            GPH850_VALUES[i,j] = MODEL_GPH850[0,opt_i,opt_j]
            HOURLY_SWE_VALUES[i,j] = MODEL_HOURLY_SWE[0,opt_i,opt_j]
            MCAPE_VALUES[i,j] = MODEL_MCAPE[0,opt_i,opt_j]
            RH2_VALUES[i,j] = MODEL_RH2[0,opt_i,opt_j]
            RH300_VALUES[i,j] = MODEL_RH300[0,opt_i,opt_j]
            RH500_VALUES[i,j] = MODEL_RH500[0,opt_i,opt_j]
            RH700_VALUES[i,j] = MODEL_RH700[0,opt_i,opt_j]
            RH850_VALUES[i,j] = MODEL_RH850[0,opt_i,opt_j]
            RH950_VALUES[i,j] = MODEL_RH950[0,opt_i,opt_j]
            SLP_VALUES[i,j] = MODEL_SLP[0,opt_i,opt_j]
            T2C_VALUES[i,j] = MODEL_T2C[0,opt_i,opt_j]
            TC500_VALUES[i,j] = MODEL_TC500[0,opt_i,opt_j]
            TC850_VALUES[i,j] = MODEL_TC850[0,opt_i,opt_j]
            U10M_VALUES[i,j] = MODEL_U10M[0,opt_i,opt_j]
            U300_VALUES[i,j] = MODEL_U300[0,opt_i,opt_j]
            U500_VALUES[i,j] = MODEL_U500[0,opt_i,opt_j]
            U700_VALUES[i,j] = MODEL_U700[0,opt_i,opt_j]
            U850_VALUES[i,j] = MODEL_U850[0,opt_i,opt_j]
            U950_VALUES[i,j] = MODEL_U950[0,opt_i,opt_j]
            WDIR10_VALUES[i,j] = MODEL_WDIR10[0,opt_i,opt_j]
            WSPD10_VALUES[i,j] = MODEL_WSPD10[0,opt_i,opt_j]

    aggregated_file = nc.Dataset(output, 'w', format='NETCDF4')
    aggregated_file.createDimension('X' ,len(scan_lat))
    aggregated_file.createDimension('Y', len(scan_lon))

    lats = aggregated_file.createVariable('lat', 'f4', ('X','Y'))
    lats.units = 'degree_north'
    lats._CoordinateAxisType = 'Lat'

    lons = aggregated_file.createVariable('lon', 'f4', ('X','Y'))
    lons.units = 'degree_east'
    lons._CoordinateAxisType = 'Lon'

    CLDFRA_TOTAL = aggregated_file.createVariable('HGT', 'f4', ('X','Y'),fill_value=-999)
    DAILY_RAIN = aggregated_file.createVariable('DAILY_RAIN', 'f4', ('X','Y'),fill_value=-999)
    DELTA_RAIN = aggregated_file.createVariable('DELTA_RAIN', 'f4', ('X','Y'),fill_value=-999)
    DELTA_WDIR10 = aggregated_file.createVariable('DELTA_WDIR10', 'f4', ('X','Y'),fill_value=-999)
    DELTA_WSPD10 = aggregated_file.createVariable('DELTA_WSPD10', 'f4', ('X','Y'),fill_value=-999)
    GPH500 = aggregated_file.createVariable('GPH500', 'f4', ('X','Y'),fill_value=-999)
    GPH850 = aggregated_file.createVariable('GPH850', 'f4', ('X','Y'),fill_value=-999)
    HOURLY_SWE = aggregated_file.createVariable('HOURLY_SWE', 'f4', ('X','Y'),fill_value=-999)
    MCAPE = aggregated_file.createVariable('MCAPE', 'f4', ('X','Y'),fill_value=-999)
    RH2 = aggregated_file.createVariable('RH2', 'f4', ('X','Y'),fill_value=-999)
    RH300 = aggregated_file.createVariable('RH300', 'f4', ('X','Y'),fill_value=-999)
    RH500 = aggregated_file.createVariable('RH500', 'f4', ('X','Y'),fill_value=-999)
    RH700 = aggregated_file.createVariable('RH700', 'f4', ('X','Y'),fill_value=-999)
    RH850 = aggregated_file.createVariable('RH850', 'f4', ('X','Y'),fill_value=-999)
    RH950 = aggregated_file.createVariable('RH950', 'f4', ('X','Y'),fill_value=-999)
    SLP = aggregated_file.createVariable('SLP', 'f4', ('X','Y'),fill_value=-999)
    T2C = aggregated_file.createVariable('T2C', 'f4', ('X','Y'),fill_value=-999)
    TC500 = aggregated_file.createVariable('TC500', 'f4', ('X','Y'),fill_value=-999)
    TC850 = aggregated_file.createVariable('TC850', 'f4', ('X','Y'),fill_value=-999)
    U10M = aggregated_file.createVariable('U10M', 'f4', ('X','Y'),fill_value=-999)
    U300 = aggregated_file.createVariable('U300', 'f4', ('X','Y'),fill_value=-999)
    U500 = aggregated_file.createVariable('U500', 'f4', ('X','Y'),fill_value=-999)
    U700 = aggregated_file.createVariable('U700', 'f4', ('X','Y'),fill_value=-999)
    U850 = aggregated_file.createVariable('U850', 'f4', ('X','Y'),fill_value=-999)
    U950 = aggregated_file.createVariable('U950', 'f4', ('X','Y'),fill_value=-999)
    WDIR10 = aggregated_file.createVariable('WDIR10', 'f4', ('X','Y'),fill_value=-999)
    WSPD10 = aggregated_file.createVariable('WSPD10', 'f4', ('X','Y'),fill_value=-999)
    RADAR_REFLECTIVITY = aggregated_file.createVariable('RADAR_REFLECTIVITY', 'f4', ('X','Y'),fill_value=-999)
    RADAR_RAIN_RATE = aggregated_file.createVariable('RADAR_RAIN_RATE', 'f4', ('X','Y'),fill_value=-999)

    lats[::] = radar_scan['lat'][::]
    lons[::] = radar_scan['lon'][::]

    CLDFRA_TOTAL[::] = CLDFRA_TOTAL_VALUES
    DAILY_RAIN[::] = DAILY_RAIN_VALUES
    DELTA_RAIN[::] = DELTA_RAIN_VALUES
    DELTA_WDIR10[::] = DELTA_WDIR10_VALUES
    DELTA_WSPD10[::] = DELTA_WSPD10_VALUES
    GPH500[::] = GPH500_VALUES
    GPH850[::] = GPH850_VALUES
    HOURLY_SWE[::] = HOURLY_SWE_VALUES
    MCAPE[::] = MCAPE_VALUES
    RH2[::] = RH2_VALUES
    RH300[::] = RH300_VALUES
    RH500[::] = RH500_VALUES
    RH700[::] = RH700_VALUES
    RH850[::] = RH850_VALUES
    RH950[::] = RH950_VALUES
    T2C[::] = T2C_VALUES
    TC500[::] = TC500_VALUES
    TC850[::] = TC850_VALUES
    U10M[::] = U10M_VALUES
    U300[::] = U300_VALUES
    U500[::] = U500_VALUES
    U700[::] = U700_VALUES
    U850[::] = U850_VALUES
    U950[::] = U950_VALUES
    WDIR10[::] = WDIR10_VALUES
    WSPD10[::] = WSPD10_VALUES

    RADAR_REFLECTIVITY[::] = radar_scan['reflectivity'][::]
    RADAR_RAIN_RATE[::] = radar_scan['rain_rate'][::]

if __name__ == '__main__':

    input_dir = 'STACKED'
    output_dir = 'NETCDF4_DATASET'

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    days = os.listdir(input_dir)

    test_wrf = 'http://193.205.230.6:8080/opendap/opendap/wrf5/d03/archive/2020/06/01/wrf5_d03_20200601Z0000.nc'
    test_scan = 'STACKED/01/NA_AV_2020-06-01 00.nc'
    scan = 'NA_AV_2020-06-01 00.nc'

    model,radar_scan = read_netcdf4_files(test_wrf,test_scan)
    regridding(model,radar_scan,os.path.join(output_dir,scan))

        
    '''
    for dd in days:
       scans = os.listdir(os.path.join(input_dir,dd))
       if scans:
            yyyy = scans[0][6:10]
            mm = scans[0][11:13]
            for scan in scans:
                hh = scan[17:19]
                wrf_url_nc = build_url(yyyy,mm,dd,hh)
                scan_path = os.path.join(input_dir,dd,scan)
    '''       






