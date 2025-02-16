import os
import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Chargement des données
average_price = pd.read_excel("data/Average price.xlsx")
sales_volume = pd.read_csv("data/Sales Volume.csv", delimiter=";")
vacants = pd.read_excel("data/vacants.xlsx")
affordability = pd.read_excel("data/affordability.xlsx") 

average_price2 = pd.read_excel("data/average_price2.xlsx")
sales_volume2 = pd.read_excel("data/sales_volume2.xlsx")
crimes2 = pd.read_excel("data/crimes2.xlsx")

average_price2 = average_price2[(average_price2["Year"] >= 2010) & (average_price2["Year"] <= 2023)]
sales_volume2 = sales_volume2[(sales_volume2["Year"] >= 2010) & (sales_volume2["Year"] <= 2023)]
vacants2 = vacants[(vacants["Year"] >= 2010) & (vacants["Year"] <= 2023)]
crimes2 = crimes2[(crimes2["Year"] >= 2010) & (crimes2["Year"] <= 2023)]
affordability2 = affordability[(affordability["Year"] >= 2010) & (affordability["Year"] <= 2023)]

# Dictionnaire de traduction des mois
month_translation = {
    'janv.': 'Jan', 'févr.': 'Feb', 'mars': 'Mar', 'avr.': 'Apr', 'mai': 'May',
    'juin': 'Jun', 'juil.': 'Jul', 'août': 'Aug', 'sept.': 'Sep', 'oct.': 'Oct',
    'nov.': 'Nov', 'déc.': 'Dec'
}

# Transformation des dates
average_price['Time'] = average_price['Time'].replace(month_translation, regex=True)
average_price['Time'] = average_price['Time'].str.replace('-', ' ', regex=False)
average_price['Time'] = pd.to_datetime(average_price['Time'], format='%b %y')

sales_volume['Time'] = sales_volume['Time'].replace(month_translation, regex=True)
sales_volume['Time'] = sales_volume['Time'].str.replace('-', ' ', regex=False)
sales_volume['Time'] = pd.to_datetime(sales_volume['Time'], format='%b %y')

vacants['Year'] = pd.to_datetime(vacants['Year'], format='%Y')  # Assurez-vous que les années sont bien formatées
affordability['Year'] = pd.to_datetime(affordability['Year'], format='%Y')  # Assurez-vous que les années sont bien formatées

scaler = MinMaxScaler()

sales_volume2_normalized = pd.DataFrame(scaler.fit_transform(sales_volume2.iloc[:, 1:]), columns=sales_volume2.columns[1:])
crimes2_normalized = pd.DataFrame(scaler.fit_transform(crimes2.iloc[:, 1:]), columns=crimes2.columns[1:])
average_price_N = pd.DataFrame(scaler.fit_transform(average_price.iloc[:, 1:]), columns=average_price.columns[1:])
vacants_N = pd.DataFrame(scaler.fit_transform(vacants.iloc[:, 1:]), columns=vacants.columns[1:])
average_price2_N = pd.DataFrame(scaler.fit_transform(average_price2.iloc[:, 1:]), columns=average_price2.columns[1:])

corr_sales_crimes = sales_volume2_normalized.corrwith(crimes2_normalized).dropna()
corr_vacants_price = vacants_N.corrwith(average_price_N).dropna()
corr_crimes_price = crimes2_normalized.corrwith(average_price2_N).dropna()

