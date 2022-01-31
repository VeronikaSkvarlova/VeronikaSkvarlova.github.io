# -*- coding: utf-8 -*-
from dash import Dash
from dash import dcc
from dash import html
from plotly.graph_objects import Figure, Scattergeo, Bar
from pandas import read_csv
from plotly.express import pie
from dash.dependencies import Input, Output  

app = Dash() # initializing dash app

server = app.server

trip_a = read_csv('tripadvisor_european_restaurants.csv', dtype={"restaurant_link": "string", "restaurant_name": "string",
                                                                    "original_location": "string", "country": "string",
                                                                    "region": "string", "province": "string"})

# if there are multiple values in a column, separate them and add them to a list
def get_all_items(lst):
    all_items = []
    for item in lst:
        if type(item) == str:
            item = item.split(',')
            for sth in item:
                if sth.strip() not in all_items:
                    all_items.append(sth.strip())
    return all_items

all_countries = trip_a['country'].unique() # get names of all countries in dataset

meals = trip_a['meals'].unique()
cuisines = trip_a['cuisines'].unique()

all_meals = get_all_items(meals)
all_cuisines = get_all_items(cuisines)

fig = Figure(data=Scattergeo())
fig.update_layout(geo_scope='europe')

app.layout = html.Div(children=[
   html.H1(children='Trip advisor european restaurants'),
   dcc.Dropdown( id = 'dropdown_country',
        style={"width": "40%"},
        options = [{'label':country, 'value': country} for country in sorted(all_countries)],
        value = '',
        placeholder="Select a country"),
    html.Div([
        dcc.Dropdown(
        id = 'region',
        style={"width": "40%"},
        options=[],
        value ='',
        placeholder="Select a region"
        )
    ], style= {'display': 'block'} # only show region selection after the country had been chosen
    ),
    html.Div([
        dcc.Dropdown(
        id = 'province',
        style={"width": "40%"},
        options=[],
        value = '',
        placeholder="Select a province"
        )
    ], style= {'display': 'block'}
    ),
    html.Div([
        dcc.Dropdown(
        id = 'city',
        style={"width": "40%"},
        options=[],
        value = '',
        placeholder="Select a city"
        )
    ], style= {'display': 'block'}
    ),
    dcc.RadioItems( id = 'vegetarian',
        options=[
            {'label': 'Vegetarian friendly', 'value': 'Y'},
            {'label': 'Doesn\'t matter', 'value': 'N'}
        ],
        value='N'
    ),
    dcc.RadioItems( id = 'vegan',
        options=[
            {'label': 'Vegan options', 'value': 'Y'},
            {'label': 'Doesn\'t matter', 'value': 'N'}
        ],
        value='N'
    ),
    dcc.RadioItems( id = 'gluten',
        options=[
            {'label': 'Gluten-free', 'value': 'Y'},
            {'label': 'Doesn\'t matter', 'value': 'N'}
        ],
        value='N'
    ),
    html.Div([
        dcc.RangeSlider(
        id = 'avg_rating',
        min=1,
        max=5,
        value=[1, 5],
        step=None,
        marks={
            1: 'Avg rating: 1',
            1.5: '1.5',
            2: '2',
            2.5: '2.5',
            3: '3',
            3.5: '3.5',
            4: '4',
            4.5: '4.5',
            5: '5'
        })
    ], style= {'width': '30%'}
    ),
    dcc.Dropdown(
        id = 'meals',
        style={"width": "40%"},
        options=[{'label': m, 'value': m} for m in sorted(all_meals)],
        value = [],
        placeholder="Choose meal types",
        multi=True
    ),
    dcc.Dropdown(
        id = 'cuisines',
        style={"width": "40%"},
        options=[ {'label': m, 'value': m} for m in sorted(all_cuisines) ],
        value = ['Europe'],
        placeholder="Choose cuisines",
        multi=True
    ),
   dcc.Graph(
        id='scatter_geo',
        style={'display': 'inline-block','vertical-align': 'top','width': '33%'}
   ),
   dcc.Graph(
        id="pie_chart",
        style={'display': 'inline-block','vertical-align': 'top','width': '33%'}),
   dcc.Graph(
        id='bar_chart',
        style={'display': 'inline-block','vertical-align': 'top','width': '33%'})
])

@app.callback(Output(component_id='scatter_geo', component_property= 'figure'),
              Input(component_id='dropdown_country', component_property='value'),
              Input(component_id='region', component_property= 'value'),
              Input(component_id='province', component_property= 'value'),
              Input(component_id='city', component_property= 'value'),
              Input(component_id='vegetarian', component_property='value'),
              Input(component_id='vegan', component_property='value'),
              Input(component_id='gluten', component_property='value'),
              Input(component_id='meals', component_property='value'),
              Input(component_id='cuisines', component_property='value'),
              Input('avg_rating', 'value'))
