import os
from pyunpack import Archive

'''
    Questo script prende in input una directory contentente gli archivi cab e 
    li estrare in un output directory con lo stesso nome dell'archivio.
'''

def unzipfile(filename,destfolder):
    os.mkdir(destfolder)
    Archive(filename).extractall(destfolder)
    print(f'{filename} extracted to {destfolder}')


def bulk_unzip(input_path,output_path):

    files = os.listdir(input_path)
    for archive in files:
        if(archive.endswith('cab')):
            destfolder = os.path.join(output_path,archive.split('.')[0])
            unzipfile(os.path.join(input_path,archive),destfolder)


if __name__ == '__main__':

    input_path = '20200605_av'
    output_path = '../WR10X/AV/data'
   
    bulk_unzip(input_path,output_path)



