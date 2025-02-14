import pandas as pd
import numpy as np
import plotly.express as px
import pmdarima as pm
import statsmodels.api as sm
from xgboost import XGBRegressor
import warnings
from dash import dcc, html
import dash_bootstrap_components as dbc
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from dash.dependencies import Input, Output


warnings.filterwarnings("ignore")

# Fonction pour générer le graphique des prédictions ARIMA + XGBoost


def generate_prediction_graph():
    # Charger et préparer les données
    data = pd.read_csv('data/transport_location_velo.csv',
                       header=None, sep=';', names=['date', 'nombre'])
    data['date'] = pd.to_datetime(data['date'], format='%m/%d/%y')
    data['nombre'] = data['nombre'].astype(str).str.replace(
        '\u202f', '').str.replace(' ', '').astype(int)

    # Séparer les données en train (avant 2023) et test (après 2023)
    train_data = data[data['date'] < '2023-01-01']
    test_data = data[data['date'] >= '2023-01-01']

    # Regrouper par mois
    train_monthly = train_data.resample('M', on='date').sum()
    test_monthly = test_data.resample('M', on='date').sum()

    # Sélection automatique des paramètres ARIMA
    auto_model = pm.auto_arima(
        train_monthly['nombre'], seasonal=False, stepwise=True, suppress_warnings=True)
    p, d, q = auto_model.order

    # Entraîner ARIMA
    arima_model = sm.tsa.ARIMA(train_monthly['nombre'], order=(p, d, q))
    arima_fit = arima_model.fit()

    # Faire des prédictions avec ARIMA
    arima_predictions = arima_fit.forecast(steps=len(test_monthly))

    # Récupérer les erreurs du modèle ARIMA
    residuals = test_monthly['nombre'] - arima_predictions

    # Préparer les données pour XGBoost
    x_train = np.arange(len(train_monthly)).reshape(-1, 1)  # Temps en feature
    y_train = train_monthly['nombre']
    x_test = np.arange(len(train_monthly), len(
        train_monthly) + len(test_monthly)).reshape(-1, 1)

    # Entraîner XGBoost sur les vraies valeurs
    xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1)
    xgb_model.fit(x_train, y_train)

    # Faire des prédictions avec XGBoost
    xgb_predictions = xgb_model.predict(x_test)

    # Fusionner les prédictions ARIMA + XGBoost
    final_predictions = arima_predictions + \
        (xgb_predictions - arima_predictions) * 0.5  # Ajustement des erreurs

    # Création des DataFrames pour affichage
    df_arima = pd.DataFrame(
        {'date': test_monthly.index, 'nombre': arima_predictions})
    df_xgb = pd.DataFrame(
        {'date': test_monthly.index, 'nombre': final_predictions})

    # Visualisation interactive avec Plotly
    fig1 = px.line(train_monthly.reset_index(), x='date', y='nombre', title="Prédiction ARIMA + XGBoost vs Réalité",
                   labels={'nombre': 'Nombre de locations'}, markers=True, color_discrete_sequence=['blue'])
    fig1.add_scatter(x=test_monthly.index, y=test_monthly['nombre'],
                     mode='lines+markers', name='Données réelles', line=dict(color='green'))
    fig1.add_scatter(x=df_arima['date'], y=df_arima['nombre'], mode='lines+markers',
                     name='Prédictions ARIMA', line=dict(dash='dot', color='red'))
    fig1.add_scatter(x=df_xgb['date'], y=df_xgb['nombre'], mode='lines+markers',
                     name='Prédictions ARIMA + XGBoost', line=dict(dash='dot', color='orange'))

    return fig1

# Fonction pour générer le graphique des passagers par ligne de métro


