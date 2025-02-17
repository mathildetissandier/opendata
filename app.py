import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
from flask import Flask
from layout import layout_home, layout_logement, layout_sante, layout_predictions
# Assurez-vous d'importer la variable 'layout' définie dans layout_transports
from layout.layout_transports import layout
import os


app = dash.Dash(__name__, external_stylesheets=[
                dbc.themes.FLATLY], suppress_callback_exceptions=True)
server = app.server

# Mise en page avec navigation


def serve_layout():
    return html.Div(
        # Fond noir, texte en blanc
        style={'backgroundColor': 'black', 'color': 'white'},
        children=[
            dcc.Location(id='url', refresh=False),
            dbc.Container(id='page-content', fluid=True)
        ]
    )


app.layout = serve_layout
layout_sante.register_callbacks(app)
layout_predictions.register_callbacks(app)
# Callback pour gérer la navigation


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/transports':
        return layout  # Retourne la variable layout définie dans layout_transports.py
    elif pathname == '/logement':
        return layout_logement.layout
    elif pathname == '/sante':
        return layout_sante.layout
    elif pathname == '/predictions':
        return layout_predictions.layout
    else:
        return layout_home.layout


# Lancer l'application

if __name__ == '__main__':
    # Récupérer le port défini par Render
    port = int(os.getenv('PORT', 8050))
    app.run_server(host="0.0.0.0", port=port)
