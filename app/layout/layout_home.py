from dash import dcc, html
import dash_bootstrap_components as dbc

# Mise en page de la page d'accueil
layout = dbc.Container([
    # Titre du projet
    html.H1("Étude sur Londres - Projet Open Data",
            className="text-center mt-4", style={'fontWeight': 'bold'}),
    html.H4("ABARKAN Suhaïla - MOUCHRIF Dounia - TISSANDIER Mathilde", className="text-center mb-5",
            style={'color': 'gray'}),

    # Grille avec 4 sections
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Transports", className="card-title text-center"),
                    dcc.Link(html.Img(src="/assets/transports.png",
                             style={"width": "40%"}), href="/transports")
                ]),
                className="shadow-lg text-center",
                style={"cursor": "pointer"}
            ), width=6, md=6, className="mb-4"
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Logement", className="card-title text-center"),
                    dcc.Link(html.Img(src="/assets/logement.png",
                             style={"width": "40%"}), href="/logement")
                ]),
                className="shadow-lg text-center",
                style={"cursor": "pointer"}
            ), width=6, md=6, className="mb-4"
        )
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Santé", className="card-title text-center"),
                    dcc.Link(html.Img(src="/assets/sante.png",
                             style={"width": "40%"}), href="/sante")
                ]),
                className="shadow-lg text-center",
                style={"cursor": "pointer"}
            ), width=6, md=6, className="mb-4"
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Prédictions et Clustering",
                            className="card-title text-center"),
                    dcc.Link(html.Img(src="/assets/predictions.png",
                             style={"width": "40%"}), href="/predictions")
                ]),
                className="shadow-lg text-center",
                style={"cursor": "pointer"}
            ), width=6, md=6, className="mb-4"
        )
    ])
], fluid=True)
