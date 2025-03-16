import os
import pandas as pd
import pickle
import argparse
from helper.plantdoc import parse_plantdoc
from helper.houseplant import parse_houseplant
from helper.houseplant2 import parse_houseplant2

'''
Dataset preparation (preprocessing) for plant health classification
'''

def preprocess():
    parser = argparse.ArgumentParser(description="Prepare dataset for plant health classification.")
    parser.add_argument("--plantdoc", action="store_true", help="Include PlantDoc dataset")
    parser.add_argument("--houseplant", action="store_true", help="Include HousePlants dataset")
    parser.add_argument("--houseplant2", action="store_true", help="Include HousePlants2 dataset")
    parser.add_argument("--output", type=str, default="dataset", help="Output dataset file name")

    args = parser.parse_args()

    dataset = []

    if args.plantdoc:
        print("Including PlantDoc dataset...")
        dataset += parse_plantdoc('datasets/PlantDoc')

    if args.houseplant:
        print("Including HousePlants dataset...")
        dataset += parse_houseplant('datasets/HousePlants')
    
    if args.houseplant2:
        print("Including HousePlants2 dataset...")
        dataset += parse_houseplant2('datasets/HousePlants2')

    if not dataset:
        print("No dataset selected. Use --plantdoc or --houseplant or --houseplant2 to include datasets.")
        return

    # save the dataset as a CSV
    output_csv = os.path.join('datasets', args.output + '.csv')
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df = pd.DataFrame(dataset)
    print(f"Total samples: {len(df)}")
    df.to_csv(output_csv, index=False)
    print(f"Dataset saved to {output_csv}")

    # save the dataset as a Python dictionary using pickle
    output_dict = os.path.join('datasets', args.output + '.pkl')
    os.makedirs(os.path.dirname(output_dict), exist_ok=True)

    with open(output_dict, 'wb') as f:
        pickle.dump(dataset, f)
    print(f"Dataset saved to {output_dict}")

if __name__ == '__main__':
    preprocess()
