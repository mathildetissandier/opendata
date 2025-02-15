import os
import pandas as pd
from dash import dcc, html, callback, Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import callback_context, no_update
import folium
import geopandas as gpd
import branca
import geopandas as gpd
import folium
import branca

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

df_total['Année'] = pd.to_numeric(df_total['Année'], errors='coerce')

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

# === Chargement des données pour la carte ===
df_ponts = pd.read_csv('data/transport_restriction_ponts.csv', sep=';')
df_ponts['Lat'] = df_ponts['Lat'].apply(lambda x: float(str(x).replace(',', '.')))
df_ponts['Lng'] = df_ponts['Lng'].apply(lambda x: float(str(x).replace(',', '.')))

# Groupby par borough pour compter le nombre de ponts
ponts_par_borough = df_ponts.groupby('Borough').size().reset_index(name='Number of Bridges')

# Charger le fichier GeoJSON des boroughs de Londres
gdf = gpd.read_file('data/london_boroughs.geojson')

map_files = {
    "Polygones": "polygons_map.html",
    "Markers": "markers_map.html"
}

maps_borough = {'Barking and Dagenham': 'maps/Barking and Dagenham_map.html',
 'Barnet': 'maps/Barnet_map.html',
 'Bexley': 'maps/Bexley_map.html',
 'Brent': 'maps/Brent_map.html',
 'Bromley': 'maps/Bromley_map.html',
 'Camden': 'maps/Camden_map.html',
 'City of London': 'maps/City of London_map.html',
 'Croydon': 'maps/Croydon_map.html',
 'Ealing': 'maps/Ealing_map.html',
 'Enfield': 'maps/Enfield_map.html',
 'Greenwich': 'maps/Greenwich_map.html',
 'Hackney': 'maps/Hackney_map.html',
 'Hammersmith and Fulham': 'maps/Hammersmith and Fulham_map.html',
 'Haringey': 'maps/Haringey_map.html',
 'Harrow': 'maps/Harrow_map.html',
 'Havering': 'maps/Havering_map.html',
 'Hillingdon': 'maps/Hillingdon_map.html',
 'Hounslow': 'maps/Hounslow_map.html',
 'Islington': 'maps/Islington_map.html',
 'Kensington and Chelsea': 'maps/Kensington and Chelsea_map.html',
 'Kingston upon Thames': 'maps/Kingston upon Thames_map.html',
 'Lambeth': 'maps/Lambeth_map.html',
 'Lewisham': 'maps/Lewisham_map.html',
 'Merton': 'maps/Merton_map.html',
 'Newham': 'maps/Newham_map.html',
 'Redbridge': 'maps/Redbridge_map.html',
 'Richmond upon Thames': 'maps/Richmond upon Thames_map.html',
 'Southwark': 'maps/Southwark_map.html',
 'Sutton': 'maps/Sutton_map.html',
 'Tower Hamlets': 'maps/Tower Hamlets_map.html',
 'Waltham Forest': 'maps/Waltham Forest_map.html',
 'Wandsworth': 'maps/Wandsworth_map.html',
 'Westminster': 'maps/Westminster_map.html'}

### premier graphique 

# Exempté : Les personnes handicapées sont des véhicules exonérés d'impôt à condition qu'ils soient utilisés par des personnes 
# handicapées réclamant le taux de mobilité plus élevé de la composante de l'allocation de subsistance pour personnes handicapées, 
# du supplément de mobilité des retraités de guerre ou ayant un véhicule invalide. Ce n'est pas la même chose que les badges 
# de stationnement pour handicapés.
#PLG : Véhicule privé ou léger (à l'exclusion des marchandises lourdes, des bus et des autocars).

### deuxième graphique

# Les véhicules sont attribués à une autorité locale en fonction du code postal du dépositaire enregistré. Il s'agit de 
# l'adresse du gardien pour les véhicules privés ou de l'adresse enregistrée de l'entreprise pour les véhicules appartenant 
# à la société. Des changements importants dans le nombre de véhicules d'une année à l'autre peuvent souvent se produire 
# lorsqu'une entreprise ayant un grand nombre de véhicules change son adresse enregistrée.
#Les autres véhicules comprennent les pelles arrière, les chariots élévateurs, les rouleaux, les ambulances, les chariots Hackney, les trois-roues et les véhicules agricoles.

