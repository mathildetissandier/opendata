from dash import dcc, html
import dash_bootstrap_components as dbc

# Mise en page de la page d'accueil
layout = dbc.Container([
    # Titre du projet
    html.H1("Étude sur Londres - Projet Open Data",
            className="text-center mt-4", style={'fontWeight': 'bold', 'color': 'white'}),
    html.H4("ABARKAN Suhaïla - MOUCHRIF Dounia - TISSANDIER Mathilde", className="text-center mb-5",
            style={'color': 'gray'}),

    # Grille avec 4 sections
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Transports", className="card-title text-center", style={'color': 'gray'}),
                    dcc.Link(
                        html.Img(
                            src="/assets/transports.png",
                            style={
                                "width": "40%",
                                "padding": "10px",  # Espace autour de l'image
                            }
                        ),
                        href="/transports"
                    )
                ]),
                className="shadow-lg text-center",
                style={
                    "cursor": "pointer",
                    "background-color": "#f0f0f0",  # Fond gris clair pour la carte
                    "border": "none",  # Supprimer la bordure par défaut
                    "border-radius": "10px"  # Coins arrondis
                }
            ), width=6, md=6, className="mb-4"
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Logement", className="card-title text-center", style={'color': 'gray'}),
                    dcc.Link(
                        html.Img(
                            src="/assets/logement.png",
                            style={
                                "width": "40%",
                                "padding": "10px",  # Espace autour de l'image
                            }
                        ),
                        href="/logement"
                    )
                ]),
                className="shadow-lg text-center",
                style={
                    "cursor": "pointer",
                    "background-color": "#f0f0f0",  # Fond gris clair pour la carte
                    "border": "none",  # Supprimer la bordure par défaut
                    "border-radius": "10px"  # Coins arrondis
                }
            ), width=6, md=6, className="mb-4"
        )
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Santé", className="card-title text-center", style={'color': 'gray'}),
                    dcc.Link(
                        html.Img(
                            src="/assets/sante.png",
                            style={
                                "width": "40%",
                                "padding": "10px",  # Espace autour de l'image
                            }
                        ),
                        href="/sante"
                    )
                ]),
                className="shadow-lg text-center",
                style={
                    "cursor": "pointer",
                    "background-color": "#f0f0f0",  # Fond gris clair pour la carte
                    "border": "none",  # Supprimer la bordure par défaut
                    "border-radius": "10px"  # Coins arrondis
                }
            ), width=6, md=6, className="mb-4"
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Prédictions et Clustering",
                            className="card-title text-center", style={'color': 'gray'}),
                    dcc.Link(
                        html.Img(
                            src="/assets/predictions.png",
                            style={
                                "width": "40%",
                                "padding": "10px",  # Espace autour de l'image
                            }
                        ),
                        href="/predictions"
                    )
                ]),
                className="shadow-lg text-center",
                style={
                    "cursor": "pointer",
                    "background-color": "#f0f0f0",  # Fond gris clair pour la carte
                    "border": "none",  # Supprimer la bordure par défaut
                    "border-radius": "10px"  # Coins arrondis
                }
            ), width=6, md=6, className="mb-4"
        )
    ])
], fluid=True, style={'background-color': 'black', 'height': '100vh'})  # Fond noir pour la page