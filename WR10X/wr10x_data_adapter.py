import os
import struct
import numpy as np
from datetime import datetime

'''
    Questa classe si occupa di convertire i dati in formato binario proprietario
    del WR10X in un dizionario di array 2d 
'''


class WR10X_bin_coverter:
    def __init__(self, bin_directory):

        if not os.path.isdir(bin_directory):
            raise NameError('Binary directory not found')

        self._bin_directory = bin_directory
        self.convert_data()

    def convert_data(self):
        # Read scan data binaries and parse it.
        files = os.listdir(self._bin_directory)

        # Search for .Scan file
        self._scan_name = ''.join([f for f in files if f.endswith(('.Scan'))])
        if not self._scan_name:
            raise NameError('Scan file not found')

        # Read scan_ID
        with open(os.path.join(self._bin_directory, self._scan_name), 'r') as sf:
            self._scan_id = sf.read().strip()

        # Scan data
        self._scan_datestamp = datetime.strptime(self._scan_name[4:16], '%Y%m%d%H%M')

        # Read binaries files
        bins = [f for f in files if f.endswith('-C.z') and f.startswith('PPI')]
        raw_bytes = {}
        for f in bins:
            el = f[39:41]
            with open(os.path.join(self._bin_directory, f), 'rb') as file:
                raw_bytes[el] = file.read()
        # Radar range (km)
        self._range = int(f[23:27]) / 10
        # Radar resolution (m)
        self._resolution = int(f[28:32])
        # Bin per beam
        self._ndata = int(self._range * 1000 / self._resolution)
        # Unpack data in 16 bytes (ushort) for group using little endian
        upck_bytes = {}
        for el in raw_bytes:
            upck_bytes[el] = struct.unpack('<' + str(len(raw_bytes[el]) // 2) + "H", raw_bytes[el])
            # Data reshape
            header_size = upck_bytes[el][0]
            upck_bytes[el] = np.reshape(upck_bytes[el], (self._ndata + header_size, 360), 'F')
            upck_bytes[el] = upck_bytes[el].astype('float32')
            # Converts data in dBZ (From WR10X doc)
            data_format = upck_bytes[el][header_size - 1]
            q_Z2Level = (pow(2, data_format) - 1) * (-(-32) / (95.5 - (-32)))
            m_Z2Level = (pow(2, data_format) - 1) / (95.5 - (-32))
            upck_bytes[el] = (upck_bytes[el] - q_Z2Level) / m_Z2Level
            # Delete headers
            upck_bytes[el] = upck_bytes[el][header_size:]
            upck_bytes[el][(upck_bytes[el] > 55)] = 55

        self._radar_data = upck_bytes

    def get_radar_data(self):
        return self._radar_data

    def get_scan_data(self):

        scan_data = {}

        scan_data['name'] = self._scan_name
        scan_data['id'] = self._scan_id
        scan_data['datestamp'] = self._scan_datestamp
        scan_data['range'] = self._range
        scan_data['resolution'] = self._resolution
        scan_data['ndata'] = self._ndata

        return scan_data
