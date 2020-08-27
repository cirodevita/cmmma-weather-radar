import os
import sys
sys.path.append(os.getcwd() + '/..')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from WR10X.Radar import Radar

def generate_plot(R,data,clevs=None,output_dir=''):
    t = np.array([np.arange(-np.pi, np.pi, 0.001)])

    lat0 = R._location[0]
    lon0 = R._location[1]
    # Circumference
    rr = 1.283
    rr1 = 0.973
    y108NA = rr1 * np.sin(t) + lat0
    x108NA = rr  * np.cos(t) + lon0
    # Plot dimensions
    my_dpi = 102.4
    plt.figure(1, figsize=(1024 / my_dpi, 1024 / my_dpi), dpi=my_dpi)
    # Data
    Zmask2 =  np.ma.array(data, mask=np.isnan(data))
    Zmask  = np.transpose(Zmask2)
    # Create Basemap
    m=Basemap(llcrnrlon=R.lonmin-0.2,llcrnrlat=R.latmin-0.2,urcrnrlon=R.lonmax+0.2,urcrnrlat=R.latmax+0.2,
    resolution='f',projection='tmerc',lon_0=lon0,lat_0=lat0)
    # Draw coast lines
    m.drawcoastlines()
    # Insert data
    x,y=m(R.lon[:360],R.lat[:360])
    w,z=m(lon0,lat0)
    m.plot(w, z, 's', color='red', markersize=3)
    x108mpNA,y108mpNA=m(x108NA,y108NA)
    plt.plot(x108mpNA[0,:],y108mpNA[0,:],color='k')
    if clevs is None:
        m.contourf(x,y,Zmask,cmap='jet')
    else:
        m.contourf(x,y,Zmask,clevs,cmap='jet')
    # Save map
    plt.savefig(os.path.join(output_dir,f'map-{R._id}.png'),transparent=False,bbox_inches='tight')

if __name__ == '__main__':

    radar_config_path = '../data/NA/radar_config.json'
    scan_data = 'A00-202006051030'

    #clevs = [0.2,0.4,0.6,0.8,1,1.2,1.4,1.6,1.8,2.0]
    clevs=[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60]
    #clevs=[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]
    
    print("Reading data...")
    R = Radar(radar_config_path,scan_data)
    print(R)
    print("Saving data as plot...")
    data = R.calculate_vmi()
    generate_plot(R,data,clevs)
    print("OK")