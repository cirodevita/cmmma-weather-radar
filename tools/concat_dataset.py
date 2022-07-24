import sys
import os
import pandas as pd


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'usage: {sys.argv[0]} <input directory> <output directory>')
        exit(-1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]

    dataset = []

    for path, subdirs, files in os.walk(input_directory):
        for name in files:
            if name == "dataset.csv":
                filename = os.path.join(path, name)
                df = pd.read_csv(filename, index_col=None, header=0)
                dataset.append(df)

    frame = pd.concat(dataset, axis=0, ignore_index=True)

    frame.to_csv(os.path.join(output_directory, 'final_dataset.csv'))
