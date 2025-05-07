import pandas as pd
from geopy.distance import geodesic

#sample user Location
user_location=(37.7749, -122.4194)

#ler dados de farmers_market
df=pd.read_excel("farmersmarket.xlsx")

coordinates=df[["location_x","location_y"]]
#print(coordinates.head())

#calcular a distancia entre o usuario e o mercado
def calculate_distance(location_x,location_y):
    try:
        market_location = (float(location_y), float(location_x))
        return geodesic(user_location, market_location).km
    except ValueError:
        return None

   

#Aplicar distância a cada linha do DataFrame
df["distance_km"] = df.apply(lambda row:calculate_distance(row["location_x"],row["location_y"]),axis=1)
print(df["distance_km"].head())

#Filtros
def filtro_distancia(distance):
    recommended_markets = df[df["distance_km"] <= distance].sort_values("distance_km")
    return recommended_markets[["listing_name", "location_address", "distance_km"]].head()


print(filtro_distancia(20))