### cinquième graphique

# Millions de véhicules parcourus par tous les véhicules à moteur et toutes les voitures à Londres. Les données proviennent de 
# l'Enquête nationale sur le trafic routier du ministère des Transports (DFT).

# Layout complet avec boutons "Analyse" et modals pour chaque graphique
# === Layout complet avec boutons "Analyse" et modals pour chaque graphique ===
layout = dbc.Container([
    dbc.Button("⬅ Retour à l'accueil", href="/", color="primary", className="mb-3"),
    html.H2("Les transports", className="text-center mb-4"),

    # === Premier graphique ===
    html.Div([
        html.H3("Tendances du nombre total de véhicules de marchandises privées ou légères à la fin de l'année depuis 1997"),
        html.Label("Sélectionnez un quartier"),
        dcc.Dropdown(
            id='quartier-dropdown',
            options=options_quartiers,
            value=quartiers[0] if quartiers else None,
            style={'width': '50%', 'padding': '3px', 'color': 'black'}
        ),
        dbc.Button("Analyse", id="open-analysis-button-1", color="info", className="mb-3"),
        dcc.Graph(id='transport-graph'),
        
        # Modal pour le premier graphique
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Analyse du graphique 1")),
            dbc.ModalBody(id="analysis-content-1"),
            dbc.ModalFooter(dbc.Button("Fermer", id="close-analysis-button-1", className="ms-auto")),
        ], id="analysis-modal-1", size="lg", is_open=False),
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

    # === Deuxième graphique ===
    html.Div([
        html.H3("Nombre de véhicules immatriculés (en milliers) à la fin de l'année ventilés par type, y compris les voitures, les motos, les marchandises légères, les marchandises lourdes, les autobus et les autocars, et autres"),
        html.Label("Sélectionnez un quartier :"),
        dcc.Dropdown(
            id='area-dropdown',
            options=[{'label': str(area), 'value': str(area)} for area in areas],
            value=areas[0] if areas else None,
            style={'width': '50%', 'color': 'black'}
        ),
        html.Label("Sélectionnez une ou plusieurs catégories de véhicules :"),
        dcc.Dropdown(
            id='vehicle-dropdown',
            options=[{'label': category, 'value': category} for category in vehicle_categories],
            value=[vehicle_categories[0]],
            multi=True,
            style={'width': '50%', 'color': 'black'}
        ),
        dbc.Button("Analyse", id="open-analysis-button-2", color="info", className="mb-3"),
        dcc.Graph(id='evolution-graph'),
        
        # Modal pour le deuxième graphique
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Analyse du graphique 2")),
            dbc.ModalBody(id="analysis-content-2"),
            dbc.ModalFooter(dbc.Button("Fermer", id="close-analysis-button-2", className="ms-auto")),
        ], id="analysis-modal-2", size="lg", is_open=False),
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

    # === Graphique des locations de vélos (Bike Rentals) ===
    html.Div([
        html.H3("Évolution des locations de vélos par mois"),
        dbc.Button("Analyse", id="open-analysis-button-3", color="info", className="mb-3"),
        dcc.Graph(id='bike-rentals-graph'),
        
        # Modal pour le graphique des locations de vélos
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Analyse du graphique 3")),
            dbc.ModalBody(id="analysis-content-3"),
            dbc.ModalFooter(dbc.Button("Fermer", id="close-analysis-button-3", className="ms-auto")),
        ], id="analysis-modal-3", size="lg", is_open=False),
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

     # === Graphique des températures du métro (Metro Temp) ===
    html.Div([
        html.H3("Évolution de la température moyenne par ligne de métro à Londres"),
        dbc.Button("Analyse", id="open-analysis-button-4", color="info", className="mb-3"),
        dcc.Graph(id='metro-temp-graph'),
        
        # Modal pour le graphique des températures du métro
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Analyse du graphique 4")),
            dbc.ModalBody(id="analysis-content-4"),
            dbc.ModalFooter(dbc.Button("Fermer", id="close-analysis-button-4", className="ms-auto")),
        ], id="analysis-modal-4", size="lg", is_open=False),
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

    # === Transport Public Graph ===
    html.Div([
        html.H3("Nombre de trajets sur le réseau de transport public par mois, par type de transport"),
        dbc.Button("Analyse", id="open-analysis-button-5", color="info", className="mb-3"),
        dcc.Graph(id='transport-public-graph'),
        
        # Modal pour le graphique transport public
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Analyse du graphique 5")),
            dbc.ModalBody(id="analysis-content-5"),
            dbc.ModalFooter(dbc.Button("Fermer", id="close-analysis-button-5", className="ms-auto")),
        ], id="analysis-modal-5", size="lg", is_open=False),
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

    # === Cinquième graphique ===
    html.Div([
        html.H3("Volume de trafic estimé pour les voitures et tous les véhicules par autorité locale depuis 1993 (kilomètres)"),
        html.Label("Sélectionnez une Route :"),
        dcc.Dropdown(
            id='route-dropdown',
            options=[{'label': f"Route {route}", 'value': route} for route in df["Route"].unique()],
            value=df["Route"].unique()[0],
            style={'width': '50%', 'padding': '3px', 'color': 'black'}
        ),
        dbc.Button("Analyse", id="open-analysis-button-5", color="info", className="mb-3"),
        dcc.Graph(id='route-graph'),
        
        # Modal pour le cinquième graphique
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Analyse du graphique 5")),
            dbc.ModalBody(id="analysis-content-5"),
            dbc.ModalFooter(dbc.Button("Fermer", id="close-analysis-button-5", className="ms-auto")),
        ], id="analysis-modal-5", size="lg", is_open=False),
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

    # === Carte Folium ===
html.Div([
    html.H3("Ponts, tunnels, barrières routières - restrictions de hauteur"),
    html.H3("Sélectionnez le type de carte :"),
    dcc.Dropdown(
        id='map-type-dropdown',
        options=[
            {'label': 'Carte avec Polygones', 'value': 'Polygones'},
            {'label': 'Carte avec Marqueurs', 'value': 'Markers'}
        ],
        value='Polygones',
        style={'width': '50%', 'color': 'black'}
    ),
    # Dropdown pour choisir le borough, visible seulement lorsque "Polygones" est sélectionné
    html.Div([
        html.H3("Sélectionnez un quartier :"),
        dcc.Dropdown(
            id='borough-dropdown',
            options=[
                {'label': borough, 'value': borough} for borough in maps_borough.keys()
            ],
            value=None,
            style={'width': '50%', 'color': 'black'}
        ),
    ], id='borough-dropdown-container', style={'display': 'none'}),
    
    # Bouton "Analyse" pour la carte
    dbc.Button("Analyse", id="open-analysis-button-7", color="info", className="mb-3"),
    
    # Carte Folium
    html.Iframe(
        id='carte-iframe',
        srcDoc=open(f'static/{map_files["Polygones"]}', 'r').read(),
        style={'width': '100%', 'height': '600px', 'border': 'none'}
    ),
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Analyse du graphique 7")),
        dbc.ModalBody(id="analysis-content-7"),
        dbc.ModalFooter(dbc.Button("Fermer", id="close-analysis-button-7", className="ms-auto")),  # Corrigé ici
    ], id="analysis-modal-7", size="lg", is_open=False),
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-top': '20px'}),


], fluid=True)

