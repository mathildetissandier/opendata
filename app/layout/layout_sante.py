from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import plotly.express as px

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
    # template='plotly_dark',
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
    # template='plotly_dark',
    xaxis=dict(tickangle=90)
)

#####
# Graphique 3 : Cartes + Indicateur HLE avec intervalles de confiance
#####

# Charger les données pour les hommes
file_path = "data/His indicators update Nov 2024 FINAL.xlsx"
hle_male_df = pd.read_excel(file_path, sheet_name="1. HLE male")
hle_male_df = hle_male_df[["Time Period", "Area Name", "Value", "Lower CI", "Upper CI"]]
hle_male_df.dropna(inplace=True)
hle_male_df["Value"] = pd.to_numeric(hle_male_df["Value"], errors="coerce")

hle_male_df['Negative Error Male'] = hle_male_df['Value'] - hle_male_df['Lower CI']
hle_male_df['Positive Error Male'] = hle_male_df['Upper CI'] - hle_male_df['Value']

# Charger les données pour les femmes
hle_female_df = pd.read_excel(file_path, sheet_name="2. HLE female")
hle_female_df = hle_female_df[["Time Period", "Area Name", "Value", "Lower CI", "Upper CI"]]
hle_female_df.dropna(inplace=True)
hle_female_df["Value"] = pd.to_numeric(hle_female_df["Value"], errors="coerce")

hle_female_df['Negative Error Female'] = hle_female_df['Value'] - hle_female_df['Lower CI']
hle_female_df['Positive Error Female'] = hle_female_df['Upper CI'] - hle_female_df['Value']

# Liste des cartes HTML (assurez-vous que ces fichiers existent dans le dossier static)
map_files = {
    "HLE Male": "london_health_map_male.html",
    "HLE Female": "london_health_map_female.html"
}

#####
# Graphique 4 : Evolution du surpoids
#####

weight_df = pd.read_excel(file_path, sheet_name="5. Excess weight age 10-11")
weight_df.dropna(subset=["Value"], inplace=True)  # Suppression des valeurs NaN

#####
# Graphique 5 : Détection du HIV par éthnie
#####

hiv_df = pd.read_excel(file_path, sheet_name="11. HIV late diagnosis")
hiv_df = hiv_df[['Time Period', 'Ethnic group ', 'Value']]
hiv_df = hiv_df.rename(columns={'Time Period': 'Year', 'Ethnic group ': 'Ethnicity', 'Value': 'Late Diagnosis Rate'})

# Création du graphique avec toutes les ethnies
fig_5 = px.line(
    hiv_df, 
    x='Year', 
    y='Late Diagnosis Rate', 
    color='Ethnicity',  # Une courbe par ethnie
    markers=True,
    title="Évolution du diagnostic tardif du VIH par ethnie",
    labels={"Year": "Année", "Late Diagnosis Rate": "Taux de diagnostic tardif (%)"}
)

#####
# Mise en page
#####

layout = dbc.Container([
    dbc.Button("⬅ Retour à l'accueil", href="/", color="primary", className="mb-3"),
    html.H2("Indicateurs sur la santé à Londres", className="text-center mb-4"),
    html.H3("Visualisations de l'espérence de vie (HLE - Healthy Life Expectancy)", className="mt-4"),
    html.H4("Sélectionnez un indicateur pour afficher la carte et le graphique", className="mt-4"),
    dcc.Dropdown(
        id="indicator-dropdown",
        options=[
            {"label": "HLE (Healthy Life Expectancy) Male", "value": "HLE Male"},
            {"label": "HLE (Healthy Life Expectancy) Female", "value": "HLE Female"}
        ],
        value="HLE Male",
        clearable=False,
        className="mb-4"
    ),
    html.Div([
        html.Div([
            html.Iframe(id="map", src="/static/london_health_map_male.html", width="100%", height="650px")
        ], style={"width": "50%", "display": "inline-block"}),

        html.Div([
            dcc.Graph(id="confidence-graph")
        ], style={"width": "50%", "display": "inline-block"})
    ], style={"display": "flex"}),

    dcc.Graph(figure=fig1),

    dcc.Graph(figure=fig2),

    html.H3("Évolution de l'excès de poids chez les enfants (10-11 ans) par zone", className="mt-4"),
    dcc.Dropdown(
        id="area-dropdown",
        options=[{"label": area, "value": area} for area in weight_df["Area Name"].unique()],
        value=weight_df["Area Name"].unique()[0],
        clearable=False,
        className="mb-4"
    ),
    dcc.Graph(id="weight-trend-graph"),

    html.H3("Inégalités du diagnostic tardif du VIH selon l'ethnie", className="mt-4"),
    dcc.Graph(figure=fig_5)

], fluid=True)

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
            template="plotly_white"
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
            template='plotly_white'
        )
        
        return fig