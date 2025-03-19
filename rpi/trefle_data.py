''' 
This is a file to get the plant data using the trefle data
Zara Mansoor (zmansoor)

'''
import pandas as pd

def main():
  df = pd.read_csv('species.csv', delimiter='\t')
  # print(df.head())
  plant_id = input("Enter the plant ID: ")
  
  plant = df[df['id'] == int(plant_id)]
  
  if not plant.empty:
    print("Plant Information:")
    for col, value in plant.iloc[0].items():
      print(f"{col}: {value}")
  else:
    print("No plant found with that ID.")
    
if __name__ == "__main__":
  main()
