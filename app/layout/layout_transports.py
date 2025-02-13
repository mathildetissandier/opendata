import os
import pandas as pd
from dash import dcc, html, callback, Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import callback_context

# === Chargement des données pour le premier graphique (CSV) ===
# Chemin du dossier contenant les fichiers CSV
dossier = 'data/transport_vehicules._autorisés'
fichiers_csv = [f for f in os.listdir(dossier) if f.endswith('.csv')]

# Liste pour stocker tous les DataFrames
dataframes = []

# Parcourir chaque fichier CSV et l'ouvrir avec pd.read_csv
for fichier in fichiers_csv:
    annee = fichier.split('.')[0]  # Extraire l'année du nom du fichier
    chemin_fichier = os.path.join(dossier, fichier)
    df = pd.read_csv(chemin_fichier, sep=';')
    df['Année'] = annee  # Ajouter l'année en colonne
    dataframes.append(df)

# Fusionner tous les DataFrames en un seul
df_total = pd.concat(dataframes, ignore_index=True)

# Liste des quartiers disponibles
quartiers = df_total['Area'].unique()
quartiers = [q for q in quartiers if q not in [None, 'London', 'UnknownBorough'] and pd.notna(q)]
options_quartiers = [{'label': q, 'value': q} for q in quartiers]

# === Chargement des données pour le deuxième graphique (Excel) ===
xls = pd.ExcelFile('data/transport_vehicules_autorises_2.xls')

# Charger les feuilles sauf la première
sheets_to_load = xls.sheet_names[1:]  
sheets_dict = {sheet: pd.read_excel(xls, sheet_name=sheet).drop(index=0) for sheet in sheets_to_load}

# Renommer les colonnes pour supprimer les espaces inutiles
dfs_par_annee = {year: df.rename(columns=lambda x: x.strip()) for year, df in sheets_dict.items()}

# Récupérer les noms de colonnes de référence (2023)
reference_columns = dfs_par_annee['2023'].columns
years = sorted(dfs_par_annee.keys())

# Liste des Local Authorities à garder
valid_areas = [
    "City of London", "Barking and Dagenham", "Barnet", "Bexley", "Brent", "Bromley",
    "Camden", "Croydon", "Ealing", "Enfield", "Greenwich", "Hackney",
    "Hammersmith and Fulham", "Haringey", "Harrow", "Havering", "Hillingdon", "Hounslow",
    "Islington", "Kensington and Chelsea", "Kingston upon Thames", "Lambeth", "Lewisham",
    "Merton", "Newham", "Redbridge", "Richmond upon Thames", "Southwark", "Sutton",
    "Tower Hamlets", "Waltham Forest", "Wandsworth", "Westminster"
]

# Récupérer les Local Authorities valides
all_areas = dfs_par_annee['2023']['Local Authority'].dropna().unique()
areas = [str(a).strip() for a in all_areas if str(a).strip() in valid_areas]

# Catégories de véhicules
vehicle_categories = ['Cars', 'Motor cycles', 'Light goods', 'Heavy goods', 'Buses and coaches', 'Other vehicles']

data=pd.read_csv('data/transport_bus_passager_par_route.csv',sep=';')
df = pd.DataFrame(data)


df_melted = df.melt(id_vars=["Route"], var_name="Année", value_name="Valeur")
df_melted["Valeur"] = df_melted["Valeur"].astype(str)  # Convertir en chaînes de caractères
df_melted["Valeur"] = df_melted["Valeur"].str.replace(" ", "")  # Retirer les espaces
df_melted["Valeur"] = pd.to_numeric(df_melted["Valeur"], errors='coerce')  # Convertir en int

