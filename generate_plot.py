import os
import numpy as np
import numpy.ma as ma

import matplotlib.pyplot as plt


from mpl_toolkits.basemap import Basemap

def plot_map(radar_name,lat0,lon0,data,path_output):
    
    ndata = 240
    radarLocation = np.array([lat0,lon0]) 
    
    t = np.array([np.arange(-np.pi, np.pi, 0.001)])

    # Circonferenza in coordinate polari
    rr = 1.283
    rr1 = 0.973
    y108NA = rr1 * np.sin(t) + lat0
    x108NA = rr * np.cos(t) + lon0

    # Raggio rispetto alla risoluzione del radar (450m)
    rkm = np.zeros(ndata)
    for j in range(ndata):
        rkm[j] = 108.0 *j/ndata

   
    z = np.zeros(360)
    for i in range(360):
        #z[i] = 3.14 * (1+((i-1)*1))/180
        z[i] = np.pi*i/180


    
    lat = np.zeros([360, ndata], float)
    lon = np.zeros([360, ndata], float)
    for j in range(ndata):
        for i in range(360):
            lat[i, j] = lat0 + np.cos(z[i]) * rkm[j] / 111.0
            lon[i, j] = lon0 + np.sin(z[i]) * (rkm[j] / 111.0) / np.cos(np.pi * lat[i, j] / 180.0)


    latmin = np.nanmin(lat)
    latmax = np.nanmax(lat)
    lonmin = np.nanmin(lon) - 0.02
    lonmax = np.nanmax(lon) + 0.02

    # -------------------------------------------------

    my_dpi = 102.4
    plt.figure(1, figsize=(650 / my_dpi, 650 / my_dpi), dpi=my_dpi)

    Zmask2 =  ma.array(data, mask=np.isnan(data))
    Zmask = np.transpose(Zmask2)

    m=Basemap(llcrnrlon=lonmin,llcrnrlat=latmin,urcrnrlon=lonmax,urcrnrlat=latmax,
    resolution='f',projection='tmerc',lon_0=lon0,lat_0=lat0)

    m.drawcoastlines()

    x,y=m(lon[:360],lat[:360])

    w,z=m(lon0,lat0)
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

    # NAPOLI    
    radar_name = 'NA'
    lat0 = 40.843812
    lon1 = 14.238565

    # AVELLINO
    #radar_name = 'AV'
    #lat0 = 41.052167
    #lon1 = 15.235667

    path_data= "WR10X"

    data = np.loadtxt(os.path.join(path_data,f'VMI_{radar_name}.out'))
    data =  np.reshape(data ,(240, 360), 'F')

    print("Plotting..",end='')
    plot_map(radar_name,lat0,lon1,data,path_data)
    print("OK")
