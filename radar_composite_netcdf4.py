import numpy as np
import netCDF4 as nc
import sys

from radar import Radar

np.set_printoptions(threshold=sys.maxsize)

def compose(radars,output_dir=''):

    radar_area_lat = []
    radar_area_lon = []
    for r in radars:
        radar_area_lat.append(r.latmin)
        radar_area_lat.append(r.latmax)
        radar_area_lon.append(r.lonmin)
        radar_area_lon.append(r.lonmax)
    latmin = np.min(radar_area_lat)
    latmax = np.max(radar_area_lat)
    lonmin = np.min(radar_area_lon)
    lonmax = np.max(radar_area_lon)

    lat_dim = 600
    lon_dim = 750
    grid_lat = np.arange(latmin,latmax,(latmax-latmin)/lat_dim)
    grid_lon = np.arange(lonmin,lonmax,(lonmax-lonmin)/lon_dim)

    grid = np.full([lat_dim,lon_dim],-999)

    for R in radars:

        vmi = R.calculate_vmi()
        lat0 = R._location[0]
        lon0 = R._location[1]

        offset_j = np.abs(grid_lon-lon0).argmin()
        offset_i = np.abs(grid_lat-lat0).argmin()

        for j in range(1,lon_dim):
            for i in range(1,lat_dim):
                x = i-offset_i
                y = j-offset_j
                r = np.sqrt(x**2+y**2)
                t = np.arctan2(y, x)
                t = t * 180 / np.pi

                if np.isnan(t):
                    continue
            
                r = int(r)
                t = int(t)
               
                if(r < R._ndata): 
                    if not np.isnan(vmi[r,t]) and grid[i,j] < np.round(vmi[r,t]):
                        grid[i,j] = np.round(vmi[r,t])
                        
                    
    grid_lat = np.array([grid_lat]*lon_dim).transpose()
    grid_lon = np.array([grid_lon]*lat_dim)

    fn = ''
    for R in radars:
        fn += R._id+'_'

    fn += str(R._scan_datestamp).replace(':','-')+'.nc'

    ds = nc.Dataset(fn, 'w', format='NETCDF4')

    ds.createDimension('X' ,lat_dim)
    ds.createDimension('Y', lon_dim)

    lats = ds.createVariable('lat', 'f4', ('X','Y'))
    lats.units = 'degree_north'
    lats._CoordinateAxisType = 'Lat'

    lons = ds.createVariable('lon', 'f4', ('X','Y'))
    lons.units = 'degree_east'
    lons._CoordinateAxisType = 'Lon'

    reflectivity = ds.createVariable('reflectivity', 'i', ('X','Y'),fill_value=-999)

    reflectivity[::] = grid
    lats[::] = grid_lat
    lons[::] = grid_lon

    ds.close()



if __name__ == '__main__':

    radar_NA = 'WR10X/NA/radar_info.json'
    radar_AV = 'WR10X/AV/radar_info.json'

    scan_name = 'A00-202006051030'

    radars = []
    radars.append(Radar(radar_NA,scan_name))
    radars.append(Radar(radar_AV,scan_name))

    compose(radars)
    

    

   
