import pandas as pd
from geopy.distance import geodesic

#sample user Location
user_location=(37.7749, -122.4194)

#ler dados de farmers_market
df=pd.read_excel("farmersmarket.xlsx")

coordinates=df[["location_x","location_y"]]
print(coordinates.head())

