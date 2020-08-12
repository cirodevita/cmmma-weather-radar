from radar import Radar
from radar_to_plot import radar_to_plot
from radar_to_netcdf4 import radar_to_netcdf4


if __name__ == '__main__':

    radar_NA = 'WR10X/NA/radar_info.json'
    radar_AV = 'WR10X/AV/radar_info.json'
   
    print("Reading data...")
    R = Radar(radar_NA)
    print(R)

    print("Creating netcdf4 file...")
    radar_to_netcdf4(R)
    print("OK")

    print("Create plot image...")
    radar_to_plot(R)
    print("OK")
   