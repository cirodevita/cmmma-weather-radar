import sys
import os
from pyunpack import Archive


def unzipFile(filename, dst_folder):
    os.mkdir(dst_folder)
    try:
        Archive(filename).extractall(dst_folder)
        print(f'{filename} extracted to {dst_folder}')
    except Exception as e:
        print("Invalid cab file")
        print(e)
    

def bulkUnzip(input_path, output_path):

    files = os.listdir(input_path)
    for archive in files:
        if archive.endswith('cab'):
            year_dir = os.path.join(output_path, archive[4:8])
            if not os.path.exists(year_dir):
                os.makedirs(year_dir)

            month_dir = os.path.join(year_dir, archive[8:10])
            if not os.path.exists(month_dir):
                os.makedirs(month_dir)

            day_dir = os.path.join(month_dir, archive[10:12])
            if not os.path.exists(day_dir):
                os.makedirs(day_dir)

            x = os.path.join(day_dir, archive.split('.')[0])
            unzipFile(os.path.join(input_path, archive), x)
    

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print(f'usage: {sys.argv[0]} <input directory path> <output directory path> ')
        exit(-1)

    print(f'Input path: {sys.argv[1]}')
    print(f'Output path: {sys.argv[2]}')

    bulkUnzip(sys.argv[1], sys.argv[2])
