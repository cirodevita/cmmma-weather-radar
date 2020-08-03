from radar import Radar
from radar_to_plot import radar_to_plot
from radar_to_netcdf4 import radar_to_netcdf4


if __name__ == '__main__':

    path_output = ''
      
    radar_id = 'NA'
    radar_location = (40.843812,14.238565)
    kmdeg = 111.0
    radar_dir = f'WR10X/{radar_id}/data'
   
    print("Reading data...")
    R = Radar(radar_id,radar_location,kmdeg,radar_dir)
    print(R)

    print("Creating netcdf4 file...")
    radar_to_netcdf4(R)
    print("OK")

    print("Create plot image...")
    radar_to_plot(R)
    print("OK")
   