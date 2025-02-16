from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import plotly.express as px
from dash import callback_context, no_update

#####
# Graphique 1 : Evolution de l'espérence de vie moyenne homme/femme à Londres
#####

file_path = "data/His indicators update Nov 2024 FINAL.xlsx"

hle_male_df = pd.read_excel(file_path, sheet_name="1. HLE male")
hle_female_df = pd.read_excel(file_path, sheet_name="2. HLE female")

hle_male_df["Time Period"] = hle_male_df["Time Period"].str[:4].astype(int)
hle_female_df["Time Period"] = hle_female_df["Time Period"].str[:4].astype(int)

hle_male_df = hle_male_df.groupby('Time Period')['Value'].mean().reset_index()
hle_female_df = hle_female_df.groupby(
    'Time Period')['Value'].mean().reset_index()

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=hle_male_df['Time Period'], y=hle_male_df['Value'],
               mode='lines', name='Homme', line=dict(color='blue')))
fig1.add_trace(go.Scatter(x=hle_female_df['Time Period'], y=hle_female_df['Value'],
               mode='lines', name='Femme', line=dict(color='pink')))
fig1.update_layout(
    title="Évolution de l'HLE (Healthy Life Expectancy) moyenne à Londres (Hommes vs Femmes)",
    xaxis_title='Année',
    yaxis_title='Âge',
    legend_title='Sexe',
    template='plotly_dark',
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
    xaxis=dict(tickangle=45)
)

#####
# Graphique 2 : Comparaison des valeurs moyennes pour les hommes et les femmes par zone géographique
#####

hle_male_df = pd.read_excel(file_path, sheet_name="1. HLE male")
hle_female_df = pd.read_excel(file_path, sheet_name="2. HLE female")

merged_df = pd.merge(hle_male_df[['Area Name', 'Value']], hle_female_df[[
                     'Area Name', 'Value']], on='Area Name', suffixes=('_Male', '_Female'))
average_values = merged_df.groupby(
    'Area Name')[['Value_Male', 'Value_Female']].mean().reset_index()

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=average_values['Area Name'],
    y=average_values['Value_Male'],
    name='Homme',
    marker=dict(color='blue')
))
fig2.add_trace(go.Bar(
    x=average_values['Area Name'],
    y=average_values['Value_Female'],
    name='Femme',
    marker=dict(color='pink')
))

fig2.update_layout(
    title="Comparaison des valeurs moyennes pour les hommes et les femmes par zone géographique",
    xaxis_title='Zone géographique',
    yaxis_title='Valeur',
    barmode='group',
    legend_title='Sexe',
    template='plotly_dark',
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white'),
    xaxis=dict(tickangle=90)
)

#####
# Graphique 3 : Cartes + Indicateur HLE avec intervalles de confiance
#####

file_path = "data/His indicators update Nov 2024 FINAL.xlsx"

hle_male_df = pd.read_excel(file_path, sheet_name="1. HLE male")
hle_male_df = hle_male_df[["Time Period",
                           "Area Name", "Value", "Lower CI", "Upper CI"]]
hle_male_df.dropna(inplace=True)
hle_male_df["Value"] = pd.to_numeric(hle_male_df["Value"], errors="coerce")
hle_male_df['Negative Error Male'] = hle_male_df['Value'] - \
    hle_male_df['Lower CI']
hle_male_df['Positive Error Male'] = hle_male_df['Upper CI'] - \
    hle_male_df['Value']


hle_female_df = pd.read_excel(file_path, sheet_name="2. HLE female")
hle_female_df = hle_female_df[["Time Period",
                               "Area Name", "Value", "Lower CI", "Upper CI"]]
hle_female_df.dropna(inplace=True)
hle_female_df["Value"] = pd.to_numeric(hle_female_df["Value"], errors="coerce")
hle_female_df['Negative Error Female'] = hle_female_df['Value'] - \
    hle_female_df['Lower CI']
hle_female_df['Positive Error Female'] = hle_female_df['Upper CI'] - \
    hle_female_df['Value']

map_files = {
    "HLE Male": "london_health_map_male.html",
    "HLE Female": "london_health_map_female.html"
}

#####
# Graphique 4 : Evolution du surpoids
#####

weight_df = pd.read_excel(file_path, sheet_name="5. Excess weight age 10-11")
weight_df.dropna(subset=["Value"], inplace=True)

#####
# Graphique 5 : Détection du HIV par éthnie
#####

