import os
from django.conf import settings
from django.shortcuts import render
import pandas as pd
from geopy.distance import geodesic
from django.http import HttpResponse


# Create your views here.
EXCEL_PATH = os.path.join(settings.BASE_DIR, 'home', 'data', 'farmersmarket.xlsx')
df = pd.read_excel(EXCEL_PATH)
print("df passou")

def home(request):
    context = {}

    if request.method == "POST":
        print("aaaaaaaaaaa")

        try:
            EXCEL_PATH = os.path.join(settings.BASE_DIR, 'home', 'data', 'farmersmarket.xlsx')
            df = pd.read_excel(EXCEL_PATH)
            print("df passou")


            user_lat = float(request.POST.get("latitude"))
            user_lon = float(request.POST.get("longitude"))
            max_distance = float(request.POST.get("max_distance"))
            user_location = (user_lat, user_lon)

            # Cálculo de distância
            def calculate_distance(location_x, location_y):
                try:
                    market_location = (float(location_y), float(location_x))  # latitude, longitude
                    return geodesic(user_location, market_location).km
                except:
                    return None

            df["distance_km"] = df.apply(
                lambda row: calculate_distance(row["location_x"], row["location_y"]),
                axis=1
            )

            # Filtro por distância escolhida
            recommended_markets = df[df["distance_km"] <= max_distance].sort_values("distance_km")
            context["markets"] = recommended_markets[
                ["listing_name", "location_address", "distance_km"]
            ].head(10).values.tolist()

        except ValueError:
            context["error"] = "Por favor, insira valores válidos."

    print("aaaa")
    return render(request, 'home/home.html',context)

