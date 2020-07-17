# CMMMA Weather Radar
A tool for processing WR-10X (https://www.eldesradar.com/product/wr-10x/) weather radar data.

# Installation

#### Clone the repository and create the virtual enviroment for Python 3
```console
$ git clone https://github.com/CCMMMA/cmmma-weather-radar.git
$ cd cmmma-weather-radar
$ virtualenv venv
```
#### Activate the environment
```console
$ source venv/bin/activate
```
#### Install requirements
```console
$ pip install -r requirements.txt
```
#### Basemap module 
The script uses the module *mpl_toolkits.basemap*  so its dependencies must be installed as well.
```console
$ sudo apt install libgeos-3.5.0
$ sudo apt install libgeos-dev
$ pip install https://github.com/matplotlib/basemap/archive/master.zip
```
# Usage

Make sure you are inside the virtual enviroment and all the dependencies has been installed.

Run the script 
```console
$ python3 radar_step_NA.py
```

After the data has been processed the output will be saved in the "WR10X/radar" directory.
