import pandas as pd
import glob
import sys
import os


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'usage: {sys.argv[0]} <input directory> <output directory>')
        exit(-1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    li = []

    for filename in glob.glob(input_dir + "/*.csv"):
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)

    frame = pd.concat(li, axis=0, ignore_index=True)

    frame.to_csv(os.path.join(output_dir, 'dataset.csv'))
