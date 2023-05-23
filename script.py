#Import
from dash import Dash, dcc, html, Input, Output, dash_table
from urllib.request import urlopen
import json
import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
pio.templates.default = "plotly_dark"

with urlopen('https://raw.githubusercontent.com/daniel-marocchi/GraficiEurostat/main/EuropeGeoJSON') as response:
  EuropeGeoJSON = json.load(response)
dati = pd.read_csv("https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/HSW_N2_02/?format=SDMX-CSV&lang=en&label=label_only")
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# APP
app = Dash("GraficiEurostat", external_stylesheets=external_stylesheets)


#Modellazione dati
dati = dati.query("nace_r2 == 'Total - all NACE activities'")
datiIncidenza = dati
dati = dati.query("unit == 'Number'")
dati = dati.drop(columns=['DATAFLOW', 'LAST UPDATE', 'OBS_FLAG', 'freq'])
dati2020 = dati.query("TIME_PERIOD == 2020")

#-----------------------------------------------------------------------------------------------------------------------------

#Grafici
graficoPunti = px.scatter(
	dati,
	x="geo",
	y="OBS_VALUE",
  color="OBS_VALUE",
	labels={"OBS_VALUE": "Numero Incidenti", "geo": "Nazioni"},
  animation_frame="TIME_PERIOD",
	animation_group="geo",
  height=1000
)
graficoPunti.update_traces(marker_size=30)

staticBarChart = px.bar(
  dati2020, 
  x="geo", 
  y="OBS_VALUE",
  height=1000,
  labels={"OBS_VALUE": "Numero Incidenti", "geo": "Nazioni", "TIME_PERIOD": "Anno"})


globe = px.choropleth(
	dati2020.query("geo != 'European Union - 27 countries (from 2020)'"),
	color="OBS_VALUE",
	geojson=EuropeGeoJSON,
  locations="geo",
	hover_name="geo",
	hover_data="OBS_VALUE",
	locationmode="country names",
	height=2000,
	labels={"OBS_VALUE": "Numero Incidenti", "geo": "Nazione"},
	fitbounds="locations",
	color_continuous_scale="sunsetdark",
)

globe.update_geos(
	showocean=True,
	oceancolor="Gray",
	projection_type="orthographic",
	showcountries=True,
	countrycolor="Gray",
)


choroplethMap = px.choropleth_mapbox(
	dati2020.query(
		"geo != 'European Union - 27 countries (from 2020)'"
	),
  geojson=EuropeGeoJSON,
	locations="geo",
  featureidkey="properties.NAME",
	mapbox_style="carto-darkmatter",
	center={"lat": 45.891031, "lon": 10.863817},
	zoom=3,
	height=1300,
	color="OBS_VALUE",
  color_continuous_scale="sunsetdark",
  hover_name="geo",
  hover_data="OBS_VALUE",
  labels={"OBS_VALUE": "Numero Incidenti", "geo": "Nazioni", "TIME_PERIOD": "Anno"}
)


animatedBarChart = px.bar(
	dati,
	x="geo",
	y="OBS_VALUE",
	animation_frame="TIME_PERIOD",
	animation_group="geo",
	color="OBS_VALUE",
	height=1300,
	color_continuous_scale="sunsetdark",
	labels={"OBS_VALUE": "Numero Incidenti", "geo": "Nazioni", "TIME_PERIOD": "Anno"},
	range_y=[0, 5000],
	hover_data="OBS_VALUE",
	hover_name="geo",
)


pieChart = px.pie(
	dati.query("TIME_PERIOD == 2020"),
	names="geo",
	values="OBS_VALUE",
	height=1000,
	labels={"OBS_VALUE": "Numero Incidenti", "geo": "Nazione"},
	hover_name="geo",
)

pieChart.update_traces(textposition="inside", textinfo="text+label")


#App Layout
app.layout = html.Div(
	style={
		"textAlign": "center",
    #'boxSizing': 'borderBox',
    'margin' : 0,
    'padding' : '20px',
    'color' : 'white',
    'backgroundColor' : '#111111'
	},
	children=[
    html.H1('Incidenti sul Lavoro'),
		dash_table.DataTable(
			data=dati2020.to_dict("records"),
			columns=[{"id": c, "name": c} for c in dati2020.drop(columns=['nace_r2', 'unit']).columns],
      style_header={
        'backgroundColor': 'white',
        'fontWeight': 'bold',
        'fontSize' : 35,
        'textTransform' : 'upperCase',
        'padding' : '16px 0px',
        'color' : 'd0d0d0',
        'backgroundColor' : '#1c1c1c',
        'borderTop': 'none'
    },
      style_cell={'textAlign': 'center', 
        'fontSize' : 20,
        'fontFamily' : 'Arial',
        'padding' : '10px 0px',
        'backgroundColor' : '#111111'
      },
      #style_as_list_view=True,
      style_table={
        'margin' : '20px 0px'
      }
		),
		
    dcc.Loading(dcc.Graph(figure=animatedBarChart)),
		dcc.Graph(figure=graficoPunti),
		dcc.Graph(figure=staticBarChart),
		dcc.Graph(figure=choroplethMap),
		dcc.Graph(figure=globe),

		dcc.Graph(figure=pieChart),
	],
)

app.run(debug=True, dev_tools_hot_reload=True, dev_tools_ui=True)