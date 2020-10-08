import os,sys
sys.path.append(os.getcwd() + '/..')

import numpy as np
import netCDF4 as nc

from WR10X.Radar import Radar


def radar_to_netcdf4(R,output_dir=''):

        c_lat = R.lat
        c_lon = R.lon

        grid_dim = 480

        step_lat = (R.latmax-R.latmin)/grid_dim
        step_lon = (R.lonmax-R.lonmin)/grid_dim

        grid_lat = np.arange(R.latmin,R.latmax,step_lat)
        grid_lon = np.arange(R.lonmin,R.lonmax,step_lon)

        vmi = R.calculate_vmi()

        rainrate = R.calculate_rain_rate()

        grid_vmi = np.full([grid_dim,grid_dim],-99.0,dtype=np.float32)
        #grid_poh = np.full([grid_dim,grid_dim],-999,dtype=np.float32)
        grid_rr  = np.full([grid_dim,grid_dim],-99.0,dtype=np.float32)

        lat0 = R._location[0]
        lon0 = R._location[1]

        offset_j = 240
        offset_i = 240

        for j in range(1,len(grid_lat)):
            for i in range(1,len(grid_lon)):
                x = i-offset_i
                y = j-offset_j
                r = np.sqrt(x**2+y**2)
                t = np.arctan2(y, x)
                
                t = t * 180 / np.pi
     
                if np.isnan(t):
                    continue
            
                t = int(np.around(t, decimals=0))
                r = int(np.around(r, decimals=0))

                t -= 1

                if(r < 240):    
                    
                    if not np.isnan(vmi[r,t]):
                        grid_vmi[i,j] = np.round(vmi[r,t])

                    if not np.isnan(rainrate[r,t]):
                        grid_rr[i,j] = np.round(rainrate[r,t])
                    
                    '''
                    if not np.isnan(poh[r,t]):
                        grid_poh[i,j] = np.round(poh[r,t])
                    '''        

        grid_lat = np.array([grid_lat,]*grid_dim).transpose()
        grid_lon = np.array([grid_lon]*grid_dim)

        datestamp = str(R._scan_datestamp).replace(':','-')
        fn = f'{R._id}_{datestamp}.nc'
        ds = nc.Dataset(os.path.join(output_dir,fn), 'w', format='NETCDF4')

        ds.createDimension('X', grid_dim)
        ds.createDimension('Y', grid_dim)

        lats = ds.createVariable('lat', 'f4', ('X','Y'))
        lats.units = 'degree_north'
        lats._CoordinateAxisType = 'Lat'

        lons = ds.createVariable('lon', 'f4', ('X','Y'))
        lons.units = 'degree_east'
        lons._CoordinateAxisType = 'Lon'

        reflectivity = ds.createVariable('reflectivity', 'f4', ('X','Y'),fill_value=-99.0)
        rain_rate    = ds.createVariable('rain_rate','f4',('X','Y'),fill_value=-99.0)
        #poh          = ds.createVariable('poh','i',('X','Y'),fill_value=-999)

        reflectivity[:] = grid_vmi
        rain_rate[:] = grid_rr
        #poh[:] = grid_poh
        lats[::] = grid_lat
        lons[::] = grid_lon

        ds.close()

if __name__ == '__main__':
    output_dir = 'TEST'
    radar_config_path = '../data/NA/radar_config.json'
    scan_data = '../data/NA/data/'

    # Da linea di comando
    if radar_config_path == '' or scan_data == '':
        if len(sys.argv) < 3:
            print(f'usage: {sys.argv[0]} <radar config file> <scan data directory> [<output map directory>] ')
            exit(-1)

        radar_config_path = sys.argv[1]
        scan_data = sys.argv[2]

        if len(sys.argv) >= 4:
            output_dir = sys.argv[3]

    days = os.listdir(scan_data)
    for d in days:
        scans = os.listdir(os.path.join(scan_data,d))

        if not os.path.exists(os.path.join(output_dir,d)):
            os.mkdir(os.path.join(output_dir,d))

        for s in scans:
            s_data = os.path.join(d,s)
            print(s_data)
            print("Reading data...")

            try:
                R = Radar(radar_config_path,s_data)
                print("Saving data as netcdf4...")
                radar_to_netcdf4(R,os.path.join(output_dir,d))
                print("OK")
            except:
                print('INVALID SCAN')