# === Callbacks ===

# Callback pour le premier graphique
@callback(
    Output('transport-graph', 'figure'),
    [Input('quartier-dropdown', 'value')]
)
def update_transport_graph(selected_quartier):
    df_filtered = df_total[df_total['Area'] == selected_quartier]

    # Trier les données par année
    df_filtered = df_filtered.sort_values(by='Année')

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
        title=f"Évolution du nombre de véhicules autorisés dans le quartier : {selected_quartier} par année",
        xaxis_title='Année',
        yaxis_title='Nombre de véhicules',
        legend_title='Type de transport',
        template='plotly_dark'
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
        hovermode='x unified',
        template='plotly_dark'
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
    fig.update_layout(hovermode='x unified', showlegend=False, template='plotly_dark')

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
    fig.update_layout(template='plotly_dark')

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
        hovermode='x unified',
        template='plotly_dark'
    )

    return fig

@callback(
    [Output('carte-iframe', 'srcDoc'),
     Output('borough-dropdown-container', 'style')],
    [Input('map-type-dropdown', 'value'),
     Input('borough-dropdown', 'value')]
)
def update_map(map_type, borough):
    # Si "Polygones" est sélectionné, afficher le dropdown des boroughs
    if map_type == 'Polygones':
        dropdown_style = {'display': 'block'}  # Afficher le dropdown pour choisir le borough
    else:
        dropdown_style = {'display': 'none'}  # Cacher le dropdown pour les autres types de carte
    
    # Si un borough est sélectionné, afficher la carte spécifique pour ce borough
    if map_type == 'Polygones' and borough:
        file_path = f"static/{maps_borough.get(borough, 'maps/Default_map.html')}"
    else:
        # Afficher la carte de type "Markers" ou la carte par défaut des Polygones
        file_path = f"static/{map_files.get(map_type, 'polygons_map.html')}"
    
    # Lire le fichier HTML et retourner son contenu
    with open(file_path, 'r') as file:
        map_html = file.read()
    
    return map_html, dropdown_style

