from radar import Radar

import os
import numpy as np
import numpy.ma as ma

import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap


def plot_map(lat0,lon0,data,path_output):

    ragg_radar = 'xx'
    ndata = 240
    radarLocation = np.array([lat0,lon0]) 
    t = np.array([np.arange(-np.pi, np.pi, 0.001)])

    rr = 1.283
    rr1 = 0.973
    y108NA = rr1 * np.sin(t) + radarLocation[0]
    x108NA = rr * np.cos(t) + radarLocation[1]

    rkm = np.zeros(ndata)
    for j in range(ndata):
        rkm[j] = 108.0 * (j - 1) / ndata

    z = np.zeros(360)
    for i in range(360):
        z[i] = 3.14 * (1 + ((i - 1) * 1)) / 180.0


    lat = np.zeros([360, ndata], float)
    lon = np.zeros([360, ndata], float)
    for j in range(ndata):
        for i in range(360):
            lat[i, j] = lat0 + np.cos(z[i]) * rkm[j] / 111.0
            lon[i, j] = lon0 + np.sin(z[i]) * (rkm[j] / 111.0) / np.cos(3.14 * lat[i, j] / 180.0)

    latmin = np.nanmin(lat)
    latmax = np.nanmax(lat)
    lonmin = np.nanmin(lon) - 0.02
    lonmax = np.nanmax(lon) + 0.02

    # -------------------------------------------------

    my_dpi = 102.4
    plt.figure(1, figsize=(1024 / my_dpi, 1024 / my_dpi), dpi=my_dpi)

    Zmask2 =  ma.array(data, mask=np.isnan(data))
    Zmask = np.transpose(Zmask2)

    m=Basemap(llcrnrlon=lonmin,llcrnrlat=latmin,urcrnrlon=lonmax,urcrnrlat=latmax,
    resolution='f',projection='tmerc',lon_0=lon0,lat_0=lat0)

    m.drawcoastlines()

    x,y=m(lon,lat)

    w,z=m(lon0,lat0)
    m.plot(w, z, 's', color='red', markersize=6)

    x108mpNA,y108mpNA=m(x108NA,y108NA)
    plt.plot(x108mpNA[0,:],y108mpNA[0,:],color='k')

    #clevs=[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60]
    #m.contourf(x,y,Zmask,clevs,cmap='jet')
    m.contourf(x,y,Zmask,cmap='jet')

    plt.savefig(os.path.join(path_output,'map.png'),transparent=False,bbox_inches='tight')


if __name__ == '__main__':

    # NAPOLI
    lat0 = 40.843812
    lon1 = 14.238565
    path = 'WR10X/radar/data/na'

    # AVELLINO
    #lat0 = 41.052167
    #lon1 = 15.235667
    #path = 'WR10X/radar/data/av'

    path_output = "WR10X/radar"
    R = Radar(lat0,lon1,path)

    print(R)
    data = R.calculate_rain_rate()
    print("Plotting..")
    plot_map(lat0,lon1,data,path_output)
    print("...OK!")
    


    