layout = dbc.Container([
    dbc.Button("⬅ Retour à l'accueil", href="/", color="primary", className="mb-3"),
    html.H2("Évolution des moyens de transport à Londres", className="text-center mb-4"),

    # Premier graphique (données CSV) : Sélection du quartier
    html.Div([
        html.Label("Sélectionnez un quartier"),
        dcc.Dropdown(
            id='quartier-dropdown',
            options=options_quartiers,
            value=quartiers[0] if quartiers else None,
            style={'width': '50%', 'padding': '3px'}
        ),
        dcc.Graph(id='transport-graph')  # Utilisation de l'ID transport-graph
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

    # Deuxième graphique (données Excel) : Sélection de la Local Authority et catégories de véhicules
    html.Div([
        html.Label("Sélectionnez une Local Authority :"),
        dcc.Dropdown(
            id='area-dropdown',
            options=[{'label': str(area), 'value': str(area)} for area in areas],
            value=areas[0] if areas else None,
            style={'width': '50%'}
        ),

        html.Label("Sélectionnez une ou plusieurs catégories de véhicules :"),
        dcc.Dropdown(
            id='vehicle-dropdown',
            options=[{'label': category, 'value': category} for category in vehicle_categories],
            value=[vehicle_categories[0]],
            multi=True,
            style={'width': '50%'}
        )
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

    # Graphique des données d'évolution avec sélection de la Local Authority
    html.Div([
        dcc.Graph(id='evolution-graph')  # Utilisation de l'ID evolution-graph
    ], style={'padding': '10px', 'border': '1px solid #ccc'}),

    # Troisième graphique (données de location de vélos) : Sélection de la route
    html.Div([
        html.H3("Évolution des locations de vélos par mois"),
        dcc.Graph(id='bike-rentals-graph')  # Utilisation de l'ID bike-rentals-graph
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-top': '20px'}),

    # Quatrième graphique (température des lignes de métro) : Graphique de la température des lignes de métro
    html.Div([
        html.H3("Évolution de la température moyenne par ligne de métro à Londres"),
        dcc.Graph(id='metro-temp-graph')  # Utilisation de l'ID metro-temp-graph
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-top': '20px'}),

    # Cinquième graphique (sélection de la route) : Graphique pour la route
    html.Div([
        html.Label("Sélectionnez une Route :"),
        dcc.Dropdown(
            id='route-dropdown',
            options=[{'label': f"Route {route}", 'value': route} for route in df["Route"].unique()],
            value=df["Route"].unique()[0],  # Route sélectionnée par défaut
            style={'width': '50%', 'padding': '3px'}
        ),
        dcc.Graph(id='route-graph')  # Utilisation de l'ID route-graph
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'})
], fluid=True)

# === Callbacks ===

# Callback pour le premier graphique
@callback(
    Output('transport-graph', 'figure'),
    [Input('quartier-dropdown', 'value')]
)
def update_transport_graph(selected_quartier):
    df_filtered = df_total[df_total['Area'] == selected_quartier]
    fig = go.Figure()

    for col in ['PLGCars:Company', 'PLGCars:Private', 'PLGOther:Company', 'PLGOther:Private', 
                'PLGTotal', 'ExemptDisabled:Cars', 'ExemptDisabled:Other']:
        fig.add_trace(go.Scatter(
            x=df_filtered['Année'],
            y=df_filtered[col],
            mode='lines',
            name=col
        ))

    fig.update_layout(
        title=f"Évolution des moyens de transport à {selected_quartier} par année",
        xaxis_title='Année',
        yaxis_title='Nombre de véhicules',
        legend_title='Type de transport'
    )
    return fig

dfs_par_annee = {year: df.rename(columns=lambda x: x.strip()) for year, df in sheets_dict.items() if year not in ['1994 regions only', '2004', '2009', '2010', '2011', '2012', '2013']}
years = sorted(dfs_par_annee.keys())

# Callback pour le deuxième graphique
@callback(
    Output('evolution-graph', 'figure'),
    [Input('area-dropdown', 'value'),
     Input('vehicle-dropdown', 'value')]
)
def update_evolution_graph(selected_area, selected_vehicles):
    if not selected_area or not selected_vehicles:
        return go.Figure()  # Graphique vide si aucune sélection

    fig = go.Figure()

    for vehicle in selected_vehicles:
        evolution_data = []

        for year in years:
            df = dfs_par_annee.get(year, pd.DataFrame())

            # Choisir la colonne appropriée en fonction de l'année
            if year == 2009:
                area_column = 'Region/local authority'  # Colonne spécifique pour 2009
            else:
                area_column = 'Local Authority'  # Colonne générale

            # Vérifier si la colonne existe pour l'année en cours
            if area_column not in df.columns:
                print(f"Erreur : La colonne '{area_column}' est manquante pour l'année {year}.")
                continue

            # Filtrer les données pour la Local Authority sélectionnée
            area_data = df[df[area_column] == selected_area]
            
            # Extraire la valeur pour le véhicule sélectionné
            value = area_data[vehicle].values[0] if not area_data.empty else 0
            evolution_data.append(value)

        # Ajouter les données au graphique
        fig.add_trace(go.Scatter(
            x=years,
            y=evolution_data,
            mode='lines+markers',
            name=vehicle
        ))

    # Mise en forme du graphique
    fig.update_layout(
        title=f'Évolution des véhicules pour {selected_area}',
        xaxis_title='Année',
        yaxis_title='Nombre de véhicules',
        hovermode='x unified'
    )

    return fig

# Callback pour le troisième graphique
@callback(
    Output('bike-rentals-graph', 'figure'),
    [Input('bike-rentals-graph', 'id')]  # Ce callback peut être déclenché indépendamment
)
def update_bike_rentals_graph(_):
    # Lecture du fichier CSV pour les locations de vélos
    data = pd.read_csv('data/transport_location_velo.csv', header=None, sep=';', names=['date', 'nombre'])

    # Conversion de la colonne date en datetime
    data['date'] = pd.to_datetime(data['date'], format='%m/%d/%y')

    # Nettoyage de la colonne 'nombre'
    data['nombre'] = data['nombre'].astype(str).str.replace('\u202f', '').str.replace(' ', '').astype(int)

    # Regroupement par mois
    data_monthly = data.resample('M', on='date').sum().reset_index()

    # Création du graphique interactif
    fig = px.line(data_monthly, 
                  x='date', 
                  y='nombre', 
                  title="Évolution des locations de vélos par mois",
                  labels={'date': 'Date', 'nombre': 'Nombre de locations'},
                  markers=True)

    # Personnalisation de l'affichage
    fig.update_traces(hovertemplate='%{y} locations')  # Affichage précis au survol
    fig.update_layout(hovermode='x unified', showlegend=False)

    return fig

# Callback pour le quatrième graphique (température des lignes de métro)
@callback(
    Output('metro-temp-graph', 'figure'),
    [Input('metro-temp-graph', 'id')]
)
def update_metro_temp_graph(_):
    # Lecture du fichier CSV pour les températures du métro
    data = pd.read_csv('data/transport_temperatures_metro.csv')

    # Créer une colonne 'Date' combinant Year et Month
    data['Date'] = pd.to_datetime(data['Year'].astype(str) + ' ' + data['Month'], format='%Y %B')

    # Transformer les données pour qu'elles soient sous une forme longue (long format)
    data_long = data.melt(id_vars=["Date"], 
                          value_vars=["Bakerloo", "Central", "Jubilee", "Northern", "Piccadilly", "Victoria", "Waterloo_and_City", "Sub-surface_lines"],
                          var_name="Metro Line", 
                          value_name="Passenger Count")

    # Créer le graphique interactif
    fig = px.line(data_long, 
                  x='Date', 
                  y='Passenger Count', 
                  color='Metro Line', 
                  title="Evolution de la température moyenne par ligne de métro à Londres",
                  labels={'Passenger Count': 'Température moyenne', 'Date': 'Date'},
                  markers=True)

    # Affichage du graphique
    return fig

@callback(
    Output('route-graph', 'figure'),
    [Input('route-dropdown', 'value')],
    allow_duplicate=True
)
def update_route_graph(selected_route):
    df_filtered = df_melted[df_melted["Route"] == selected_route]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_filtered["Année"],
        y=df_filtered["Valeur"],
        mode='lines+markers',
        name=f"Route {selected_route}",
        hovertemplate='%{y} véhicules<br>Année: %{x}<extra></extra>',
    ))

    fig.update_layout(
        title=f'Évolution du trafic pour la Route {selected_route}',
        xaxis_title='Année',
        yaxis_title='Nombre de véhicules',
        yaxis=dict(
            range=[df_filtered["Valeur"].min() * 0.95, df_filtered["Valeur"].max() * 1.05],
        ),
        hovermode='x unified'
    )

    return fig
