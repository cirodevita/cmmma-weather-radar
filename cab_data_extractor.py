from os import listdir
from os import path
import sys
import struct

import numpy as np


'''
    Dato un path in cui sono presenti i file .z restituisce una matrice np 
    con i dati letti, privi dei 23 headers
'''
def cab_to_mat(path):
    list = listdir(path)

    # Cerco il file .Scan
    name = None
    for file in list:
        if file.endswith('.Scan'):
            name=file
            continue

    if name is None:
        print("[x] Not able to find the \".Scan\" file.")
        sys.exit()

    # Memorizzo dati della scansione
    yyyy = name[4:8]
    mm   = name[8:10]
    dd   = name[10:12]
    hh   = name[12:14]
    mi   = name[14:16]
    date = f"{dd}/{mm}/{yyyy} {hh}:{mi} UTC"


    # TODO: Rendere tali valori dinamici, non hardcoded
    radar_range = 108000
    radar_resolution = 450
    data_row = radar_range / radar_resolution

    # Stampa informazioni
    print(f"name: {name}\ndate {date}\nradar range: {radar_range} m\nradar resolution: {radar_resolution} m ")

    # Leggo raw bytes dai file
    raw_bytes = {}
    for file_name in list:
        if(file_name[0:3] == "PPI" and file_name[-3] == "U"):
            r_el = file_name[39:41] # Radar elevation
            with open(path+file_name,'rb') as file:
                raw_bytes[r_el] = file.read()
  
    radar_data = {}
    for r_el in raw_bytes:
        # Unpack dei dati in ushort a 16 bit
        radar_data[r_el] = struct.unpack('<' + str(len(raw_bytes[r_el]) // 2) + "H", raw_bytes[r_el])
       
        # Reshape dei dati
        radar_data[r_el] =  np.reshape(radar_data[r_el] ,(263, 360), 'F')

        # Converto i dati in float32
        radar_data[r_el] = radar_data[r_el].astype('float32')

        # Vengono fatte queste operazioni nello script Fortran
        #radar_data[r_el] = (radar_data[r_el]-64)/2
        #radar_data[r_el][(radar_data[r_el] > 64)] = 64
        #radar_data[r_el] = np.around(radar_data[r_el])

        # Elimino gli header in ogni riga
        radar_data[r_el] = radar_data[r_el][23:]
    
    return radar_data
