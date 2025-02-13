from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

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
# Graphique 3 : Indicateur HLE avec intervalles de confiance
#####

hle_male_df['Negative Error Male'] = hle_male_df['Value'] - \
    hle_male_df['Lower CI']
hle_male_df['Positive Error Male'] = hle_male_df['Upper CI'] - \
    hle_male_df['Value']

hle_female_df['Negative Error Female'] = hle_female_df['Value'] - \
    hle_female_df['Lower CI']
hle_female_df['Positive Error Female'] = hle_female_df['Upper CI'] - \
    hle_female_df['Value']

fig3 = go.Figure()

fig3.add_trace(go.Scatter(
    x=hle_male_df['Time Period'], y=hle_male_df['Value'],
    mode='markers',
    name='Homme',
    marker=dict(color='blue', size=8),
    error_y=dict(type='data', symmetric=False,
                 array=hle_male_df['Positive Error Male'],
                 arrayminus=hle_male_df['Negative Error Male'])
))

fig3.add_trace(go.Scatter(
    x=hle_female_df['Time Period'], y=hle_female_df['Value'],
    mode='markers',
    name='Femme',
    marker=dict(color='pink', size=8),
    error_y=dict(type='data', symmetric=False,
                 array=hle_female_df['Positive Error Female'],
                 arrayminus=hle_female_df['Negative Error Female'])
))

fig3.update_layout(
    title="Indicateur HLE avec intervalles de confiance",
    xaxis_title='Période',
    yaxis_title='Valeur',
    legend_title='Sexe',
    # template='plotly_dark',
    xaxis=dict(tickangle=45)
)

#####
# Mise en page
#####

layout = dbc.Container([
    dbc.Button("⬅ Retour à l'accueil", href="/",
               color="primary", className="mb-3"),
    html.H2("Indicateurs sur la santé à Londres",
            className="text-center mb-4"),

    dcc.Graph(figure=fig1),
    dcc.Graph(figure=fig2),
    dcc.Graph(figure=fig3)

], fluid=True)
