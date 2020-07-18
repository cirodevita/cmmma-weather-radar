import numpy as np
import numpy.ma as ma

import matplotlib.pyplot as plt
from os import listdir
from os import path
import sys
from mpl_toolkits.basemap import Basemap

from StatisticalFilter import StatisticalFilter
import scan_data


import warnings
warnings.filterwarnings("ignore")
np.set_printoptions(threshold=sys.maxsize)


def apply_statistical_filter(radar_data):
    # Converto il dizionario in una lista

    data_mappe = []
    for radar_elevation in radar_data:
        data_mappe.append(radar_data[radar_elevation])

    Mappe = np.array(data_mappe)
    Etn_Th = 0.0005
    Txt_Th = 14.0
    Z_Th = 0


    d_filt1 = StatisticalFilter(Mappe, Etn_Th, Txt_Th, Z_Th)

    # Scompongo in dati filtrati
    index = 0
    for radar_elevation in radar_data:
        radar_data[radar_elevation] = d_filt1[index,:,:]

    return radar_data

def apply_sea_clutter(radar_data):

    rd = np.empty([240, 360])
    for i in range(240):
        for j in range(360):
            rd[i, j] = radar_data['01'][i, j] - radar_data['02'][i, j]
    rd[rd == 0] = np.nan

    for j in range(126, 252):
        T1 = 50.0
        T2 = 0.0
        for i in range(70):
            if rd[i, j] > T1:
                radar_data['01'][i, j] = radar_data['02'][i, j]
            elif rd[i, j] > 0.0 and radar_data['02'][i, j] < T2:
                radar_data['01'][i, j] = radar_data['02'][i, j]

    
    return  radar_data

def bean_blocking(radar_data):
    # Lettura file M

    m1 = np.loadtxt('WR10X/radar/mc1_na.txt')
    m2 = np.loadtxt('WR10X/radar/mc2_na.txt')
    m3 = np.loadtxt('WR10X/radar/mc3_na.txt')

    MC = np.array([m1, m2, m3])

    MNC = np.array([radar_data['01'], radar_data['02'], radar_data['03']])

    for k in range(3):
        for i in range(240):
            for j in range(360):
                if MNC[k, i, j] <= 0:
                    MNC[k, i, j] = np.nan

    Z_cbb = np.empty([3, 240, 360])

    for k in range(3):
        for i in range(240):
            for j in range(360):
                Z_cbb[k, i, j] = MNC[k, i, j] + MC[k, i, j]

    Z_cbb1 = Z_cbb[0, :, :]
    Z_cbb2 = Z_cbb[1, :, :]
    Z_cbb3 = Z_cbb[2, :, :]

    radar_data['01'] = Z_cbb1
    radar_data['02'] = Z_cbb2
    radar_data['03'] = Z_cbb3


    return radar_data

def attenuazione(radar_data):
    for radar_elevation in radar_data:
        radar_data[radar_elevation][(radar_data[radar_elevation]>60)] = 60

    for radar_elevation in radar_data:
        radar_data[radar_elevation] == 10 ** (radar_data[radar_elevation] / 10)

    a = 0.000372
    b = 0.72

    A = {}
    for radar_elevation in radar_data:
        A[radar_elevation] = np.zeros([240, 360])
    
    for i in range(240):
        for j in range(1, 360):
            A[radar_elevation][i,j] =  abs(0.6 * a * (radar_data[radar_elevation][i, j] ** b))

    A[radar_elevation][np.isnan(A[radar_elevation])] = 0.0


    PI = {}
    for radar_elevation in radar_data:
        PI[radar_elevation] = np.zeros([240, 360])
        for i in range(240):
            for j in range(1, 360):
                PI[radar_elevation][i, j] = A[radar_elevation][i, j] + PI[radar_elevation][i, j - 1]

        PI[radar_elevation][(PI[radar_elevation] > 10)] = 10



    Z_filt = {}
    for radar_elevation in radar_data:
        Z_filt[radar_elevation] = np.zeros([240, 360])
        for i in range(240):
            for j in range(1, 360):
                Z_filt[radar_elevation][i, j] = radar_data[radar_elevation][i, j] * 10.0 ** ((PI[radar_elevation][i, j - 1] + A[radar_elevation][i, j]) / 10.0)
        # FIXME : Warning - RuntimeWarning: divide by zero encountered in log10
        Z_filt[radar_elevation] = 10 * np.log10(Z_filt[radar_elevation])

        z_th = 4
        Z_filt[radar_elevation][(Z_filt[radar_elevation] < z_th)] = np.nan
        Z_filt[radar_elevation][:, 359] = Z_filt[radar_elevation][:, 0]


    return Z_filt

