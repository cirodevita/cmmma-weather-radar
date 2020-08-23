import os
import radar_composite_netcdf4 
from radar import Radar

if __name__ == '__main__':

    radar_NA = 'WR10X/NA/radar_info.json'
    radar_AV = 'WR10X/AV/radar_info.json'

    av = 'WR10X/AV/data/'
    na = 'WR10X/NA/data/'
    scans_av = os.listdir(av)
    scans_na = os.listdir(na)
    scans = [value for value in scans_av if value in scans_na]

    for scan in scans:

        print(f'Composing for {scan}...',end='')

        radars = []
        radars.append(Radar(radar_NA,scan))
        radars.append(Radar(radar_AV,scan))
        radar_composite_netcdf4.compose(radars,'output')

        print('OK')
    