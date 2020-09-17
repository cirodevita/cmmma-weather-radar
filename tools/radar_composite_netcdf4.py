import os,sys
sys.path.append(os.getcwd() + '/..')

import numpy as np
import netCDF4 as nc

from WR10X.Radar import Radar

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

    grid_vmi = np.full([lat_dim,lon_dim],-999,dtype=np.float32)
    #grid_poh = np.full([lat_dim,lon_dim],-999)
    grid_rr  = np.full([lat_dim,lon_dim],-999,dtype=np.float32)

    for R in radars:

        vmi = R.calculate_vmi()
        #poh = R.calculate_poh()
        rainrate = R.calculate_rain_rate()
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

                    if np.isnan(t) or np.isnan(r):
                        continue
                
                    r = int(r)
                    t = int(t)
                
                    if(r < R._ndata): 
                        if not np.isnan(rainrate[r,t]) and grid_rr[i,j] < rainrate[r,t]:
                            grid_rr[i,j] = rainrate[r,t]
                        if not np.isnan(vmi[r,t]) and grid_vmi[i,j] < vmi[r,t]:
                            grid_vmi[i,j] = vmi[r,t]
                        '''if not np.isnan(poh[r,t]) and grid_poh[i,j] < poh[r,t]:
                            grid_poh[i,j] = poh[r,t]'''

                
    grid_lat = np.array([grid_lat]*lon_dim).transpose()
    grid_lon = np.array([grid_lon]*lat_dim)

    fn = ''
    for R in radars:
        fn += R._id+'_'

    fn += str(R._scan_datestamp).replace(':','-')+'.nc'

    ds = nc.Dataset(os.path.join(output_dir,fn), 'w', format='NETCDF4')

    ds.createDimension('X' ,lat_dim)
    ds.createDimension('Y', lon_dim)

    lats = ds.createVariable('lat', 'f4', ('X','Y'))
    lats.units = 'degree_north'
    lats._CoordinateAxisType = 'Lat'

    lons = ds.createVariable('lon', 'f4', ('X','Y'))
    lons.units = 'degree_east'
    lons._CoordinateAxisType = 'Lon'

   
    reflectivity = ds.createVariable('reflectivity', 'f4', ('X','Y'),fill_value=-999)
    rain_rate    = ds.createVariable('rain_rate','f4',('X','Y'),fill_value=-999)
    #poh          = ds.createVariable('poh','i',('X','Y'),fill_value=-999)


    reflectivity[:] = grid_vmi
    rain_rate[:] = grid_rr
    #poh[:] = grid_poh
    lats[::] = grid_lat
    lons[::] = grid_lon

    ds.close()


def bulk_compose():

    radar_na_config = '../data/NA/radar_config.json'
    radar_av_config = '../data/AV/radar_config.json'

    day = '01'

    av_data = '../data/AV/data/'
    na_data = '../data/NA/data/'
    
    scans_av = os.listdir(os.path.join(av_data,day))
    scans_na = os.listdir(os.path.join(na_data,day))
    
    #scans = os.listdir(na_data)
    scans = [s for s in scans_av if s in scans_na]

    if not os.path.exists('COMPOSED'):
        os.mkdir('COMPOSED')

    if not os.path.exists(os.path.join('COMPOSED',day)):
        os.mkdir(os.path.join('COMPOSED',day))


    for scan in scans:
        try:
            print(f'Composing for {scan}...',end='')

            radars = []
            scan = os.path.join(day,scan);
            radars.append(Radar(radar_na_config,scan))
            radars.append(Radar(radar_av_config,scan))
            
            compose(radars,os.path.join('COMPOSED',day))

            print('OK')
        except NameError as err:
            print(err) 




if __name__ == '__main__':

    # Composing for a single Scan
    '''
    radar_na_config = '../data/NA/radar_config.json'
    radar_av_config = '../data/AV/radar_config.json'

   
    scan_data = 'A00-202006051030'

    radars = []
    radars.append(Radar(radar_na_config,scan_data))
    radars.append(Radar(radar_av_config,scan_data))

    print(f'Composing {scan_data} radar scan..')
    compose(radars)
    print('OK')
    '''
    # Bulk compose
    bulk_compose()


