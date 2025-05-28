import os
from django.conf import settings
from django.shortcuts import render
import pandas as pd
from geopy.distance import geodesic
import json
from datetime import datetime

# Create your views here.
EXCEL_PATH = os.path.join(settings.BASE_DIR, 'home', 'data', 'farmersmarket.xlsx')
df = pd.read_excel(EXCEL_PATH)

def home(request):
    context = {}
    markets = []
    user_lat = None
    user_lon = None

    if request.method == "POST":

        try:

            EXCEL_PATH = os.path.join(settings.BASE_DIR, 'home', 'data', 'csa_2025-56131011.xlsx')
            df = pd.read_excel(EXCEL_PATH)
            print("df passou")

            
            user_lat = float(request.POST.get("latitude"))
            user_lon = float(request.POST.get("longitude"))
            max_distance = float(request.POST.get("max_distance"))
            food_type=(request.POST.get("food_type"))
            user_location = (user_lat, user_lon)

            #remover coordenadas Nan
            df = df.dropna(subset=["location_x","location_y"])

            
            
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

            def recomendation(planilha:pd.DataFrame,) -> pd.DataFrame:
                mes=datetime.now().month
                mes_comparado=f'month_{mes}'

                #filtra por colunas com produção no mês atual
                df_mes=planilha[planilha[mes_comparado] == 1].copy()

                #cria coluna de pontuação
                df_mes['score'] = 0
                #sistema de pontuações
                df_mes['score'] += df_mes['specialproductionmethods'].str.lower().str.contains("organic", na=False).astype(int)
                df_mes['score'] += df_mes['specialproductionmethods'].str.lower().str.contains("no hormones", na=False).astype(int)

                #ordena df_mes pela pontuação
                df_mes=df_mes.sort_values(by='score', ascending = False)

                return df_mes

                


            df = df.dropna(subset=["distance_km"])
            if food_type == "" :
                # Filtro por distância escolhida
                recommended_markets = df[df["distance_km"] <= max_distance].sort_values("distance_km")
                recommended_markets = recommended_markets.where(pd.notnull(recommended_markets), None)
                context["markets"] = recommended_markets[
                    ["listing_name", "location_address", "distance_km","products","location_y","location_x"]
                ].head(10).values.tolist()
                recomendation(recommended_markets)
            
            else:
                food_type = food_type.lower()
                filtrado = df[df["products"].str.lower().str.contains(food_type, na=False)]
                print(filtrado["products"])
                recommended_markets=filtrado[filtrado["distance_km"] <= max_distance].sort_values("distance_km")
                recommended_markets = recommended_markets.where(pd.notnull(recommended_markets), None)
                context["markets"] = recommended_markets[["listing_name", "location_address", "distance_km","products","location_y","location_x"]].head(10).values.tolist()
                print(context)
                context["recommended"]=recomendation(recommended_markets)[[]]

                
                

        except ValueError:
            context["error"] = "Por favor, insira valores válidos."

    if user_lat is not None and user_lon is not None:
        context["latitude"] = user_lat
        context["longitude"] = user_lon

    if "markets" in context:
        context["markets_json"] = json.dumps(context["markets"])
    print(context["markets_json"])




    return render(request, 'home/home.html',context)

