import numpy as np
import netCDF4 as nc
from radar import Radar

def radar_to_netcdf4(R,output_dir=''):

        c_lat = R.lat
        c_lon = R.lon

        grid_dim = 480

        grid_lat = np.arange(R.latmin,R.latmax,(R.latmax-R.latmin)/grid_dim)
        grid_lon = np.arange(R.lonmin,R.lonmax,(R.lonmax-R.lonmin)/grid_dim)

        grid = np.full([grid_dim,grid_dim],-999)

        vmi = R.calculate_vmi()

        for i in range(len(vmi)):
            for j in range(len(vmi[0])):
                if(not np.isnan(vmi[i,j])):
                    best_lat = np.abs(grid_lat-c_lat[j,i]).argmin()
                    best_lon = np.abs(grid_lon-c_lon[j,i]).argmin()
                    grid[best_lat,best_lon] = np.round(vmi[i,j])
                
        grid_lat = np.array([grid_lat,]*grid_dim).transpose()
        grid_lon = np.array([grid_lon]*grid_dim)

        fn = f'{R._id}_{R._scan_datestamp}.nc'
        ds = nc.Dataset(fn, 'w', format='NETCDF4')

        ds.createDimension('eta_rho', grid_dim)
        ds.createDimension('xi_rho', grid_dim)

        lats = ds.createVariable('lat', 'f4', ('eta_rho','xi_rho'))
        lats.units = 'degree_north'
        lats._CoordinateAxisType = 'Lat'

        lons = ds.createVariable('lon', 'f4', ('eta_rho','xi_rho'))
        lons.units = 'degree_east'
        lons._CoordinateAxisType = 'Lon'

        reflectivity = ds.createVariable('reflectivity', 'i', ('eta_rho','xi_rho'),fill_value=-999)

        reflectivity[:] = grid
        lats[::] = grid_lat
        lons[::] = grid_lon

        ds.close()

if __name__ == '__main__':

    output_dir = ''
    radar_id = 'NA'
    radar_location = (40.843812,14.238565)
    kmdeg = 111.0
    radar_dir = f'WR10X/{radar_id}/data'

    print("Reading data...")
    R = Radar(radar_id,radar_location,kmdeg,radar_dir)
    print(R)

    print("Saving data as netcdf4...")
    radar_to_netcdf4(R)
    print("OK")