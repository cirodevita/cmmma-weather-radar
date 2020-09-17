import os
from pyunpack import Archive

'''
    Questo script prende in input una directory contentente gli archivi cab e 
    li estrare in un output directory con lo stesso nome dell'archivio.
'''

def unzipfile(filename,destfolder):
    os.mkdir(destfolder)
    try:
        Archive(filename).extractall(destfolder)
        print(f'{filename} extracted to {destfolder}')
    except ErrorName as e:
        print("Invalid cab file")
        print(e)
    

def bulk_unzip(input_path,output_path):

    files = os.listdir(input_path)
    for archive in files:
        if(archive.endswith('cab')):

            day_dir = os.path.join(output_path,archive[10:12])
            if not os.path.exists(day_dir):
                os.makedirs(day_dir)

            x = os.path.join(day_dir,archive.split('.')[0])
            unzipfile(os.path.join(input_path,archive),x)
    

if __name__ == '__main__':

    input_path = '/mnt/c/Users/Maimba/Desktop/RAW_GIUGNO_AV'
    output_path = '/mnt/c/Users/Maimba/Desktop/cmmma-weather-radar/data/AV/data'
   
    bulk_unzip(input_path,output_path)