def generate_metro_passenger_graph():
    # Charger les données
    data = pd.read_csv('data/transport_temperatures_metro.csv')

    # Création de la colonne 'Date'
    data['Date'] = pd.to_datetime(data['Year'].astype(
        str) + ' ' + data['Month'], format='%Y %B')

    # Transformation des données en format long
    data_long = data.melt(id_vars=['Date'],
                          value_vars=['Bakerloo', 'Central', 'Jubilee', 'Northern', 'Piccadilly',
                                      'Victoria', 'Waterloo_and_City', 'Sub-surface_lines'],
                          var_name='Metro Line',
                          value_name='Passenger Count')

    # Ajout des jours en tant que variable numérique
    data_long['Days'] = (data_long['Date'] - data_long['Date'].min()).dt.days

    # Encodage cyclique du mois pour capturer la saisonnalité
    data_long['Month'] = data_long['Date'].dt.month
    data_long['Month_sin'] = np.sin(2 * np.pi * data_long['Month'] / 12)
    data_long['Month_cos'] = np.cos(2 * np.pi * data_long['Month'] / 12)

    # Initialiser le graphique avec Plotly
    fig2 = px.line(data_long,
                   x='Date',
                   y='Passenger Count',
                   color='Metro Line',
                   title='Évolution du nombre de passagers par ligne de métro à Londres',
                   labels={'Passenger Count': 'Nombre de passagers',
                           'Date': 'Date'},
                   markers=True)

    # Récupérer les couleurs attribuées automatiquement par Plotly
    colors = {trace.name: trace.line.color for trace in fig2.data}

    # Initialiser le modèle XGBoost
    model = XGBRegressor(n_estimators=200, learning_rate=0.05, random_state=42)

    # Prédictions pour chaque ligne de métro
    for metro_line in data_long['Metro Line'].unique():
        # Filtrer les données de la ligne
        line_data = data_long[data_long['Metro Line'] == metro_line].copy()

        # Sélection des features
        X = line_data[['Days', 'Month_sin', 'Month_cos']]
        y = line_data['Passenger Count']

        # Standardisation des features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Entraînement du modèle
        model.fit(X_scaled, y)

        # Générer les dates futures
        future_dates = pd.date_range(
            start='2024-01-01', end='2024-12-01', freq='MS')
        future_days = (
            future_dates - data_long['Date'].min()).days.values.reshape(-1, 1)
        future_months = future_dates.month
        future_sin = np.sin(2 * np.pi * future_months / 12)
        future_cos = np.cos(2 * np.pi * future_months / 12)

        # Création du dataset de prédiction
        X_future = np.column_stack([future_days, future_sin, future_cos])
        X_future_scaled = scaler.transform(X_future)

        # Prédictions
        predicted_values = model.predict(X_future_scaled)

        # Ajouter les prédictions au graphique avec la couleur de la ligne correspondante
        fig2.add_scatter(x=future_dates,
                         y=predicted_values,
                         mode='lines',
                         # Utilisation de la bonne couleur
                         line=dict(dash='dot', color=colors[metro_line]),
                         name=f'Prévision {metro_line}')

    return fig2

# Fonction pour générer le graphique de l'excès de poids en fonction de la ville sélectionnée


