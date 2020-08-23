import os
import numpy as np
import netCDF4 as nc


def aggregate(path,output_path=''):

    files = os.listdir(path)
    times = []
    for f in files:
        if(f.endswith('nc')):
            times.append(f[17:19])
    times = set(times)

    for t in times:
        print(f'Aggregating scans for hour {t}...')

        t_files = [s for s in files if t in s[17:19]]

        nf = nc.Dataset(os.path.join(path,t_files[0]), 'r', format='NETCDF4')
        lat = nf['lat'][::]
        lon = nf['lon'][::]

        aggregated_file = nc.Dataset(os.path.join(output_path,t_files[0][0:19])+'.nc', 'w', format='NETCDF4')
        aggregated_file.createDimension('X' ,len(lat))
        aggregated_file.createDimension('Y', len(lon[0]))

        lats = aggregated_file.createVariable('lat', 'f4', ('X','Y'))
        lats.units = 'degree_north'
        lats._CoordinateAxisType = 'Lat'

        lons = aggregated_file.createVariable('lon', 'f4', ('X','Y'))
        lons.units = 'degree_east'
        lons._CoordinateAxisType = 'Lon'

        reflectivity = aggregated_file.createVariable('reflectivity', 'i', ('X','Y'),fill_value=-999)

        lats[::] = lat
        lons[::] = lon

        data = []
        for f in t_files:
            nf = nc.Dataset(os.path.join(path,f), 'r', format='NETCDF4')
            data.append(nf['reflectivity'][::])

        mean =  grid = np.full([len(lat),len(lon[0])],-999)

        for i in range(len(mean)):
            for j in range(len(mean[0])):
                for d in data:
                    if (d[i,j] != -999):
                        if mean[i,j] == -999:
                            mean[i,j] = d[i,j]
                        else:
                            mean[i,j] += d[i,j]
        

        for i in range(len(mean)):
            for j in range(len(mean[0])):
                if mean[i,j] != -999:
                    mean[i,j] /= len(data)
        
        reflectivity[::] = mean

        aggregated_file.close()

        print("OK")



   


if __name__ == '__main__':

    path = 'output'
    output_path = 'output_h'
    aggregate(path,output_path)