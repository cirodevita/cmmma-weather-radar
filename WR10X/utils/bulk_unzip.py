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
    except:
        print("Invalid cab file")
    

def bulk_unzip(input_path,output_path):

    files = os.listdir(input_path)
    for archive in files:
        if(archive.endswith('cab')):
            x = os.path.join(output_path,archive[10:12],archive.split('.')[0])
            unzipfile(os.path.join(input_path,archive),x)
    

if __name__ == '__main__':

    input_path = '/mnt/c/Users/Maimba/Desktop/DATA_RAW_11_2019'
    output_path = '/mnt/c/Users/Maimba/Desktop/DATA_RAW'
   
    bulk_unzip(input_path,output_path)



