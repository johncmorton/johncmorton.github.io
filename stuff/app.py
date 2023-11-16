# First, import the necessary libraries
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import janitor

pattern = r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?)"
planets =       ['Mercury', 'Venus',   'Earth',   'Mars',    'Jupiter', 'Saturn',  'Uranus',  'Neptune']
planet_colors = ['#8d8d8d', '#d9b700', '#197ad9', '#d64c78', '#d45b00', '#ada6c1', '#6cd9b4', '#3759bf']
color_map = dict(zip(planets, planet_colors))




df = pd\
    .read_html("https://en.wikipedia.org/wiki/List_of_natural_satellites")[-2]\
    .drop(columns=["Image"])\
    .clean_names()\
    .assign(discovery_year=lambda x: pd.to_numeric(x['discovery_year'], errors='coerce'),
            year_announced=lambda x: pd.to_numeric(x['year_announced'], errors='coerce'),
            numeral=lambda x: pd.to_numeric(x['numeral'].str.extract('(\\d+)', expand=False), errors='coerce'),
            mean_radius_km=lambda x: pd.to_numeric(x['mean_radius_km_'].str.extract(pattern, expand=False).str.replace(',', ''), errors='coerce'),
            orbital_semi_km=lambda x: pd.to_numeric(x['orbital_semi_major_axis_km_'].str.extract(pattern, expand=False).str.replace(',', ''), errors='coerce'),
            sidereal_period=lambda x: pd.to_numeric(x['sidereal_period_d_r_=_retrograde_'].str.extract(pattern, expand=False).str.replace(',', ''), errors='coerce'))\
    .query("parent in @planets")\
    .assign(sorting_key = lambda x: x['parent'].map(lambda y: planets.index(y)))\
    .sort_values(by=['sorting_key', 'numeral'])\
    .drop(columns=['mean_radius_km_', 
                   'orbital_semi_major_axis_km_', 
                   'sidereal_period_d_r_=_retrograde_',
                   'ref_s_',
                   'sorting_key'])\
    .assign(discovery_year=lambda x: np.where(x['parent'] == 'Earth', 0, x['discovery_year']))


# Initialize the Dash app
app = dash.Dash(__name__)

years = np.linspace(1610, 2023, 20)


# Set up the layout of the app
app.layout = html.Div([

    html.Div([
    ], style={'width': '20%', 'margin': 'auto'}),

    html.Div([

        html.Label('Year of Discovery:'),
        dcc.Slider(
            id='year-slider',
            min=1600,
            max=max(years),
            value=min(years),
            marks={int(year): {'label': str(int(year)), 'style': {'transform': 'rotateY(0deg) rotate(45deg)'}} for year in years},
            included=True
        ),
        
        html.Div([
            dcc.Graph(id='moons-bar-chart', style={'display': 'inline-block', 'width': '50%'}),
            dcc.Graph(id='moons-donut-chart', style={'display': 'inline-block', 'width': '50%'})
        ]),
    ], style={'width': '60%', 'margin': 'auto'}),

    html.Div([
    ], style={'width': '20%', 'margin': 'auto'}),

])

# Callback to update both the bar chart and the donut chart
@app.callback(
    [Output('moons-bar-chart', 'figure'),
     Output('moons-donut-chart', 'figure')],
    [Input('year-slider', 'value')]
)
def update_figures(selected_year):
    # Filter the dataset based on the selected year from the slider

    
    filtered_df = df.query("discovery_year <= @selected_year")

    now_planets = filtered_df["parent"].unique()

    filtered_df= filtered_df.assign(parent=lambda x: pd.Categorical(x['parent'], categories=now_planets, ordered=True))
    
    
    # Create a summary dataframe for the bar chart that counts the number of moons per parent
    moon_counts = filtered_df.groupby('parent')['name'].count().reset_index(name='count')
    
    # Create the bar chart
    bar_fig = px\
        .bar(moon_counts, 
             x='parent', 
             y='count', 
             color='parent',
             text='count', 
             template="simple_white",
             color_discrete_map=color_map)\
        .update_traces(texttemplate='%{text}', 
                       textposition='outside',
                       showlegend=False)\
        .update_layout(
            title_text='Number of Moons<br>Discovered by Parent Planet',
            xaxis=dict(title=''),
            yaxis=dict(title='Number of Moons', visible=False),
            legend_title = '',            
            transition_duration=300)
    
    # Create a summary dataframe for the donut chart that counts the number of moons per parent
    moon_counts_donut = filtered_df['parent'].value_counts().reset_index(name='count')
    moon_counts_donut.columns = ['parent', 'count']
    
    # Create the donut chart
    donut_fig = px\
        .pie(moon_counts_donut, 
             names='parent', 
             values='count', 
             hole=0.5,
             color='parent',
             color_discrete_map=color_map)\
        .update_traces(textinfo='percent+label',
                       showlegend=False)\
        .update_layout(
            title_text='Distribution of Moons<br>Discovered by Parent Planet',
            transition_duration=500)
        
    
    return bar_fig, donut_fig




# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