def create_corr_heatmap(corr_data, title):
    # Créer un tableau de corrélation avec Plotly
    fig = go.Figure(data=go.Heatmap(
        z=[corr_data.values],
        x=corr_data.index,  
        y=["Correlation"],
        colorscale="RdBu",  
        zmin=-1, zmax=1, 
        colorbar=dict(title="Corrélation"),
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Quartiers",
        yaxis_title="Corrélation",
        template="plotly_dark"
    )
    
    return fig

# Layout Dash
layout = dbc.Container([
    dbc.Button("⬅ Retour à l'accueil", href="/", color="primary", className="mb-3"),
    html.H2("Indicateurs sur le logements à Londres", className="text-center mb-4"),

    # 📌 Graphique de l'évolution des prix moyens
    html.Div([
        html.H3("Évolution du prix moyen d'un bien par quartier entre 1995 et 2024"),
        html.Label("Sélectionnez un quartier :"),
        dcc.Dropdown(
            id='quartier-dropdown-logement',
            options=[{'label': "Tous les quartiers", 'value': "all"}] +
                    [{'label': col, 'value': col} for col in average_price.columns[1:]],
            value="all",
            style={'width': '50%', 'color': 'black'}
        ),
        dcc.Graph(id='logement-graph'),
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

    # 📌 Graphique de l'évolution des ventes de biens
    html.Div([
        html.H3("Évolution du nombre de biens vendus par quartier entre 1995 et 2024"),
        html.Label("Sélectionnez un quartier :"),
        dcc.Dropdown(
            id='quartier-dropdown-ventes',
            options=[{'label': "Tous les quartiers", 'value': "all"}] +
                    [{'label': col, 'value': col} for col in sales_volume.columns[1:]],
            value="all",
            style={'width': '50%', 'color': 'black'}
        ),
        dcc.Graph(id='ventes-graph'),
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

    # 📌 Graphique de l'évolution des logements vacants
    html.Div([
        html.H3("Évolution des logements vacants par quartier entre 2004 et 2023"),
        html.Label("Sélectionnez un quartier :"),
        dcc.Dropdown(
            id='quartier-dropdown-vacants',
            options=[{'label': "Tous les quartiers", 'value': "all"}] +
                    [{'label': col, 'value': col} for col in vacants.columns[1:]],
            value="all",
            style={'width': '50%', 'color': 'black'}
        ),
        dcc.Graph(id='vacants-graph'),
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

    # 📌 Graphique de l'évolution de l'abordabilité
    html.Div([
        html.H3("Évolution du ratio prix/revenus (abordabilité) entre 1997 et 2023"),
        html.Label("Sélectionnez un quartier :"),
        dcc.Dropdown(
            id='quartier-dropdown-affordability',
            options=[{'label': "Tous les quartiers", 'value': "all"}] +
                    [{'label': col, 'value': col} for col in affordability.columns[1:]],
            value="all",
            style={'width': '50%', 'color': 'black'}
        ),
        dcc.Graph(id='affordability-graph'),
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

    # 📌 Sélection pour la matrice de corrélation
    html.Div([
        html.H3("Matrice de corrélation entre quartiers"),
        dcc.RadioItems(
            id='corr-radio',
            options=[
                {'label': 'Prix Moyen', 'value': 'Prix Moyen'},
                {'label': 'Nombre de ventes', 'value': 'Nombre de biens vendus'},
                {'label': 'Nombre de logements vacants', 'value': 'Nombre de logements vacants'},
                {'label': 'Abordabilité', 'value': 'Abordabilité'},
            ],
            value='Nombre de logements vacants',  # Valeur par défaut
            labelStyle={'display': 'inline-block', 'margin-right': '20px'}
        ),
        dcc.Graph(id='corr-matrix-graph')
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),

    # 📌 Sélection pour la matrice de corrélation
    html.Div([
        html.H3("Matrice de corrélation par quartiers"),
        dcc.RadioItems(
            id='corr-radio-2',
            options=[
                {'label': 'Nombre de ventes & Nombre de crimes', 'value': 'Sales & Crimes'},
                {'label': 'Nombre de logements vacants & Prix moyen', 'value': 'Vacants & Price'},
                {'label': 'Nombre de crimes & Prix moyen', 'value': 'Crimes & Price'},
            ],
            value='Vacants & Price',  # Valeur par défaut
            labelStyle={'display': 'inline-block', 'margin-right': '20px'}
        ),
        dcc.Graph(id='corr-matrix-graph-2')
    ], style={'padding': '10px', 'border': '1px solid #ccc', 'margin-bottom': '20px'}),
], fluid=True)

# Callback pour mettre à jour le graphique des prix
@dash.callback(
    Output('logement-graph', 'figure'),
    Input('quartier-dropdown-logement', 'value')
)
def update_price_graph(selected_quartier):
    fig = make_subplots(rows=1, cols=1)

    if selected_quartier == "all":
        for column in average_price.columns[1:]:
            fig.add_trace(go.Scatter(x=average_price['Time'], y=average_price[column], mode='lines', name=column))
    else:
        fig.add_trace(go.Scatter(x=average_price['Time'], y=average_price[selected_quartier], mode='lines', name=selected_quartier))

    fig.update_layout(
        title=f"Évolution du prix moyen d'un bien {('par quartier' if selected_quartier == 'all' else f'pour {selected_quartier}')}",
        xaxis_title="Temps",
        yaxis_title="Prix",
        template="plotly_dark"
    )
    return fig

# Callback pour mettre à jour le graphique des ventes
@dash.callback(
    Output('ventes-graph', 'figure'),
    Input('quartier-dropdown-ventes', 'value')
)
def update_sales_graph(selected_quartier):
    fig = make_subplots(rows=1, cols=1)

    if selected_quartier == "all":
        for column in sales_volume.columns[1:]:
            fig.add_trace(go.Scatter(x=sales_volume['Time'], y=sales_volume[column], mode='lines', name=column))
    else:
        fig.add_trace(go.Scatter(x=sales_volume['Time'], y=sales_volume[selected_quartier], mode='lines', name=selected_quartier))

    fig.update_layout(
        title=f"Évolution du nombre de biens vendus {('par quartier' if selected_quartier == 'all' else f'pour {selected_quartier}')}",
        xaxis_title="Temps",
        yaxis_title="Nombre de ventes",
        template="plotly_dark"
    )
    return fig

# Callback pour mettre à jour le graphique des logements vacants
@dash.callback(
    Output('vacants-graph', 'figure'),
    Input('quartier-dropdown-vacants', 'value')
)
def update_vacants_graph(selected_quartier):
    fig = go.Figure()

    if selected_quartier == "all":
        for area in vacants.columns[1:]:
            fig.add_trace(go.Scatter(
                x=vacants['Year'], 
                y=vacants[area], 
                mode='lines+markers', 
                name=area
            ))
        fig.update_layout(
            title="Évolution des logements vacants par quartier entre 2004 et 2023",
            xaxis_title="Année",
            yaxis_title="Nombre de logements vacants",
            template="plotly_dark"
        )
    else:
        fig.add_trace(go.Scatter(
            x=vacants['Year'], 
            y=vacants[selected_quartier], 
            mode='lines+markers', 
            name=selected_quartier
        ))
        fig.update_layout(
            title=f"Évolution des logements vacants entre 2004 et 2023 - {selected_quartier}",
            xaxis_title="Année",
            yaxis_title="Nombre de logements vacants",
            template="plotly_dark"
        )

    return fig

# Callback pour mettre à jour le graphique de l'abordabilité
@dash.callback(
    Output('affordability-graph', 'figure'),
    Input('quartier-dropdown-affordability', 'value')
)
def update_affordability_graph(selected_quartier):
    fig = go.Figure()

    if selected_quartier == "all":
        for area in affordability.columns[1:]:
            fig.add_trace(go.Scatter(
                x=affordability['Year'], 
                y=affordability[area], 
                mode='lines+markers', 
                name=area
            ))
        fig.update_layout(
            title="Évolution du ratio prix/revenus (abordabilité) entre 1997 et 2023",
            xaxis_title="Année",
            yaxis_title="Ratio prix/revenus",
            template="plotly_dark"
        )
    else:
        fig.add_trace(go.Scatter(
            x=affordability['Year'], 
            y=affordability[selected_quartier], 
            mode='lines+markers', 
            name=selected_quartier
        ))
        fig.update_layout(
            title=f"Évolution du ratio prix/revenus (abordabilité) entre 1997 et 2023 - {selected_quartier}",
            xaxis_title="Année",
            yaxis_title="Ratio prix/revenus",
            template="plotly_dark"
        )

    return fig

# Callback pour mettre à jour la matrice de corrélation
@dash.callback(
    Output('corr-matrix-graph', 'figure'),
    Input('corr-radio', 'value')
)
def update_corr_matrix(selected):
    fig = go.Figure()

    if selected == 'Prix Moyen':
        corr_matrix = average_price.iloc[:, 1:].corr()
    elif selected == 'Nombre de biens vendus':
        corr_matrix = sales_volume.iloc[:, 1:].apply(pd.to_numeric, errors='coerce').corr()
    elif selected == 'Nombre de logements vacants':
        corr_matrix = vacants.iloc[:, 1:].corr()
    elif selected == 'Abordabilité':
        corr_matrix = affordability.iloc[:, 1:].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        hoverongaps=False
    ))

    fig.update_layout(
        title=f"Corrélation entre quartiers selon : {selected}",
        xaxis_title="Quartiers",
        yaxis_title="Quartiers",
        xaxis=dict(tickmode='array', tickvals=np.arange(len(corr_matrix.columns)), ticktext=corr_matrix.columns),
        yaxis=dict(tickmode='array', tickvals=np.arange(len(corr_matrix.columns)), ticktext=corr_matrix.columns),
        template="plotly_dark",
        height=800,  
        width=800,  
    )

    return fig

# Callback pour mettre à jour le graphique de corrélation en fonction de la sélection
@dash.callback(
    Output('corr-matrix-graph-2', 'figure'),
    Input('corr-radio-2', 'value')
)
def update_corr_graph(selected_corr):
    if selected_corr == 'Sales & Crimes':
        corr_data = corr_sales_crimes
        title = "Corrélation par quartiers entre : Nombre de ventes & Nombre de crimes"
    elif selected_corr == 'Vacants & Price':
        corr_data = corr_vacants_price
        title = "Corrélation par quartiers entre : Nombre de logements vacants & Prix moyen"
    elif selected_corr == 'Crimes & Price':
        corr_data = corr_crimes_price
        title = "Corrélation par quartiers entre : Nombre de crimes vacants & Prix moyen"

    return create_corr_heatmap(corr_data, title)