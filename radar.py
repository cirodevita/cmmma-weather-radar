import os
import sys
import struct
from datetime import datetime
import numpy as np

from StatisticalFilter import StatisticalFilter

import netCDF4 as nc

import warnings
warnings.filterwarnings('ignore')

class Radar:
    
    def __init__(self,lat0,lon0,kmdeg,radar_dir,radar_name):
        '''
            Costruttore della classe Radar.

            Parameters:
            lat0 (float)      : latitudine del radar
            lon0 (float)      : longitudine del radar
            cab_data (string) : path del contenuto del file .cab
        '''
        self.lat0     = lat0
        self.lon0     = lon0
        self.kmdeg    = kmdeg
        self.cab_data = os.path.join(radar_dir,'data')
        self.radar_name = radar_name


        # Legge i dati dai .z
        raw_radar_data = self.read_ppi_z_files(self.cab_data)
        # Applica il filtro statistico sui dati
        sfilt_radar_data = self.apply_statistical_filter(raw_radar_data)
        # Applico attenuazione
        self.radar_data = self.apply_attenuation(sfilt_radar_data)
        # Calcolo VMI
        self.vmi = self.calculate_vmi()
        # Calcolo Rain rate
        #self.rain_rate = self.calculate_rain_rate()


    def __str__(self):
        '''
            Serializza la classe Radar mostrando le informazioni più
            importanti.
        '''
        return (f'Scan id: {self.scan_id}\n'
                f'Name: {self.scan_name}\n'
                f'Data: {self.scan_datestamp}\n'
                f'Cab content: {self.cab_data}\n'
                f'Radar location (lat,lon): {self.lat0} {self.lon0}\n'
                f'Radar range (km): {self.radar_range}\n'
                f'Radar resolution (m): {self.radar_resolution}\n'
                f'Beam per azimut: {self.radar_ndata}')

    def read_ppi_z_files(self,cab_data):
        '''
            Legge i dati relativi alla scansione del radar dai file
            binari .z

            Parameters:
            cab_data (string) : path del contenuto del file .cab 
        '''
        list = os.listdir(cab_data)

        # Cerco il file .Scan
        scan_file = None
        for file in list:
            if file.endswith('.Scan'):
                scan_file=file
                continue

        # Se non trovo nessun file .Scan, esco
        if scan_file is None:
            print("[x] Nessun .Scan trovato.")
            sys.exit()

        self.scan_name = scan_file

        # Leggo lo scan id
        with open(os.path.join(cab_data,scan_file),'r') as sf:
            self.scan_id = sf.read().strip()

        # Scan data
        date_string = scan_file[4:16]
        self.scan_datestamp = datetime.strptime(date_string, '%Y%m%d%H%M')
        
        # Leggo i file binari filtrando solo i PPI-[..]-C.z
        raw_bytes = {}
        for file_name in list:
            meta_data = file_name.split('-')
            if meta_data[0] == 'PPI':
                if(meta_data[8] == 'C.z'):
                    el = meta_data[7][1:3] # Angolo di elevazione
                    with open(os.path.join(cab_data,file_name),'rb') as file:
                        raw_bytes[el] = file.read()

        # Raggio del radar
        self.radar_range = int(meta_data[4])/10
        # Risoluzione del radar
        self.radar_resolution = int(meta_data[5])
        # Numero di beam lungo una direzione
        self.radar_ndata = int(self.radar_range*1000 / self.radar_resolution)

        # Effettuo un unpack di bytes in gruppi da 16 bit (ushort) in little endian
        unpacked_bytes = {}
        for el in raw_bytes:
            unpacked_bytes[el] = struct.unpack('<' + str(len(raw_bytes[el]) // 2) + "H", raw_bytes[el])
            
            header_size = unpacked_bytes[el][0]
            data_format = unpacked_bytes[el][header_size-1]

            # Reshape dei dati
            unpacked_bytes[el] =  np.reshape(unpacked_bytes[el] ,(self.radar_ndata+header_size, 360), 'F')
            # Converto i dati in float32 (Requisito del filtro statistico)
            unpacked_bytes[el] = unpacked_bytes[el].astype('float32')
            # Converto i dati di dbz (dalla documentazione del WR10X)
            q_Z2Level = (pow(2,data_format)-1)*(-(-32)/(95.5-(-32)))
            m_Z2Level = (pow(2,data_format)-1)/(95.5-(-32))

            unpacked_bytes[el] = (unpacked_bytes[el]-q_Z2Level)/m_Z2Level
        
            # Elimino gli header in ogni riga
            unpacked_bytes[el] = unpacked_bytes[el][header_size:]

            # soglie di riflettività sulle matrici raw
            unpacked_bytes[el][(unpacked_bytes[el] > 55)] = 55

        return unpacked_bytes

    def apply_statistical_filter(self,radar_data):
        '''
            Applica il filtro statistico ai dati.

            Parameters:
             radar_data - dati della scansione
        '''
        data_mappe = []
        for radar_elevation in radar_data:
            data_mappe.append(radar_data[radar_elevation])

        Mappe = np.array(data_mappe)
        Etn_Th = 0.0005
        Txt_Th = 14.0
        Z_Th = -32

        d_filt1 = StatisticalFilter(Mappe, Etn_Th, Txt_Th, Z_Th)

        # Scompongo in dati filtrati
        index = 0
        for radar_elevation in radar_data:
            radar_data[radar_elevation] = d_filt1[index,:,:]
            index+=1

        return radar_data

    def apply_attenuation(self,radar_data):
        '''
            Correzione dell'attenuazione di percorso (PIA Algorithm)
        '''
        a = 0.000372
        b = 0.72

        A   = {}
        PIA = {}
        Z_filt = {}

        # Conversione riflettivita in Z
        for el in radar_data:
            radar_data[el][(radar_data[el] > 60)] = 60
            radar_data[el] = 10 ** (radar_data[el] / 10)

            A[el]  = np.zeros([self.radar_ndata, 360])
            PIA[el]  = np.zeros([self.radar_ndata, 360]) 
            Z_filt[el]  = np.zeros([self.radar_ndata, 360])
        
        
        for i in range(self.radar_ndata):
            for j in range(360):
                for el in radar_data:
                    A[el][i,j] = abs(0.6 * a * (radar_data[el][i, j] ** b))
                    A[el][np.isnan(A[el])] = 0.0

        for i in range(self.radar_ndata):
            for j in range(0,360):
                for el in radar_data:
                    PIA[el][i,j] = A[el][i, j] + PIA[el][i, j - 1]
        
        # ?
        for el in radar_data:
            PIA[el][(PIA[el]>10)] = 10
        

        for i in range(self.radar_ndata):
            for j in range(360):
                for el in radar_data:
                    #radar_data[el][i, j] = radar_data[el][i][j] * 10.0 ** ((PIA[el][i, j - 1] + PIA[el][i, j]) / 10.0)
                    #radar_data[el][i,j] = radar_data[el][i,j] + PIA[el][i][j-1] + A[el][i][j]
                    radar_data[el][i,j] = 10*np.log10(radar_data[el][i][j]) + PIA[el][i,j-1] + A[el][i,j]

        for el in radar_data:
            #radar_data[el] = 10*np.log10(radar_data[el])
            radar_data[el][(radar_data[el] < 4)] = np.nan

        return radar_data


    def calculate_vmi(self):
        '''
            Calcola la VMI della scansione.
        '''
        data = []
        for el in self.radar_data:
            data.append(self.radar_data[el])

        dbz_max = np.empty([self.radar_ndata, 360])
        for i in range(self.radar_ndata):
            for j in range(360):
                dbz_max[i, j] = np.nanmax( [item[i][j] for item in data] )

                if dbz_max[i, j] <= 0.0: 
                    dbz_max[i, j] = np.nan

        return dbz_max


    def calculate_rain_rate(self):
        '''
            Calcola il rain_rate
        '''
        a = 128.3
        b = 1.67

        rain_rate = np.empty([self.radar_ndata, 360])

        rain_rate = pow(pow(10,self.vmi/10)/a,1/b)

        return rain_rate


    def create_grid(self):
        ndata = self.radar_ndata

        rkm = np.zeros(ndata)
        for j in range(ndata):
            rkm[j] = self.radar_range *j/ndata

        z = np.zeros(360)
        for i in range(360):
            z[i] = np.pi*i/180

        self.lat = np.zeros([360, ndata], float)
        self.lon = np.zeros([360, ndata], float)

        for j in range(ndata):
            for i in range(360):
                self.lat[i, j] = self.lat0 + np.cos(z[i]) * rkm[j] / self.kmdeg
                self.lon[i, j] = self.lon0 + np.sin(z[i]) * (rkm[j] / self.kmdeg ) / np.cos(np.pi * self.lat[i, j] / 180.0)
        
        self.latmin = np.nanmin(self.lat)
        self.latmax = np.nanmax(self.lat)
        self.lonmin = np.nanmin(self.lon) - 0.02
        self.lonmax = np.nanmax(self.lon) + 0.02

    def save_as_netcd4(self):

        # Effettua l'interpolazione tra l'array circolare e il grigiato

        self.create_grid()
    
        c_lat = self.lat
        c_lon = self.lon

        grid_dim = 480

        grid_lat = np.arange(self.latmin,self.latmax,(self.latmax-self.latmin)/grid_dim)
        grid_lon = np.arange(self.lonmin,self.lonmax,(self.lonmax-self.lonmin)/grid_dim)

        grid = np.full([grid_dim,grid_dim],-999)

        for i in range(len(self.vmi)):
            for j in range(len(self.vmi[0])):
                if(not np.isnan(self.vmi[i,j])):
                    best_lat = np.abs(grid_lat-c_lat[j,i]).argmin()
                    best_lon = np.abs(grid_lon-c_lon[j,i]).argmin()
                    grid[best_lat,best_lon] = np.round(self.vmi[i,j])
                
        grid_lat = np.array([grid_lat,]*grid_dim).transpose()
        grid_lon = np.array([grid_lon]*grid_dim)

        fn = f'{self.radar_name}_{self.scan_datestamp}.nc'
        ds = nc.Dataset(fn, 'w', format='NETCDF4')

        # Dimensions
        ds.createDimension('eta_rho', grid_dim)
        ds.createDimension('xi_rho', grid_dim)

        # add unlimited dimension time
        lats = ds.createVariable('lat', 'f4', ('eta_rho','xi_rho'))
        lats.units = 'degree_north'
        lats._CoordinateAxisType = 'Lat'

        lons = ds.createVariable('lon', 'f4', ('eta_rho','xi_rho'))
        lons.units = 'degree_east'
        lons._CoordinateAxisType = 'Lon'

        reflectivity = ds.createVariable('reflectivity', 'i', ('eta_rho','xi_rho'),fill_value=-999)

        reflectivity[:] = grid
        lats[::] = grid_lat
        lons[::] = grid_lon

        ds.close()




