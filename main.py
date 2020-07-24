from radar import Radar
import numpy as np
import os

if __name__ == '__main__':

    # NAPOLI    
    radar_name = 'NA'
    lat0 = 40.843812
    lon1 = 14.238565

    # AVELLINO
    #radar_name = 'AV'
    #lat0 = 41.052167
    #lon1 = 15.235667

    radar_dir = f'WR10X/{radar_name}/'
    path_data = "WR10X"
    path_output = "WR10X"

    R = Radar(lat0,lon1,radar_dir)
    print(R)

    data = R.calculate_vmi()
    np.savetxt(os.path.join(path_output,f'VMI_{radar_name}.out'), data.astype(int), fmt='%i')
