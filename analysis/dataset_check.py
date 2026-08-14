import pandas as pd

df = pd.read_csv(
    "data/superstore.csv",
    encoding="latin1"
)

print("Dataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 3 Rows:")
print(df.head(3).to_string())

print("\nOrder Date Sample:")
print(df["Order Date"].head(5).to_list())

print("\nShip Date Sample:")
print(df["Ship Date"].head(5).to_list())

print("\nData Types:")
print(df.dtypes)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())