@callback(
    Output('transport-public-graph', 'figure'),
    [Input('transport-public-graph', 'id')]
)

def transport_public(_):
    xls = pd.ExcelFile('data/transport_public.xlsx')
    transport = pd.read_excel(xls, sheet_name=1)
    transport = transport.dropna()
    transport['All operator journeys (m)'] = (
        transport['DLR Journeys (m)'] + 
        transport['Tram Journeys (m)'] + 
        transport['Overground Journeys (m)'] + 
        transport['London Cable Car Journeys (m)'] + 
        transport['TfL Rail Journeys (m)']
    )
    transport['Period beginning'] = pd.to_datetime(transport['Period beginning'])
    df_long = transport.melt(id_vars=['Period beginning'], 
                             value_vars=['Bus journeys (m)', 'Underground journeys (m)', 'All operator journeys (m)'], 
                             var_name='Transport Type', 
                             value_name='Journeys (millions)')
    
    fig = px.line(df_long, 
                  x='Period beginning', 
                  y='Journeys (millions)', 
                  color='Transport Type', 
                  title='Nombre de trajets sur le réseau de transport public par mois, par type de transport',
                  labels={'Period beginning': 'Période de début', 'Journeys (millions)': 'Nombre de trajets (millions)'})
    
    fig.update_traces(mode='lines+markers', hovertemplate='%{y} millions')  # Affichage des valeurs au survol
    
    # Mettre à jour les titres des axes
    fig.update_layout(
        hovermode='x unified',
        showlegend=True,
        xaxis_title='Temps',  # Titre pour l'axe X
        yaxis_title='Millions' , # Titre pour l'axe Y
        template='plotly_dark'
    )
    
    return fig

for i in range(1, 8):  # 5 graphiques => 5 modals
    @callback(
        [Output(f"analysis-modal-{i}", "is_open"),
         Output(f"analysis-content-{i}", "children")],
        [Input(f"open-analysis-button-{i}", "n_clicks"),
         Input(f"close-analysis-button-{i}", "n_clicks")],
        prevent_initial_call=True
    )
    def toggle_modal(open_clicks, close_clicks, i=i):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == f"open-analysis-button-{i}":
            # Retourner le contenu de l'analyse pour le graphique correspondant
            analysis_text = f"Description spécifique pour le graphique {i}."
            return True, analysis_text
        elif button_id == f"close-analysis-button-{i}":
            return False, no_update
        return no_update, no_update