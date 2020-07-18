from os import listdir
from os import path
import sys
import struct

import numpy as np

def read_ppi_z_files(path):

    list = listdir(path)

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

    # Leggo i file binari .z
    raw_bytes = {}
    for file_name in list:
        meta_data = file_name.split('-')

        # Non considera i file non di scansione
        if len(meta_data) < 9 : 
            continue

        if meta_data[0] == 'PPI' and meta_data[8][0] == 'C':
          
            el = meta_data[7][1:3] 

            with open(path+file_name,'rb') as file:
                raw_bytes[el] = file.read()

    # Effettuo un unpack di bytes in gruppi da 16 bit (ushort)
    unpacked_bytes = {}
    for el in raw_bytes:
        unpacked_bytes[el] = struct.unpack('<' + str(len(raw_bytes[el]) // 2) + "H", raw_bytes[el])

    
    # Estraggo i metadata riguardo la scansione e il radar
    yyyy = meta_data[2][0:4]
    mm   = meta_data[2][4:6]
    dd   = meta_data[2][6:8]
    hh   = meta_data[2][8:10]
    mi   = meta_data[2][10:12]

    scan_date = f"{dd}/{mm}/{yyyy} {hh}:{mi} UTC"
    radar_range = int(meta_data[4])*100
    radar_resolution = int(meta_data[5])
    print(f'Name: {scan_file}')
    print(f'Scan Date: {scan_date}')
    print(f'Radar range: {radar_range} m')
    print(f'Radar resolution: {radar_resolution} m')


    return unpacked_bytes

'''
    Dato un path in cui sono presenti i file .z restituisce una matrice np 
    con i dati letti, privi dei 23 headers
'''
def get_radar_data(path):


    radar_data = read_ppi_z_files(path)
   
    for el in radar_data:
        # Reshape dei dati
        radar_data[el] =  np.reshape(radar_data[el] ,(263, 360), 'F')
        # Elimino gli header in ogni riga
        radar_data[el] = radar_data[el][23:]
        # Converto i dati in float32 (Requisito del filtro statistico)
        radar_data[el] = radar_data[el].astype('float32')
        # Converto i dati da Z a dbz
        #radar_data[el] = 10 * np.log10(radar_data[r_el])
        #radar_data[el][(radar_data[r_el]) < 0 ] = np.nan
        
        '''
        # Ulteriori operazioni fatte dallo script in Fortran 
        q = 64
        m = 2
        radar_data[el] = (radar_data[r_el]-q)/m
        radar_data[el][(radar_data[r_el] > q)] = 64
        radar_data[el] = np.around(radar_data[r_el])
        '''
    return radar_data
    

if __name__ == "__main__" : 
    pass