def generate_weight_prediction_graph(selected_area):
    # Chargement des données d'excès de poids
    file_path = "data/His indicators update Nov 2024 FINAL.xlsx"
    weight_df = pd.read_excel(
        file_path, sheet_name="5. Excess weight age 10-11")

    # Suppression des valeurs NaN
    weight_df.dropna(subset=["Value"], inplace=True)

    # Filtrage pour la ville sélectionnée
    filtered_df = weight_df[weight_df["Area Name"] == selected_area].copy()

    # Conversion des périodes en format numérique (ex: "2006/07" → 2006.5)
    def convert_period(period):
        start_year = int(period.split("/")[0])
        return start_year + 0.5

    filtered_df["Year"] = filtered_df["Time Period"].apply(convert_period)

    # Préparation des données pour la régression
    X = filtered_df["Year"].values.reshape(-1, 1)
    y = filtered_df["Value"].values

    # Entraînement du modèle de régression linéaire
    model = LinearRegression()
    model.fit(X, y)

    # Mapping des périodes futures
    year_mapping = {"2022/23": 2022.5, "2023/24": 2023.5}
    future_periods = ["2022/23", "2023/24"]
    future_years = np.array([year_mapping[p]
                            for p in future_periods]).reshape(-1, 1)

    # Prédictions pour les périodes futures
    future_predictions = model.predict(future_years)

    # Création du graphique
    fig = go.Figure()

    # Ajouter les données historiques
    fig.add_trace(go.Scatter(
        x=filtered_df["Year"],
        y=filtered_df["Value"],
        mode='lines+markers',
        name=selected_area,
        line=dict(color='red')
    ))

    # Ajouter les prédictions
    fig.add_trace(go.Scatter(
        x=[year_mapping[p] for p in future_periods],
        y=future_predictions,
        mode='markers+lines',
        name="Prédictions",
        line=dict(color='blue', dash='dot'),
        marker=dict(size=10, symbol="star")
    ))

    # Filtrer et ajouter les vraies données futures si elles existent
    actual_data = filtered_df[filtered_df["Time Period"].isin(
        future_periods)].copy()
    actual_data["Year"] = actual_data["Time Period"].map(year_mapping)

    if not actual_data.empty:
        fig.add_trace(go.Scatter(
            x=actual_data["Year"],
            y=actual_data["Value"],
            mode='lines+markers',
            name="Données réelles",
            line=dict(color='green'),
            marker=dict(size=8)
        ))

    # Mise en forme du graphique
    fig.update_layout(
        title=f"Évolution et prévisions de l'excès de poids à {selected_area}",
        xaxis_title='Période',
        yaxis_title='Excès de poids (%)',
        template="plotly_white"
    )

    return fig

# Liste des villes disponibles dans les données


def get_available_areas():
    file_path = "data/His indicators update Nov 2024 FINAL.xlsx"
    weight_df = pd.read_excel(
        file_path, sheet_name="5. Excess weight age 10-11")
    return weight_df["Area Name"].unique()


layout = dbc.Container([
    dbc.Button("⬅ Retour à l'accueil", href="/", color="primary", className="mb-3"),
    html.H2("Prédictions et clustering", className="text-center mb-4"),

    # Graphique des prédictions ARIMA + XGBoost
    dbc.Card([
        dbc.CardHeader(html.H3("Prédictions des locations de vélos")),
        dbc.CardBody([
            dcc.Graph(id='predictions-graph', figure=generate_prediction_graph())
        ])
    ], className="mb-4"),

    # Carte pour le graphique du nombre de passagers par ligne de métro
    dbc.Card([
        dbc.CardHeader(html.H3("Prédictions du nombre de passagers par ligne de métro")),
        dbc.CardBody([
            dcc.Graph(id='metro-passenger-graph', figure=generate_metro_passenger_graph())
        ])
    ], className="mb-4"),

    # Graphique des prédictions de l'excès de poids
    dbc.Card([
        dbc.CardHeader(html.H3("Prédictions de l'excès de poids par quartier")),
        html.Div([
            html.Label("Sélectionnez une ville:"),
            dcc.Dropdown(
                id="city-dropdown",
                options=[{'label': area, 'value': area} for area in get_available_areas()],
                value="Barnet",  # Valeur initiale
                clearable=False,
                style={'width': '50%', 'margin': 'auto'}
            )
        ], className="mb-4"),
        dbc.CardBody([dcc.Graph(id='weight-predictions-graph')])
    ], className="mb-4"),

    # Ajout de la carte sauvegardée en HTML
    html.Div([
        html.H3("Carte des clusters de Londres"),
        html.Iframe(
            src='/static/london_clusters_map.html',
            width="100%",
            height="600px",
            style={"border": "none"}
        )
    ], className="mt-4")

], fluid=True)



def register_callbacks(app):
    # Callback pour mettre à jour le graphique de l'excès de poids en fonction de la ville sélectionnée
    @app.callback(
        Output('weight-predictions-graph', 'figure'),
        [Input('city-dropdown', 'value')]
    )
    def update_graph(selected_area):
        return generate_weight_prediction_graph(selected_area)
