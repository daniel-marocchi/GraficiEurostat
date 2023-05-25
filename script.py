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
dati.columns=['Unità', 'Attività', 'Nazione', 'Anno','Numero Incidenti']
dati2020 = dati.query("Anno == 2020")

#-----------------------------------------------------------------------------------------------------------------------------

#Grafici Animati

graficoPunti = px.scatter(
	dati,
	x="Nazione",
	y="Numero Incidenti",
  color="Numero Incidenti",
  animation_frame="Anno",
	animation_group="Nazione",
  height=1000,
  color_continuous_scale="sunsetdark"
)
graficoPunti.update_traces(marker_size=30)

#Grafico a Barre Animato
animatedBarChart = px.bar(
	dati,
	x="Nazione",
	y="Numero Incidenti",
	animation_frame="Anno",
	animation_group="Nazione",
	color="Numero Incidenti",
	height=1300,
	color_continuous_scale="sunsetdark",
	range_y=[0, 5000],
	hover_data="Numero Incidenti",
	hover_name="Nazione",
)


#-----------------------------------------------------------------------------------------------------------------------------


#App Layout
app.layout = html.Div(
	children=[
    html.H1('Incidenti sul Lavoro', style={
      'textAlign' : 'center',
      'fontSize' : '8rem',
      'padding' : '3rem',
      'marginBottom' : '6rem'
    }),
    dcc.Slider(
      dati['Anno'].min(),
      dati['Anno'].max(),
      step=1,
      id='yearSlider',
      tooltip={
        'always_visible':True 
      },
      value=dati["Anno"].max(),
      marks={str(year): str(year) for year in dati['Anno'].unique()},
    ),
		
		dash_table.DataTable(
      columns=[{"id": c, "name": c} for c in dati.drop(columns=['Attività', 'Unità', 'Anno']).columns],
      style_header={
        'fontSize' : 35,
        'fontWeight': '300',
        'textTransform' : 'upperCase',
        'padding' : '16px 0px',
        'backgroundColor' : '#1c1c1c',
      },
      style_cell={'textAlign': 'center', 
        'fontSize' : 20,
        'fontFamily' : 'Arial',
        'padding' : '10px 0px',
        'backgroundColor' : '#111111'
      },
      style_table={
        'margin' : '10rem 0px',
      },
      #style_as_list_view=True,
      id='table'),
		dcc.Graph(id='staticBarChart', style={
      'margin' : '10rem 0px'
    }),
		dcc.Graph(id='pieChart'),
		dcc.Graph(id='choroplethMapbox', style={
      'margin' : '10rem 0px'
    }),
		dcc.Graph(id='globe', style={
      'margin' : '10rem 0px'
    }),
    dcc.Graph(figure=animatedBarChart, style={
      'margin' : '10rem 0px'
    }),
		dcc.Graph(figure=graficoPunti, style={
      'margin' : '10rem 0px'
    })
	]
)

#-----------------------------------------------------------------------------------------------------------------------------

#Funzioni di Callback
#Aggiorno Grafico a Barre Statico
@app.callback(
  Output('staticBarChart', 'figure'),
  Input('yearSlider', 'value')
)
def updateStaticBarChart(annoSelezionato):
  datiFiltrati = dati.query('Anno == '+ str(annoSelezionato))
  
  staticBarChart = px.bar(
    data_frame=datiFiltrati, 
    x="Nazione", 
    y="Numero Incidenti",
    height=1000,
    hover_name='Nazione',
    hover_data=['Numero Incidenti', 'Anno'],
    color_continuous_scale="sunsetdark",
    color='Numero Incidenti',
  )

  staticBarChart.update_layout(transition_duration=500)

  return staticBarChart

#Aggiorno Tabella
@app.callback(
  Output('table', 'data'),
  Input('yearSlider', 'value')
)
def updateTable(annoSelezionato):
  datiFiltrati = dati.query('Anno == '+ str(annoSelezionato))
  data=datiFiltrati.to_dict("records")

  return data


#Update Grafico a Torta
@app.callback(
  Output('pieChart', 'figure'),
  Input('yearSlider', 'value')
)
def updatePieChart(annoSelezionato):
  datiFiltrati = dati.query('Anno == '+ str(annoSelezionato))
  pieChart = px.pie(
    datiFiltrati,
    names="Nazione",
    values="Numero Incidenti",
    height=1000,
    hover_name="Nazione",
    hover_data=['Numero Incidenti']
  )

  pieChart.update_traces(textposition="inside", textinfo="text+label")

  return pieChart


#Update Globo
@app.callback(
  Output('globe', 'figure'),
  Input('yearSlider', 'value')
)
def updateGlobe(annoSelezionato):
  datiFiltrati = dati.query('Anno == '+ str(annoSelezionato))
    
  globe = px.choropleth(
    datiFiltrati
    .query("Nazione != 'European Union - 27 countries (from 2020)'")
    .query("Nazione != 'European Union - 28 countries (2013-2020)'")
    .query("Nazione != 'European Union - 27 countries (2007-2013)'")
    .query("Nazione != 'European Union - 15 countries (1995-2004)'"),
    color="Numero Incidenti",
    geojson=EuropeGeoJSON,
    locations="Nazione",
    hover_name="Nazione",
    hover_data=['Numero Incidenti', 'Anno'],
    locationmode="country names",
    height=1800,
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

  globe.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

  return globe


#Update Mappa
@app.callback(
  Output('choroplethMapbox', 'figure'),
  Input('yearSlider', 'value')
)
def updateChoroplethMapbox(annoSelezionato):
  datiFiltrati = dati.query('Anno == '+ str(annoSelezionato))
  
  choroplethMap = px.choropleth_mapbox(
	datiFiltrati
    .query("Nazione != 'European Union - 27 countries (from 2020)'")
    .query("Nazione != 'European Union - 28 countries (2013-2020)'")
    .query("Nazione != 'European Union - 27 countries (2007-2013)'")
    .query("Nazione != 'European Union - 15 countries (1995-2004)'"),
  geojson=EuropeGeoJSON,
	locations="Nazione",
  featureidkey="properties.NAME",
	mapbox_style="carto-darkmatter",
	center={"lat": 45.891031, "lon": 10.8638110},
	zoom=3,
	height=1300,
	color="Numero Incidenti",
  color_continuous_scale="sunsetdark",
  hover_name="Nazione",
  hover_data=['Numero Incidenti', 'Anno'],
  ) 

  return choroplethMap


app.run(debug=True)