hiv_df = pd.read_excel(file_path, sheet_name="11. HIV late diagnosis")
hiv_df = hiv_df[['Time Period', 'Ethnic group ', 'Value']]
hiv_df = hiv_df.rename(columns={
                       'Time Period': 'Year', 'Ethnic group ': 'Ethnicity', 'Value': 'Late Diagnosis Rate'})

fig_5 = px.line(
    hiv_df,
    x='Year',
    y='Late Diagnosis Rate',
    color='Ethnicity',
    markers=True,
    title="Évolution du diagnostic tardif du VIH par ethnie",
    labels={"Year": "Année",
            "Late Diagnosis Rate": "Taux de diagnostic tardif (%)"}
)

fig_5.update_layout(
    template='plotly_dark',
    paper_bgcolor='black',
    plot_bgcolor='black',
    font=dict(color='white')
)

#####
# Mise en page
#####

layout = dbc.Container([
    dbc.Button("⬅ Retour à l'accueil", href="/",
               color="primary", className="mb-3"),
    html.H2("Indicateurs sur la santé à Londres",
            className="text-center mb-4", style={'color': 'white'}),

    # Carte + Indicateur HLE
    dbc.Card(
        dbc.CardBody([
            html.H4("Visualisation de l'espérance de vie en bonne santé (HLE - Healthy Life Expectancy)",
                    className="card-title", style={'color': 'white'}),
            html.H5(
                "Sélectionnez un indicateur pour afficher la carte et le graphique",
                style={'color': 'white'}),
            dcc.Dropdown(
                id="indicator-dropdown",
                options=[
                    {"label": "HLE (Healthy Life Expectancy) Male",
                     "value": "HLE Male"},
                    {"label": "HLE (Healthy Life Expectancy) Female",
                     "value": "HLE Female"}
                ],
                value="HLE Male",
                clearable=False,
                className="mb-4"
            ),
            dbc.Button("Analyse", id="health_open-analysis-button-0",
                       color="info", className="mb-3"),

            html.Div([
                html.Div([
                    html.Iframe(
                        id="map", src="/static/london_health_map_male.html", width="100%", height="650px")
                ], style={"width": "50%", "display": "inline-block"}),

                html.Div([
                    dcc.Graph(id="confidence-graph")
                ], style={"width": "50%", "display": "inline-block"})
            ], style={"display": "flex"}),

            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(
                    "Analyse de la carte et du graphique des intervalles de confiance")),
                dbc.ModalBody(id="health_analysis-content-0"),
                dbc.ModalFooter(dbc.Button(
                    "Fermer", id="health_close-analysis-button-0", className="ms-auto")),
            ], id="health_analysis-modal-0", size="lg", is_open=False),
        ], style={'backgroundColor': 'black'}),
        className="mb-4 shadow"
    ),

    # Espérance de vie
    dbc.Card(
        dbc.CardBody([
            html.H4("Évolution de l'espérance de vie en bonne santé (HLE) à Londres",
                    className="card-title", style={'color': 'white'}),
            dbc.Button("Analyse", id="health_open-analysis-button-1",
                       color="info", className="mb-3"),
            dcc.Graph(figure=fig1),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(
                    "Analyse de l'évolution de l'espérance de vie en bonne santé")),
                dbc.ModalBody(id="health_analysis-content-1"),
                dbc.ModalFooter(dbc.Button(
                    "Fermer", id="health_close-analysis-button-1", className="ms-auto")),
            ], id="health_analysis-modal-1", size="lg", is_open=False),
        ], style={'backgroundColor': 'black'}),
        className="mb-4 shadow"
    ),

    # Comparaison HLE par zone
    dbc.Card(
        dbc.CardBody([
            html.H4("Comparaison des valeurs moyennes de l'HLE par zone géographique",
                    className="card-title", style={'color': 'white'}),
            dbc.Button("Analyse", id="health_open-analysis-button-2",
                       color="info", className="mb-3"),
            dcc.Graph(figure=fig2),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(
                    "Analyse de la comparaison par zone géographique")),
                dbc.ModalBody(id="health_analysis-content-2"),
                dbc.ModalFooter(dbc.Button(
                    "Fermer", id="health_close-analysis-button-2", className="ms-auto")),
            ], id="health_analysis-modal-2", size="lg", is_open=False),
        ], style={'backgroundColor': 'black'}),
        className="mb-4 shadow"
    ),

    # Excès de poids
    dbc.Card(
        dbc.CardBody([
            html.H3("Évolution de l'excès de poids chez les enfants (10-11 ans)",
                    className="card-title", style={'color': 'white'}),
            dcc.Dropdown(
                id="area-dropdown",
                options=[{"label": area, "value": area}
                         for area in weight_df["Area Name"].unique()],
                value=weight_df["Area Name"].unique()[0],
                clearable=False,
                className="mb-4"
            ),
            dbc.Button("Analyse", id="health_open-analysis-button-3",
                       color="info", className="mb-3"),
            dcc.Graph(id="weight-trend-graph"),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(
                    "Analyse de l'évolution de l'excès de poids")),
                dbc.ModalBody(id="health_analysis-content-3"),
                dbc.ModalFooter(dbc.Button(
                    "Fermer", id="health_close-analysis-button-3", className="ms-auto")),
            ], id="health_analysis-modal-3", size="lg", is_open=False),
        ], style={'backgroundColor': 'black'}),
        className="mb-4 shadow"
    ),

    # VIH par ethnie
    dbc.Card(
        dbc.CardBody([
            html.H3("Inégalités du diagnostic tardif du VIH selon l'ethnie",
                    className="card-title", style={'color': 'white'}),
            dbc.Button("Analyse", id="health_open-analysis-button-4",
                       color="info", className="mb-3"),
            dcc.Graph(figure=fig_5),
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle(
                    "Analyse des inégalités du diagnostic tardif du VIH")),
                dbc.ModalBody(id="health_analysis-content-4"),
                dbc.ModalFooter(dbc.Button(
                    "Fermer", id="health_close-analysis-button-4", className="ms-auto")),
            ], id="health_analysis-modal-4", size="lg", is_open=False),
        ], style={'backgroundColor': 'black'}),
        className="mb-4 shadow"
    )
], fluid=True, style={'backgroundColor': 'black', 'color': 'white', 'minHeight': '100vh', 'padding': '20px'})

