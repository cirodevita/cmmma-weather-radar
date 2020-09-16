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
The script uses the module *mpl_toolkits.basemap*  for its plotting tool, so its dependencies must be installed as well if you are going to produce a plot.
```console
$ sudo apt install libgeos-3.5.0
$ sudo apt install libgeos-dev
$ pip install https://github.com/matplotlib/basemap/archive/master.zip
```

# Configuration 

In WR10X  there is a directory for each radar. Each directory contains a configuration json file wih this format:
```json
{
    "radar_id":"NA",
    "radar_location":[
       "40.843812",
       "14.238565"
    ],
    "kmdeg":111,
    "dir_data":"WR10X/NA/data/",
    "statistical_filter": {
        "Etn_Th" : 0.0005,
        "Txt_Th" : 14.0,
        "Z_Th" : -32
    },
    "sea_clutter" : {
        "interval" : [126,256,0,70],
        "levels" : ["01","02"],
        "T1" : 50.0,
        "T2" : 0.0
    },
    "com_map_path" : "WR10X/NA/"
 }
```
Where:


|  Value |  Description|
| ------------ | ------------ |
|  radar_id | A radar identifier |
|  radar_location  | The radar location position [lat,lon]  |
|  kmdeg  | Kilometers per degree  |
| dirdata  | Directory that contains the radar scan data  |
|  statistical_filter | Parameters for the statistical filter  |
|  sea_clutter |  Intervals, elevation level and threshold values for the sea clutter algorithm |
| com_map_path | Path for the compensation map used for the beam blocking  |


# Usage

The tool directory contains a set of scripts.

W.I.P.

You can run a script with the following command
```console
$ python3 <script-name>.py
```
