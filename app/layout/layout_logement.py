from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Exemple de données sur le logement
df_logement = pd.DataFrame({
    "Ville": ["Bordeaux", "Paris", "Lyon", "Marseille"],
    "Prix Moyen": [3500, 10000, 5000, 4000],
    "Nombre de Logements": [120000, 300000, 150000, 130000]
})

fig_logement = px.bar(df_logement, x="Ville", y="Prix Moyen",
                      title="Prix Moyen du Logement par Ville")

layout = dbc.Container([
    dbc.Button("⬅ Retour à l'accueil", href="/",
               color="primary", className="mb-3"),
    html.H2("Dashboard Logement", className="text-center mb-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_logement), width=12)
    ])
], fluid=True)