#####
# Dropdowns
#####


def register_callbacks(app):
    @app.callback(
        [Output("map", "src"),
         Output("confidence-graph", "figure")],
        [Input("indicator-dropdown", "value")]
    )
    def update_content(selected_indicator):
        if selected_indicator == "HLE Male":
            map_src = "/static/london_health_map_male.html"
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hle_male_df['Time Period'], y=hle_male_df['Value'],
                mode='markers', marker=dict(color='blue'), name='Homme',
                error_y=dict(type='data', symmetric=False,
                             array=hle_male_df['Positive Error Male'],
                             arrayminus=hle_male_df['Negative Error Male'])
            ))
        else:
            map_src = "/static/london_health_map_female.html"
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hle_female_df['Time Period'], y=hle_female_df['Value'],
                mode='markers', marker=dict(color='pink'), name='Femme',
                error_y=dict(type='data', symmetric=False,
                             array=hle_female_df['Positive Error Female'],
                             arrayminus=hle_female_df['Negative Error Female'])
            ))

        fig.update_layout(
            title="Indicateur HLE avec intervalles de confiance",
            xaxis_title="Période", yaxis_title="Valeur",
            legend_title="Légende", xaxis_tickangle=-45,
            template='plotly_dark',
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white')
        )

        return map_src, fig

    @app.callback(
        Output("weight-trend-graph", "figure"),
        [Input("area-dropdown", "value")]
    )
    def update_weight_graph(selected_area):
        filtered_df = weight_df[weight_df["Area Name"] == selected_area]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered_df["Time Period"],
            y=filtered_df["Value"],
            mode='lines+markers',
            name=selected_area,
            line=dict(color='red')
        ))

        fig.update_layout(
            title=f"Évolution de l'excès de poids à {selected_area}",
            xaxis_title='Période',
            yaxis_title='Poids',
            template='plotly_dark',
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white')
        )

        return fig

    # Callbacks pour les modals
    for i in range(0, 5):
        @app.callback(
            [Output(f"health_analysis-modal-{i}", "is_open"),
             Output(f"health_analysis-content-{i}", "children")],
            [Input(f"health_open-analysis-button-{i}", "n_clicks"),
             Input(f"health_close-analysis-button-{i}", "n_clicks")],
            prevent_initial_call=True
        )
        def toggle_modal(open_clicks, close_clicks, i=i):
            ctx = callback_context
            if not ctx.triggered:
                return no_update, no_update
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if button_id == f"health_open-analysis-button-{i}":
                analysis_text = f"Description spécifique pour le graphique {i}."
                return True, analysis_text
