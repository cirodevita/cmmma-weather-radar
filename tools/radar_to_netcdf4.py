import os,sys
sys.path.append(os.getcwd() + '/..')

import numpy as np
import netCDF4 as nc

from WR10X.Radar import Radar


def radar_to_netcdf4(R,output_dir=''):

        c_lat = R.lat
        c_lon = R.lon

        grid_dim = 480

        grid_lat = np.arange(R.latmin,R.latmax,(R.latmax-R.latmin)/grid_dim)
        grid_lon = np.arange(R.lonmin,R.lonmax,(R.lonmax-R.lonmin)/grid_dim)

        grid = np.full([grid_dim,grid_dim],-999)

        vmi = R.calculate_vmi()

        lat0 = R._location[0]
        lon0 = R._location[1]


        offset_j = np.abs(grid_lon-lon0).argmin()
        offset_i = np.abs(grid_lat-lat0).argmin()

        for j in range(1,len(grid_lat)):
            for i in range(1,len(grid_lon)):
                x = i-offset_i
                y = j-offset_j
                r = np.sqrt(x**2+y**2)
                t = np.arctan2(y, x)
                t = t * 180 / np.pi
     
                if np.isnan(t):
                    continue
            
                r = int(r)
                t = int(t)

                if(r < 240):      
                    if np.isnan(vmi[r,t]):
                        grid[i,j] = -999
                    else: 
                        grid[i,j] = np.round(vmi[r,t])
                    

        grid_lat = np.array([grid_lat,]*grid_dim).transpose()
        grid_lon = np.array([grid_lon]*grid_dim)


        datestamp = str(R._scan_datestamp).replace(':','-')
        fn = f'{R._id}_{datestamp}.nc'
        ds = nc.Dataset(fn, 'w', format='NETCDF4')

        ds.createDimension('X', grid_dim)
        ds.createDimension('Y', grid_dim)

        lats = ds.createVariable('lat', 'f4', ('X','Y'))
        lats.units = 'degree_north'
        lats._CoordinateAxisType = 'Lat'

        lons = ds.createVariable('lon', 'f4', ('X','Y'))
        lons.units = 'degree_east'
        lons._CoordinateAxisType = 'Lon'

        reflectivity = ds.createVariable('reflectivity', 'i', ('X','Y'),fill_value=-999)

        reflectivity[:] = grid
        lats[::] = grid_lat
        lons[::] = grid_lon

        ds.close()


if __name__ == '__main__':

    radar_config_path = '../data/NA/radar_config.json'
    scan_data = 'A00-202006051030'

    print("Reading data...")
    R = Radar(radar_config_path,scan_data)
    print(R)

    print("Saving data as netcdf4...")
    radar_to_netcdf4(R)
    print("OK")