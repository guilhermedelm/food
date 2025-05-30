import os
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import render, redirect
import pandas as pd
from geopy.distance import geodesic
import json
import numpy as np  

# Create your views here.
#EXCEL_PATH = os.path.join(settings.BASE_DIR, 'home', 'data', 'farmersmarket.xlsx')
#df = pd.read_excel(EXCEL_PATH)

def home(request):
    context = {}
    markets = []
    user_lat = None
    user_lon = None

    if request.method == "GET" and 'last_context' in request.session:
        context = request.session.pop('last_context')  # .pop() apaga da sessão após uso
        return render(request, 'home/home.html', context)


    if request.method == "POST":

        try:


            EXCEL_PATH = os.path.join(settings.BASE_DIR, 'home', 'data', 'csa_2025-56131011.xlsx')
            notas_path = os.path.join(settings.BASE_DIR, 'home', 'data', ' notas.xlsx')
            df_notas = pd.read_excel(notas_path)
            df = pd.read_excel(EXCEL_PATH)
            print("df passou")

            df = df.merge(df_notas, on="listing_name", how="left")
            user_lat = (request.POST.get("latitude"))
            if user_lat:
                user_lat = float(user_lat)

            user_lon = (request.POST.get("longitude"))    
            if user_lon:
                user_lon = float(user_lon)

            max_distance = (request.POST.get("max_distance"))    
            if max_distance:    
                max_distance = float(max_distance)

            food_type=(request.POST.get("food_type"))    
           
            user_location = (user_lat, user_lon)
            listing_name = request.POST.get("listing_name")  # Você pode obter isso do formulário ou contexto
            


            #remover coordenadas Nan
            df = df.dropna(subset=["location_x","location_y"])





            ''' def criar_notas(df_base):
                notas = df_base[['listing_name']].copy()
                notas['notas'] = np.round(np.random.uniform(3, 5, size=len(notas)), 1)
                notas['numero_notas'] = np.random.randint(1, 1000, size=len(notas))
                print("entrou na função")
                output_path = os.path.join(settings.BASE_DIR, 'home', 'data', ' notas.xlsx')
                notas.to_excel(output_path, index=False)
                return notas'''

            def atualizar_nota(listing_name, nova_nota,df_notas, path):
                

                # Verifica se o estabelecimento já existe
                if listing_name in df_notas['listing_name'].values:
                    idx = df_notas[df_notas['listing_name'] == listing_name].index[0]
                    nota_atual = df_notas.at[idx, 'notas']
                    num_avaliacoes = df_notas.at[idx, 'numero_notas']

                    # Recalcula média e atualiza número de avaliações
                    nova_media = round((nota_atual * num_avaliacoes + nova_nota) / (num_avaliacoes + 1), 1)
                    df_notas.at[idx, 'notas'] = nova_media
                    df_notas.at[idx, 'numero_notas'] = num_avaliacoes + 1

                else:
                    # Novo estabelecimento — adiciona
                    df_notas = df_notas.append({
                        'listing_name': listing_name,
                        'notas': round(nova_nota, 1),
                        'numero_notas': 1
                    }, ignore_index=True)

                # Salva de volta
                df_notas.to_excel(path, index=False)

            
            user_rating = request.POST.get("user_rating")
            if user_rating:
                nova_nota = float(user_rating)
                atualizar_nota(listing_name, nova_nota, df_notas, notas_path)
                return redirect('/')



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
            df["pontuacao"] = np.round(np.random.uniform(3, 5, size=len(df)),1)

            df = df.dropna(subset=["distance_km"])

            if food_type == "" :
                # Filtro por distância escolhida
                recommended_markets = df[df["distance_km"] <= max_distance].sort_values("notas")
                recommended_markets = recommended_markets.where(pd.notnull(recommended_markets), None)
                context["markets"] = recommended_markets[
                    ["listing_name", "location_address", "distance_km","products","location_y","location_x","notas"]
                ].head(10).values.tolist()
                
            
            else:
                food_type = food_type.lower()
                filtrado = df[df["products"].str.lower().str.contains(food_type, na=False)]
                print(filtrado["products"])
                recommended_markets=filtrado[filtrado["distance_km"] <= max_distance].sort_values("notas")
                recommended_markets = recommended_markets.where(pd.notnull(recommended_markets), None)
                context["markets"] = recommended_markets[["listing_name", "location_address", "distance_km","products","location_y","location_x","notas"]].head(10).values.tolist()
                print(context)    
                

        except ValueError:
            context["error"] = "Por favor, insira valores válidos."

    if user_lat is not None and user_lon is not None:
        context["latitude"] = user_lat
        context["longitude"] = user_lon

    if "markets" in context:
        context["markets_json"] = json.dumps(context["markets"])
    #print(context["markets_json"])
    request.session['last_context'] = context
    return redirect('/') 

    return render(request, 'home/home.html',context)

