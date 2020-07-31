from radar import Radar
import numpy as np
import os



import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


import sys
np.set_printoptions(threshold=sys.maxsize)

def generate_plot(radar):

    t = np.array([np.arange(-np.pi, np.pi, 0.001)])

    # Circonferenza in coordinate polari
    rr = 1.283
    rr1 = 0.973
    y108NA = rr1 * np.sin(t) + radar.lat0
    x108NA = rr  * np.cos(t) + radar.lon0

    radar.create_grid()
    data = radar.calculate_vmi()


    my_dpi = 102.4
    plt.figure(1, figsize=(650 / my_dpi, 650 / my_dpi), dpi=my_dpi)

    Zmask2 =  np.ma.array(data, mask=np.isnan(data))
    Zmask  = np.transpose(Zmask2)

    m=Basemap(llcrnrlon=radar.lonmin,llcrnrlat=radar.latmin,urcrnrlon=radar.lonmax,urcrnrlat=radar.latmax,
    resolution='f',projection='tmerc',lon_0=radar.lon0,lat_0=radar.lat0)

    m.drawcoastlines()

    x,y=m(radar.lon[:360],radar.lat[:360])

    w,z=m(radar.lon0,radar.lat0)
    m.plot(w, z, 's', color='red', markersize=6)

    x108mpNA,y108mpNA=m(x108NA,y108NA)
    plt.plot(x108mpNA[0,:],y108mpNA[0,:],color='k')

    clevs=[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60]
    #clevs=[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]
    m.contourf(x,y,Zmask,clevs,cmap='jet')
    #m.contourf(x,y,Zmask,cmap='jet')
    #m.pcolormesh(x,y,Zmask,cmap='jet')
    #m.pcolor(x,y,Zmask[:,:],cmap='jet') 
    plt.savefig(os.path.join(path_output,f'map-{radar_name}.png'),transparent=False,bbox_inches='tight')
    #np.savetxt(f'WR10X/radar/lat-{radar_name}.out', lat)
    #np.savetxt(f'WR10X/radar/lon-{radar_name}.out', lon)


if __name__ == '__main__':

    kmdeg = 111.0

    # NAPOLI    
    radar_name = 'NA'
    lat0 = 40.843812
    lon1 = 14.238565

    # AVELLINO
    #radar_name = 'AV'
    #lat0 = 41.052167
    #lon1 = 15.235667

    radar_dir = f'WR10X/{radar_name}/'
    path_data = "WR10X"
    path_output = "WR10X"

    print("Reading data...")
    R = Radar(lat0,lon1,kmdeg,radar_dir,radar_name)
    print(R)

    print("Creating netcdf4 file...")
    R.save_as_netcd4()
    print("OK")


    print("Create plot image...")
    generate_plot(R)
    print("OK")
   