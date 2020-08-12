import os
import sys
import struct
import json
from datetime import datetime
import numpy as np

from StatisticalFilter import StatisticalFilter

import warnings
warnings.filterwarnings('ignore')

class Radar:

    def __init__ (self, radar_config_file_path):

        with open(radar_config_file_path) as f:
            config_file = json.load(f)
        
        self._id       = config_file['radar_id']
        self._location = (float(config_file['radar_location'][0]),float(config_file['radar_location'][1]))
        self._kmdeg    = float(config_file['kmdeg'])
        self._dir_data = config_file['dir_data']

        self._config_file = config_file

        self._data = self.read_ppi_z_files()
        
        self.apply_statistical_filter()

        if self._config_file['sea_clutter'] is not None:
            self.remove_sea_clutter()
    
        if self._config_file['com_map_path'] is not None:
            self.beam_blocking()
        
        #self.apply_attenuation()

        self.create_grid()

    def __str__(self):
        '''
            Serializza la classe Radar mostrando le informazioni più
            importanti.
        '''
        return (f'Scan id: {self._scan_id}\n'
                f'Name: {self._scan_name}\n'
                f'Data: {self._scan_datestamp}\n'
                f'Directory data: {self._dir_data}\n'
                f'Radar location (lat,lon): {self._location[0]} {self._location[1]}\n'
                f'Radar range (km): {self._range}\n'
                f'Radar resolution (m): {self._resolution}\n'
                f'Beam per azimut: {self._ndata}')

    def read_ppi_z_files(self):
        """Legge i dati relativi alla scansione del radar.
        
        La lettura è effettuata solo delle scansione cluttered. È necessario che sia
        presente il file .Scan nella directory.

        Returns
        -------
        upck_bytes : dictionary
                     Contiene i valori di reflettività espressi in dbmz per ogni grado
                     di elevazione. Il grado è utilizzato come key.

        """

        files = os.listdir(self._dir_data)
    
        # Cerco il file .Scan
        self._scan_name = ''.join([f for f in files if f.endswith(('.Scan'))])
        if not self._scan_name :
            raise FileNotFound
        
        # Leggo lo scan id
        with open(os.path.join(self._dir_data,self._scan_name),'r') as sf:
            self._scan_id = sf.read().strip()
        
        # Scan data
        self._scan_datestamp = datetime.strptime(self._scan_name[4:16], '%Y%m%d%H%M')

        # Leggo tutti i file binari
        bins = [f for f in files if f.endswith('-C.z') and f.startswith('PPI')]
        raw_bytes = {}
        for f in bins:
            el = f[39:41]
            with open(os.path.join(self._dir_data,f),'rb') as file:
                raw_bytes[el] = file.read()

        # Raggio del radar (km)
        self._range = int(f[23:27])/10
        # Risoluzione del radar (m)
        self._resolution = int(f[28:32])
        # Numero di beam lungo una direzione
        self._ndata = int(self._range*1000 / self._resolution)

        # Effettuo un unpack di bytes in gruppi da 16 bit (ushort) in little endian
        upck_bytes = {}
        for el in raw_bytes:
            upck_bytes[el] = struct.unpack('<' + str(len(raw_bytes[el]) // 2) + "H", raw_bytes[el])
            
            # Reshape dei dati
            header_size = upck_bytes[el][0]
            upck_bytes[el] =  np.reshape(upck_bytes[el] ,(self._ndata+header_size, 360), 'F')
            
            # Converto i dati in float32 (Requisito del filtro statistico)
            upck_bytes[el] = upck_bytes[el].astype('float32')
            
            # Converto i dati di dbz (dalla documentazione del WR10X)
            data_format = upck_bytes[el][header_size-1]
            q_Z2Level = (pow(2,data_format)-1)*(-(-32)/(95.5-(-32)))
            m_Z2Level = (pow(2,data_format)-1)/(95.5-(-32))
            upck_bytes[el] = (upck_bytes[el]-q_Z2Level)/m_Z2Level
        
            # Elimino gli header in ogni riga
            upck_bytes[el] = upck_bytes[el][header_size:]
            
            # TODO : Verificare
            # Soglie di riflettività sulle matrici raw
            upck_bytes[el][(upck_bytes[el] > 55)] = 55

        return upck_bytes


    def apply_statistical_filter(self):
        '''
            Applica il filtro statistico ai dati.
            Parameters:
             radar_data - dati della scansione
        '''
        data_mappe = []
        for el in self._data:
            data_mappe.append(self._data[el])

        Mappe = np.array(data_mappe)
        Etn_Th = self._config_file['statistical_filter']['Etn_Th']
        Txt_Th = self._config_file['statistical_filter']['Txt_Th']
        Z_Th   = self._config_file['statistical_filter']['Z_Th']

        d_filt1 = StatisticalFilter(Mappe, Etn_Th, Txt_Th, Z_Th)
        # Scompongo in dati filtrati
        index = 0
        for el in self._data:
            self._data[el] = d_filt1[index,:,:]
            index+=1

    def remove_sea_clutter(self):

        rd = np.empty([self._ndata, 360])

        v1 = self._config_file['sea_clutter']['levels'][0]
        v2 = self._config_file['sea_clutter']['levels'][1]
        T1 = self._config_file['sea_clutter']['T1']
        T2 = self._config_file['sea_clutter']['T2']

        theta1 = self._config_file['sea_clutter']['interval'][0]
        theta2 = self._config_file['sea_clutter']['interval'][1]
        rho1 = self._config_file['sea_clutter']['interval'][2]
        rho2 = self._config_file['sea_clutter']['interval'][3]


        for i in range(self._ndata):
            for j in range(360):
                rd[i, j] = self._data[v1][i,j] - self._data[v2][i,j]
        rd[rd == 0] = np.nan

        for j in range(theta1, theta2):
            for i in range(rho1,rho2):
                if (rd[i, j] > T1) or (rd[i, j] > 0.0 and self._data[v2][i, j] < T2):
                    self._data[v1][i, j] = self._data[v2][i, j]


    def beam_blocking(self):

        cm_path = self._config_file['com_map_path']
        files = os.listdir(cm_path)

        MC = {}
        for f in files:
            if(f.startswith('mc')):
                el = f.split('-')[1]
                MC[el] = np.loadtxt(os.path.join(cm_path,f))

        
        for el in MC:
            for i in range(self._ndata):
                for j in range(360):
                    if self._data[el][i,j] <= 0.0:
                        self._data[el][i,j] = np.nan
                    self._data[el][i,j] += MC[el][i,j]

        

    def apply_attenuation(self):
        '''
            Correzione dell'attenuazione di percorso (PIA Algorithm)
        '''
        a = 0.000372
        b = 0.72

        A   = {}
        PIA = {}
        Z_filt = {}

        # Conversione riflettivita in Z
        for el in self._data:
            #self._data[el][( self._data[el] > 60)] = 60
            self._data[el] = 10 ** ( self._data[el] / 10)

            A[el]  = np.zeros([self._ndata, 360])
            PIA[el]  = np.zeros([self._ndata, 360]) 
            Z_filt[el]  = np.zeros([self._ndata, 360])
        
        
        for i in range(self._ndata):
            for j in range(360):
                for el in  self._data:
                    A[el][i,j] = abs(0.6 * a * ( self._data[el][i, j] ** b))
                    A[el][np.isnan(A[el])] = 0.0

        for i in range(self._ndata):
            for j in range(0,360):
                for el in self._data:
                    PIA[el][i,j] = A[el][i, j] + PIA[el][i, j - 1]
        
        # ?
        for el in self._data:
            PIA[el][(PIA[el]>10)] = 10
        

        for i in range(self._ndata):
            for j in range(360):
                for el in  self._data:
                    #radar_data[el][i, j] = radar_data[el][i][j] * 10.0 ** ((PIA[el][i, j - 1] + PIA[el][i, j]) / 10.0)
                    #radar_data[el][i,j] = radar_data[el][i,j] + PIA[el][i][j-1] + A[el][i][j]
                    self._data[el][i,j] = 10*np.log10( self._data[el][i][j]) + PIA[el][i,j-1] + A[el][i,j]

        for el in  self._data:
            #radar_data[el] = 10*np.log10(radar_data[el])
             self._data[el][( self._data[el] < 4)] = np.nan

    
    def calculate_vmi(self):
        '''
            Calcola la VMI della scansione.
        '''
        data = []
        for el in self._data:
            data.append(self._data[el])

        vmi = np.empty([self._ndata, 360])
        for i in range(self._ndata):
            for j in range(360):
                vmi[i, j] = np.nanmax( [z[i][j] for z in data] )

                if vmi[i, j] <= 0.0: 
                    vmi[i, j] = np.nan

        return vmi

    def calculate_rain_rate(self):
        '''
            Calcola il rain_rate
        '''
        a = 128.3
        b = 1.67

        vmi = self.calculate_vmi()

        rain_rate = np.empty([self._ndata, 360])

        rain_rate = pow(pow(10,vmi/10)/a,1/b)

        return rain_rate

    def create_grid(self):
        '''
            Calcola il grigliato georiferito
        '''
        ndata = self._ndata

        rkm = np.zeros(ndata)
        for j in range(ndata):
            rkm[j] = self._range *j/ndata

        z = np.zeros(360)
        for i in range(360):
            z[i] = np.pi*i/180

        self.lat = np.zeros([360, ndata], float)
        self.lon = np.zeros([360, ndata], float)

        for j in range(ndata):
            for i in range(360):
                self.lat[i, j] = self._location[0] + np.cos(z[i]) * rkm[j] / self._kmdeg
                self.lon[i, j] = self._location[1] + np.sin(z[i]) * (rkm[j] / self._kmdeg ) / np.cos(np.pi * self.lat[i, j] / 180.0)
        
        self.latmin = np.nanmin(self.lat)
        self.latmax = np.nanmax(self.lat)
        self.lonmin = np.nanmin(self.lon) - 0.02
        self.lonmax = np.nanmax(self.lon) + 0.02
    
