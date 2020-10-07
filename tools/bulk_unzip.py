import sys
import os
from pyunpack import Archive

'''
    Questo script prende in input una directory contentente gli archivi cab e 
    li estrare in un output directory con lo stesso nome dell'archivio facendo 
    automaticamente la divisione in giorni.
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

    if len(sys.argv) < 3:
        print(f'usage: {sys.argv[0]} <input directory path> <output directory path> ')
        exit(-1)

    print(f'Input path: {sys.argv[1]}')
    print(f'Input output: {sys.argv[2]}')

    bulk_unzip(sys.argv[1],sys.argv[2])



