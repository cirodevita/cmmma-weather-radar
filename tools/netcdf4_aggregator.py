import os
import sys
import numpy as np
import netCDF4 as nc


def aggregate(path, output_path=''):

    files = os.listdir(path)
    times = []
    for f in files:
        if f.endswith('nc'):
            times.append(f[14:16])
    times = set(times)

    for t in times:
        print(f'Aggregating scans for hour {t}...')

        t_files = [s for s in files if t in s[14:16]]

        nf = nc.Dataset(os.path.join(path, t_files[0]), 'r', format='NETCDF4')
        lat = nf['lat'][::]
        lon = nf['lon'][::]

        aggregated_file = nc.Dataset(os.path.join(output_path, t_files[0][0:16])+'.nc', 'w', format='NETCDF4')
        aggregated_file.createDimension('X' ,len(lat))
        aggregated_file.createDimension('Y', len(lon[0]))

        lats = aggregated_file.createVariable('lat', 'f4', ('X','Y'))
        lats.units = 'degree_north'
        lats._CoordinateAxisType = 'Lat'

        lons = aggregated_file.createVariable('lon', 'f4', ('X','Y'))
        lons.units = 'degree_east'
        lons._CoordinateAxisType = 'Lon'

        reflectivity = aggregated_file.createVariable('reflectivity', 'i', ('X','Y'),fill_value=-99.0)
        rain_rate    = aggregated_file.createVariable('rain_rate','i',('X','Y'),fill_value=-99.0)
        # poh_rate    = aggregated_file.createVariable('poh','i',('X','Y'),fill_value=-999)

        lats[::] = lat
        lons[::] = lon

        vmi = []
        rr  = []
        poh = []
        for f in t_files:
            nf = nc.Dataset(os.path.join(path,f), 'r', format='NETCDF4')
            vmi.append(nf['reflectivity'][::])
            rr.append(nf['rain_rate'][::])
            # poh.append(nf['poh'][::])

        # Calculate mean
        mean_vmi = np.full([len(lat), len(lon[0])], -99.0, dtype=np.float32)
        mean_rr = np.full([len(lat), len(lon[0])], -99.0, dtype=np.float32)
        mean_poh = np.full([len(lat), len(lon[0])], -99.0, dtype=np.float32)

        for i in range(len(mean_vmi)):
            for j in range(len(mean_vmi[0])):

                for d in vmi:
                    if d[i,j] != -99.0:
                        if mean_vmi[i, j] == -99.0:
                            mean_vmi[i, j] = d[i, j]
                        else:
                            mean_vmi[i, j] += d[i, j]
                for d in rr:
                    if d[i, j] != -99.0:
                        if mean_rr[i, j] == -99.0:
                            mean_rr[i, j] = d[i, j]
                        else:
                            mean_rr[i, j] += d[i, j]
                '''
                for d in poh:
                    if (d[i,j] != -999):
                        if mean_poh[i,j] == -999:
                            mean_poh[i,j] = d[i,j]
                        else:
                            mean_poh[i,j] += d[i,j]
                '''

        for i in range(len(mean_vmi)):
            for j in range(len(mean_vmi[0])):

                if mean_vmi[i, j] != -99.0:
                    mean_vmi[i, j] /= len(vmi)
                '''
                if mean_rr[i,j] != -999:
                    mean_rr[i,j] /= len(rr)
          
                if mean_poh[i,j] != -999:
                    mean_poh[i,j] /= len(poh)
                '''

        reflectivity[::] = mean_vmi
        rain_rate[:] = mean_rr
        # poh_rate[:] = mean_poh

        aggregated_file.close()

        print("OK")


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print(f'usage: {sys.argv[0]} <input directory> <output directory>')
        exit(-1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    aggregate(input_dir, output_dir)
    