def graph_update(country, region, province, city, vegetarian, vegan, gluten, meals, cuisines, rating):
    cond_country = trip_a['country'] == country 
    cond_region = trip_a['region'] == region if region != '' else True
    cond_province = trip_a['province'] == province if province != '' else True
    cond_city = trip_a['city'] == city if city != '' else True
    cond_vegetarian = trip_a['vegetarian_friendly'] == vegetarian
    cond_vegan = trip_a['vegan_options'] == vegan
    cond_gluten = trip_a['gluten_free'] == gluten
    cond_rating = (trip_a['avg_rating'] >= rating[0]) & (trip_a['avg_rating'] <= rating[1])
    cond_meal = True
    for m in meals:
        cond_meal = (cond_meal) & (trip_a['meals'].str.contains(m))
    cond_cuisine = True
    for c in cuisines:
        cond_cuisine = (cond_cuisine) & (trip_a['cuisines'].str.contains(c))
    condition = cond_country & cond_region & cond_province & cond_city & cond_vegetarian & cond_vegan & cond_gluten & cond_rating & cond_meal & cond_cuisine
    fig = Figure([
        Scattergeo(
            lon = trip_a.loc[condition]['longitude'],
            lat = trip_a.loc[condition]['latitude'],
            text = trip_a.loc[condition]['restaurant_name'].astype(str) + "; " + trip_a.loc[condition]['address'].astype(str),
            marker = dict(
            color = trip_a.loc[condition]['avg_rating'],
            size = 5,
            colorbar = dict(
                    titleside = "right",
                    outlinecolor = "rgba(68, 68, 68, 0)",
                    ticks = "outside",
                    showticksuffix = "last",
                    dtick = 0.5
            ),
        )
        )])
    fig.update_layout(geo_scope='europe')
    return fig 

@app.callback(
   Output(component_id='region', component_property='style'),
   [Input(component_id='dropdown_country', component_property='value')])
def show_hide_region(value):
    if value != '':
        return {'display': 'block', "width": "40%"}
    if value == '':
        return {'display': 'none'}

@app.callback(
   Output(component_id='province', component_property='style'),
   [Input(component_id='region', component_property='value')])
def show_hide_province(value):
    if value != '':
        return {'display': 'block', "width": "40%"}
    if value == '':
        return {'display': 'none'}

@app.callback(
   Output(component_id='city', component_property='style'),
   [Input(component_id='province', component_property='value')])
def show_hide_element(value):
    if value != '':
        return {'display': 'block', "width": "40%"}
    if value == '':
        return {'display': 'none'}

@app.callback(
    Output('region', 'options'),
    Output('region', 'value'),
    [Input('dropdown_country', 'value')])
def update_region_dropdown(country):
    regions = trip_a.loc[trip_a['country'] == country, 'region']
    regions = regions.dropna()
    all_regions = []
    for region in regions:
        if region and region not in all_regions:
            all_regions.append(region)
    return [{'label': i, 'value': i} for i in sorted(all_regions)], ''

@app.callback(
    Output('province', 'options'),
    Output('province', 'value'),
    [Input('region', 'value')])
def update_province_dropdown(region):
    provinces = trip_a.loc[trip_a['region'] == region, 'province']
    provinces = provinces.dropna()
    all_provinces = []
    for province in provinces:
        if province and province not in all_provinces:
            all_provinces.append(province)
    return [{'label': i, 'value': i} for i in sorted(all_provinces)], ''

@app.callback(
    Output('city', 'options'),
    Output('city', 'value'),
    [Input('province', 'value')])
def update_province_dropdown(province):
    cities = trip_a.loc[trip_a['province'] == province, 'city']
    cities = cities.dropna()
    all_cities = []
    for city in cities:
        if city and city not in all_cities:
            all_cities.append(city)
    return [{'label': i, 'value': i} for i in sorted(all_cities)], ''

@app.callback(
        Output('pie_chart', 'figure'),
        [Input('scatter_geo', 'clickData')])
def upadte_pie_chart(selection):
    if selection is None:
        return {"layout": {"xaxis": {"visible": False},
                           "yaxis": {"visible": False},
                "annotations": [{
                    "text": "No matching data found",
                    "showarrow": False,
                    "font": {"size": 28}
                }]
            }
        }
    else:
        names = ['Excellent', 'Very good', 'Average', 'Poor', 'Terrible']
        longitude = selection['points'][0]['lon']
        latitude = selection['points'][0]['lat']
        restaurant = trip_a.loc[(trip_a['longitude'] == longitude) & (trip_a['latitude'] == latitude)]

        data = [restaurant['excellent'].values[0], restaurant['very_good'].values[0], restaurant['average'].values[0],
        restaurant['poor'].values[0], restaurant['terrible'].values[0]]

        fig = pie(values=data, names=names, title='Reviews count in default language')
        return fig
    
@app.callback(
    Output("bar_chart", "figure"), 
    [Input('scatter_geo', 'clickData')])
def update_bar_chart(selection):
    if selection is None:
        return {"layout": {"xaxis": {"visible": False},
                           "yaxis": {"visible": False},
                "annotations": [{
                    "text": "No matching data found",
                    "showarrow": False,
                    "font": {"size": 28}
                }]
            }
        }
    else:
        names = ['Food', 'Service', 'Value', 'Atmosphere']
        longitude = selection['points'][0]['lon']
        latitude = selection['points'][0]['lat']
        restaurant = trip_a.loc[(trip_a['longitude'] == longitude) & (trip_a['latitude'] == latitude)]

        data = [restaurant['food'].values[0], restaurant['service'].values[0], restaurant['value'].values[0], restaurant['atmosphere'].values[0]]

        fig = Figure([Bar(x=names, y=data)])
        fig.update_layout(yaxis_range=[1,5], title="Food, service, value and atmosphere rating")
        return fig
    
if __name__ == '__main__':
   app.run_server(debug=False)