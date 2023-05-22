from dash import Dash, dcc, html, Input, Output, dash_table
from urllib.request import urlopen
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# pycountry
#https://raw.githubusercontent.com/leakyMirror/map-of-europe/master/GeoJSON/europe.geojson

# APP
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets=external_stylesheets
app = Dash("GraficiEurostat")


# Import Dati
with urlopen('https://raw.githubusercontent.com/leakyMirror/map-of-europe/master/GeoJSON/europe.geojson') as response:
  eu = json.load(response)

#print(eu["features"][2]['properties']['NAME'])


dati = (
	pd.read_csv(
		"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/HSW_N2_02$DEFAULTVIEW/?format=SDMX-CSV&lang=en&label=label_only"
	)
	.query("nace_r2 == 'Total - all NACE activities'")
	.query("unit == 'Number'")
)

dati2 = pd.read_csv(
	"https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/HSW_N2_02$DEFAULTVIEW/1.0/A.NR.TOTAL.*?c[geo]=BE,BG,CZ,DK,DE,EE,IE,EL,ES,FR,HR,IT,CY,LV,LT,LU,HU,MT,NL,AT,PL,PT,RO,SI,SK,FI,SE,IS,NO,CH,UK&compress=false&format=csvdata&formatVersion=2.0&c[TIME_PERIOD]=ge:2011+le:2020"
)

dati2020 = dati.query("TIME_PERIOD == 2020")
dati2019 = dati.query("TIME_PERIOD == 2019")
dati2018 = dati.query("TIME_PERIOD == 2018")
dati2017 = dati.query("TIME_PERIOD == 2017")
dati2016 = dati.query("TIME_PERIOD == 2016")
dati2015 = dati.query("TIME_PERIOD == 2015")


# Grafici
g1 = px.scatter(
	dati2020,
	x="geo",
	y="OBS_VALUE",
	labels={"OBS_VALUE": "Numero Incidenti", "geo": "Nazioni"},
)

g2 = px.bar(dati2020, x="geo", y="OBS_VALUE")

g4 = px.choropleth(
	dati2020.query("geo != 'European Union - 27 countries (from 2020)' "),
	color="OBS_VALUE",
	locations="geo",
	hover_name="geo",
	hover_data="OBS_VALUE",
	locationmode="country names",
	height=800,
	labels={"OBS_VALUE": "Numero Incidenti", "geo": "Nazione"},
	fitbounds="locations",
	color_continuous_scale="sunsetdark",
)
g4.update_geos(
	showocean=True,
	oceancolor="LightBlue",
	#projection_type="orthographic",
	showcountries=True,
	countrycolor="Gray",
)

map = px.choropleth_mapbox(
	dati2.query("TIME_PERIOD == 2020").query(
		"geo != 'European Union - 27 countries (from 2020)' "
	),
  geojson=eu,
	locations="geo",
  featureidkey="properties.NAME",
	mapbox_style="carto-positron",
	center={"lat": 45.891031, "lon": 10.863817},
	zoom=4,
	height=700,
	color="OBS_VALUE",
)

animatedBarChart = px.bar(
	dati2,
	x="geo",
	y="OBS_VALUE",
	animation_frame="TIME_PERIOD",
	animation_group="geo",
	color="OBS_VALUE",
	color_continuous_scale="sunsetdark",
	height=700,
	labels={"OBS_VALUE": "Numero Incidenti", "geo": "Nazioni", "TIME_PERIOD": "Anno"},
	range_y=[0, 800],
	hover_data="OBS_VALUE",
	hover_name="geo",
)

pieChart = px.pie(
	dati2,
	names="geo",
	values="OBS_VALUE",
	height=1000,
	labels={"OBS_VALUE": "Numero Incidenti", "geo": "Nazione"},
	hover_name="geo",
)

table = go.Figure(
	data=[
		go.Table(
			header=dict(
				values=[["ANNO"], ["NAZIONE"], ["INCIDENTI"]],
				fill_color="paleturquoise",
				align="center",
				font=dict(size=18),
				height=60,
				),
				cells=dict(
				values=[dati2020.TIME_PERIOD, dati2020.geo, dati2020.OBS_VALUE],
				# fill_color='lavender',
				align="left",
				height=40,
				font_size=20,
			),
		)
	]
)

pieChart.update_traces(textposition="inside", textinfo="text+label")


# LAYOUT
app.layout = html.Div(
	style={
		"textAlign": "center",
	},
	children=[
		dcc.Graph(figure=table),
		dash_table.DataTable(
			data=dati2020.to_dict("records"),
			columns=[{"id": c, "name": c} for c in dati2020.columns],
		),
		dcc.Graph(figure=g1),
		dcc.Graph(figure=g2),
		dcc.Graph(figure=g4),
		dcc.Graph(figure=map),

		dcc.Loading(dcc.Graph(figure=animatedBarChart)),
		dcc.Graph(
			figure=pieChart,
		),
	],
)

app.run(debug=True)
