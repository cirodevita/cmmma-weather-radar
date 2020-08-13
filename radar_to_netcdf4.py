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

        lat0 = R._location[0]
        lon0 = R._location[1]


        offset_i = np.abs(grid_lon-lon0).argmin()
        offset_j = np.abs(grid_lat-lat0).argmin()

        for j in range(1,len(grid_lat)):
            for i in range(1,len(grid_lon)):
                x = i-offset_i
                y = j-offset_j
                r = np.sqrt(x**2+y**2)
                t = np.arctan2(y, x)
                t = t * 180 / np.pi


                if(grid_lat[j] > (R.latmax-R.latmin)/2 and grid_lon[i] < (R.lonmax-R.lonmin)/2):
                    t += 180

                elif(grid_lat[j] < (R.latmax-R.latmin)/2 and grid_lon[i] < (R.lonmax-R.lonmin)/2):
                    t += 180

                elif(grid_lat[j] < (R.latmax-R.latmin)/2 and grid_lon[i] > (R.lonmax-R.lonmin)/2):
                    t+=360

            
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

    radar_NA = 'WR10X/NA/radar_info.json'

    print("Reading data...")
    R = Radar(radar_NA)
    print(R)

    print("Saving data as netcdf4...")
    radar_to_netcdf4(R)
    print("OK")