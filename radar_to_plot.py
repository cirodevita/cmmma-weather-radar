
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from radar import Radar


def radar_to_plot(R,output_dir=''):

    t = np.array([np.arange(-np.pi, np.pi, 0.001)])

    lat0 = R._location[0]
    lon0 = R._location[1]

    # Circonferenza in coordinate polari
    rr = 1.283
    rr1 = 0.973
    y108NA = rr1 * np.sin(t) + lat0
    x108NA = rr  * np.cos(t) + lon0

    R.create_grid()
    data = R.calculate_vmi()

    Zmask2 =  np.ma.array(data, mask=np.isnan(data))
    Zmask  = np.transpose(Zmask2)

    m=Basemap(llcrnrlon=R.lonmin-0.2,llcrnrlat=R.latmin-0.2,urcrnrlon=R.lonmax+0.2,urcrnrlat=R.latmax+0.2,
    resolution='f',projection='tmerc',lon_0=lon0,lat_0=lat0)

    m.drawcoastlines()

    x,y=m(R.lon[:360],R.lat[:360])

    w,z=m(lon0,lat0)
    m.plot(w, z, 's', color='red', markersize=3)

    x108mpNA,y108mpNA=m(x108NA,y108NA)
    plt.plot(x108mpNA[0,:],y108mpNA[0,:],color='k')

    clevs=[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60]
    #clevs=[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]

    m.contourf(x,y,Zmask,clevs,cmap='jet')
    #m.contourf(x,y,Zmask,cmap='jet')
    #m.pcolormesh(x,y,Zmask,cmap='jet')
    #m.pcolor(x,y,Zmask[:,:],cmap='jet') 

    plt.savefig(os.path.join(output_dir,f'map-{R._id}.png'),transparent=False,bbox_inches='tight')


if __name__ == '__main__':

    output_dir = ''
    radar_id = 'NA'
    radar_location = (40.843812,14.238565)
    kmdeg = 111.0
    radar_dir = f'WR10X/{radar_id}/data'

    print("Reading data...")
    R = Radar(radar_id,radar_location,kmdeg,radar_dir)
    print(R)

    print("Saving data as plot...")
    radar_to_plot(R)
    print("OK")