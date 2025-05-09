import os
from django.conf import settings
from django.shortcuts import render
import pandas as pd
from geopy.distance import geodesic


# Create your views here.
EXCEL_PATH = os.path.join(settings.BASE_DIR, 'markets', 'data', 'farmersmarket.xlsx')
df = pd.read_excel(EXCEL_PATH)


def home(request):
    context={}

    if request.method == "POST":
    
        try:
            user_lat = float(request.POST.get("latitude"))
            user_lon = float(request.POST.get("longitude"))
            user_location = (user_lat,user_lon)
            
            #calcula distância douser_location até o local inserido
            def calculate_distance(location_x,location_y):
                try:
                    market_location = (float(location_y), float(location_x))
                    return geodesic(user_location, market_location).km
                except ValueError:
                    return None
            
            #Aplica calculate_distace para cada nó
            df["distance_km"] = df.apply(lambda row:calculate_distance(row["location_x"],row["location_y"]),axis=1)
            print(df["distance_km"].head())
            
            #aplica filtro à distância
            def filtro_distancia(distance):
                recommended_markets = df[df["distance_km"] <= distance].sort_values("distance_km")
                return recommended_markets[["listing_name", "location_address", "distance_km"]].head()
        except:
            context["error"] = "Por favor, insira coordenadas válidas."    
    return render(request, "markets/home.html", context)