def calcola_vmi (radar_data) :

    dbz_max = np.empty([240, 360])
    #Dict to list
    # Calcolo VMI
    for i in range(240):
        for j in range(360):
            # FIXME : Warning - RuntimeWarning: All-NaN axis encountered
            dbz_max[i, j] = np.nanmax(
                [
                    radar_data['01'][i, j], radar_data['02'][i, j],radar_data['03'][i, j], radar_data['04'][i, j], radar_data['05'][i, j],
                    radar_data['07'][i, j], radar_data['10'][i, j],radar_data['12'][i, j], radar_data['15'][i, j], radar_data['20'][i, j]
                ])
            if dbz_max[i, j] <= 0.0: 
                dbz_max[i, j] = np.nan


    '''
    rain_rate = np.empty([240, 360])
    for i in range(240):
        for j in range(360):
            rain_rate[i, j] = ((10 ** (dbz_max[i, j] / 10.0)) / 128.3) ** (1 / 1.67)

    Zfilt = np.empty([240, 360])
    Zfilt[:, :] = rain_rate
    rain_rate = np.copy(Zfilt)

    rain_rate = np.empty([240, 360])
    for i in range(240):
        for j in range(360):
            rain_rate[i, j] = (200*dbz_max[i, j]**(1.6))
    '''
    return dbz_max

def generate_map_plot(rain_rate):

    # ---------------------------------------------------------------------------------------------------------
    ndata = 240
    t = np.array([np.arange(-np.pi, np.pi, 0.001)])

    # Coordinate radar NAPOLI
    radar_lat = 40.843812
    radar_lon = 14.238565

    centerNA = np.array([radar_lat, radar_lon]) 
    rr = 1.283
    rr1 = 0.973
    y108NA = rr1 * np.sin(t) + centerNA[0]
    x108NA = rr * np.cos(t) + centerNA[1]

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
            lat[i, j] = radar_lat + np.cos(z[i]) * rkm[j] / 111.0
            lon[i, j] = radar_lon + np.sin(z[i]) * (rkm[j] / 111.0) / np.cos(3.14 * lat[i, j] / 180.0)

    latmin = np.nanmin(lat)
    latmax = np.nanmax(lat)
    lonmin = np.nanmin(lon) - 0.02
    lonmax = np.nanmax(lon) + 0.02

    # ---------------------------------------------------------------------------------------------------------

    my_dpi = 102.4
    plt.figure(1, figsize=(1024 / my_dpi, 1024 / my_dpi), dpi=my_dpi)


    Zmask2 =  ma.array(rain_rate, mask=np.isnan(rain_rate))
    Zmask = np.transpose(Zmask2)


    Zmask = np.transpose(rain_rate)

    m=Basemap(llcrnrlon=lonmin,llcrnrlat=latmin,urcrnrlon=lonmax,urcrnrlat=latmax,
    resolution='f',projection='tmerc',lon_0=radar_lon,lat_0=radar_lat)

    m.drawcoastlines()

    x,y=m(lon,lat)

    w,z=m(radar_lon,radar_lat)
    m.plot(w, z, 's', color='red', markersize=6)

    x108mpNA,y108mpNA=m(x108NA,y108NA)
    plt.plot(x108mpNA[0,:],y108mpNA[0,:],color='k')

    clevs=[0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60]
    m.contourf(x,y,Zmask,clevs,cmap='jet')
    #Z=m.pcolor(x,y,Zmask[:,:],cmap='jet') 
    #m.contourf(x,y,Zmask,cmap='jet')

    np.savetxt(path.join(path_output,'VMI_NA.out'), Zmask)
    plt.savefig(path.join(path_output,'image_alb.png'),transparent=False,bbox_inches='tight')



if __name__ == '__main__':
    
    path_data   = 'WR10X/radar/data/na/'  # Path dati
    path_output = "WR10X/radar/"          # Path di output

    radar_data = scan_data.get_radar_data(path_data)

    # ---------------------------------------------------------------------------------------------------------
    '''
    # soglie di riflettività sulle matrici raw (threshold)
    th_reflett = 55
    for radar_elevation in radar_data:
        radar_data[radar_elevation][(radar_data[radar_elevation] > th_reflett)] = th_reflett
        radar_data[radar_elevation][(radar_data[radar_elevation] < 4)] = np.nan

    '''
    # Copio Matrici ---------------------------------------------------------

    '''
    radar_data_raw = {}
    for radar_elevation in radar_data:
        radar_data_raw[radar_elevation] = np.copy(radar_data[radar_elevation])

    radar_data = apply_statistical_filter(radar_data)
    
    radar_data = apply_sea_clutter(radar_data)

 
    # Riassegno i valori nelle aree non affette da clutter
    for i in range(99, 240):
        for j in range(42, 120):
            for radar_elevation in radar_data:
                radar_data[radar_elevation][i,j] = radar_data_raw[radar_elevation][i,j]

    for i in range(81, 240):
        for j in range(123, 258):
            for radar_elevation in radar_data:
                radar_data[radar_elevation][i,j] = radar_data_raw[radar_elevation][i,j]

    for i in range(37, 240):
        for j in range(264, 360):
            for radar_elevation in radar_data:
                radar_data[radar_elevation][i,j] = radar_data_raw[radar_elevation][i,j]
    '''
    
    
    #radar_data = bean_blocking(radar_data)
    #z_filt = attenuazione(radar_data)

    
    
    # Converto i dati da Z a dbz
    
    for r_el in radar_data:
        radar_data[r_el] = 10 * np.log10(radar_data[r_el])
        radar_data[r_el][(radar_data[r_el]) < 0 ] = np.nan
    
    z_filt = radar_data
    vmi = calcola_vmi(z_filt)

    #print(vmi)


    generate_map_plot(vmi)

