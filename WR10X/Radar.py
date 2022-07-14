import os
import sys
import json
import warnings

from .utils.statistical_filter import StatisticalFilter
from .wr10x_data_adapter import WR10X_bin_coverter
import numpy as np

warnings.filterwarnings('ignore')
np.set_printoptions(threshold=sys.maxsize)
sys.path.append(os.getcwd())

required_levels = ['01', '02', '03', '04']


class Radar:
    def __init__(self, radar_config_file_path, scan_data):
        with open(radar_config_file_path) as f:
            config_file = json.load(f)

        self._id = config_file['radar_id']
        self._location = (float(config_file['radar_location'][0]), float(config_file['radar_location'][1]))
        self._kmdeg = float(config_file['kmdeg'])
        self._dir_data = scan_data
        self._config_file = config_file

        self.read_ppi_z_files(self._dir_data)

        if not set(required_levels).issubset(set(self._data.keys())):
            raise NameError('Invalid scan')

        self.apply_statistical_filter()

        if self._config_file['sea_clutter'] is not None:
            self.remove_sea_clutter()
        if self._config_file['com_map_path'] is not None:
            self.beam_blocking()

        self.apply_attenuation()
        self.create_grid()

    def __str__(self):
        '''
            Serialize the class
        '''
        return (f'Scan id: {self._scan_id}\n'
                f'Name: {self._scan_name}\n'
                f'Data: {self._scan_datestamp}\n'
                f'Data directory: {self._dir_data}\n'
                f'Location (lat,lon): {self._location[0]} {self._location[1]}\n'
                f'Range (km): {self._range}\n'
                f'Resolution (m): {self._resolution}\n'
                f'Beam per azimut: {self._ndata}')

    def read_ppi_z_files(self, bin_dir):
        converter = WR10X_bin_coverter(bin_dir)
        # Get scan data
        self._data = converter.get_radar_data()
        # Get scan metadata
        scan_metadata = converter.get_scan_data()
        self._scan_id = scan_metadata['id']
        self._scan_name = scan_metadata['name']
        self._scan_datestamp = scan_metadata['datestamp']
        self._range = scan_metadata['range']
        self._resolution = scan_metadata['resolution']
        self._ndata = scan_metadata['ndata']

    def apply_statistical_filter(self):
        # Converts dictionaries in lists
        data_mappe = []
        for el in self._data:
            data_mappe.append(self._data[el])
        data = np.array(data_mappe)
        # Reads threshold values
        Etn_Th = self._config_file['statistical_filter']['Etn_Th']
        Txt_Th = self._config_file['statistical_filter']['Txt_Th']
        Z_Th = self._config_file['statistical_filter']['Z_Th']

        d_filt1 = StatisticalFilter(data, Etn_Th, Txt_Th, Z_Th)
        # Decompose data
        index = 0
        for el in self._data:
            self._data[el] = d_filt1[index, :, :]
            index += 1

    def remove_sea_clutter(self):

        rd = np.empty([self._ndata, 360])
        # Reads the levels and thresholds for applying
        # the algorithm
        v1 = self._config_file['sea_clutter']['levels'][0]
        v2 = self._config_file['sea_clutter']['levels'][1]
        T1 = self._config_file['sea_clutter']['T1']
        T2 = self._config_file['sea_clutter']['T2']
        # Reads in interval in which apply the algorithm
        # (This reduce the number of operations)
        theta1 = self._config_file['sea_clutter']['interval'][0]
        theta2 = self._config_file['sea_clutter']['interval'][1]
        rho1 = self._config_file['sea_clutter']['interval'][2]
        rho2 = self._config_file['sea_clutter']['interval'][3]

        for i in range(self._ndata):
            for j in range(360):
                rd[i, j] = self._data[v1][i, j] - self._data[v2][i, j]
        rd[rd == 0] = np.nan

        for j in range(theta1, theta2):
            for i in range(rho1, rho2):
                if (rd[i, j] > T1) or (rd[i, j] > 0.0 and self._data[v2][i, j] < T2):
                    self._data[v1][i, j] = self._data[v2][i, j]

    def beam_blocking(self):
        '''
            Reduce the beam occlusion caused by the orography
        '''
        cm_path = self._config_file['com_map_path']
        files = os.listdir(cm_path)
        # Read compensation maps
        MC = {}
        for f in files:
            if (f.startswith('mc')):
                el = f.split('-')[1]
                MC[el] = np.loadtxt(os.path.join(cm_path, f))
        # Apply the reflectivity increment
        for el in MC:
            for i in range(self._ndata):
                for j in range(360):
                    if self._data[el][i, j] <= 0.0:
                        self._data[el][i, j] = np.nan
                    self._data[el][i, j] += MC[el][i, j]

    def apply_attenuation(self):
        '''
           Path Integrated Attenuation
        '''
        a = 0.000372
        b = 0.72

        A = {}
        PIA = {}
        Z_filt = {}

        # Converts reflectovity Z
        for el in self._data:
            self._data[el] = 10 ** (self._data[el] / 10)
            A[el] = np.zeros([self._ndata, 360])
            PIA[el] = np.zeros([self._ndata, 360])
            Z_filt[el] = np.zeros([self._ndata, 360])
        # Calculate the attenuation coefficents
        for i in range(self._ndata):
            for j in range(360):
                for el in self._data:
                    A[el][i, j] = abs(0.6 * a * (self._data[el][i, j] ** b))
                    A[el][np.isnan(A[el])] = 0.0
        # Calculate the PIA
        for i in range(self._ndata):
            for j in range(0, 360):
                for el in self._data:
                    PIA[el][i, j] = A[el][i, j] + PIA[el][i - 1, j]
        for el in self._data:
            PIA[el][(PIA[el] > 10)] = 10
        # Calculate the correct reflectivity value
        for i in range(self._ndata):
            for j in range(360):
                for el in self._data:
                    self._data[el][i, j] = 10 * np.log10(self._data[el][i][j]) + PIA[el][i, j - 1] + A[el][i, j]
        for el in self._data:
            self._data[el][(self._data[el] < 4)] = np.nan

    def calculate_vmi(self):
        # Converts data from dictionary to lists
        data = []
        for el in self._data:
            data.append(self._data[el])
        # Calcualte the maximum along the vertical for
        # each bin
        vmi = np.empty([self._ndata, 360])
        for i in range(self._ndata):
            for j in range(360):
                vmi[i, j] = np.nanmax([z[i][j] for z in data])
                if vmi[i, j] <= 0.0:
                    vmi[i, j] = np.nan
        return vmi

    def calculate_rain_rate(self):
        # Empirical coefficients for Z/R relationship
        a = 128.3
        b = 1.67
        vmi = self.calculate_vmi()
        return pow(pow(10, vmi / 10) / a, 1 / b)
        # Marshall Palmer
        # return ((10**(vmi/10))/200)**(5/8)

    def calculate_poh(self):

        el = ['01', '02', '03', '04', '05', '07', '10', '12', '15']
        H = []
        for f in el:
            H.append(np.loadtxt(os.path.join(self._config_file['H_dir'], f)))

        a = 3.44 * (10 ** -6)
        b = 4 / 7.0

        Zf = []
        for level in el:
            Zf.append(self._data[level])

        Zf = 10 ** (np.array(Zf) / 10.0)
        Zf[np.isnan(Zf)] = 0

        w = a * (Zf ** b)

        VIL = w[0, :, :] * H[0]
        for k in range(1, 9):
            VIL += w[k - 1] * (H[k] - H[k - 1]) + ((H[k] - H[k - 1]) * (w[k] - w[k - 1])) / 2

        VIL[VIL == 0] = np.nan

        echotop = np.empty([240, 360])
        for i in range(240):
            for j in range(360):
                for k in range(6)[::-1]:
                    if not np.isnan(w[k, i, j]):
                        psv = H[k]
                        echotop[i, j] = psv[i, j]
                        break

        VILD = np.array([240, 360])
        VILD = (VIL / echotop) * 1000

        d4 = -0.5395
        d3 = 1.483
        d2 = -0.5623
        d1 = 0.07278

        POH = ((d1 * (VILD ** 3) + d2 * (VILD ** 2) + d3 * (VILD) + d4)) * 100
        POH[POH < 0] = 0
        POH[POH == 0] = np.nan
        POH[POH > 100] = 100

        return POH

    def create_grid(self):
        '''
            Calculate the georeferenced grid
        '''
        ndata = self._ndata

        rkm = np.zeros(ndata)
        for j in range(ndata):
            rkm[j] = self._range * j / ndata

        # Angles in radians
        z = np.zeros(360)
        for i in range(360):
            z[i] = np.pi * i / 180

        self.lat = np.zeros([360, ndata], float)
        self.lon = np.zeros([360, ndata], float)

        for j in range(ndata):
            for i in range(360):
                self.lat[i, j] = self._location[0] + np.cos(z[i]) * rkm[j] / self._kmdeg
                self.lon[i, j] = self._location[1] + np.sin(z[i]) * (rkm[j] / self._kmdeg) / np.cos(
                    np.pi * self.lat[i, j] / 180.0)

        self.latmin = np.nanmin(self.lat)
        self.latmax = np.nanmax(self.lat)
        self.lonmin = np.nanmin(self.lon) - 0.02
        self.lonmax = np.nanmax(self.lon) + 0.02
