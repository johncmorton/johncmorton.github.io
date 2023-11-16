# First, import the necessary libraries
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import janitor
import os
os.chdir(os.path.dirname(__file__))



pattern = r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?)"
planets =       ['Mercury', 'Venus',   'Earth',   'Mars',    'Jupiter', 'Saturn',  'Uranus',  'Neptune']
planet_colors = ['#8d8d8d', '#d9b700', '#197ad9', '#d64c78', '#d45b00', '#ada6c1', '#6cd9b4', '#3759bf']
color_map = dict(zip(planets, planet_colors))

df = pd.read_csv('moons.csv')

fig = px\
    .area(
        x=df['discovery_year'].value_counts().sort_index().index, 
        y=df['discovery_year'].value_counts().sort_index().cumsum().values, 
        template="simple_white",
        color_discrete_sequence=['#197ad9'],
        # log_y=True,
        labels={'x': 'Year of Discovery', 'y': 'Number of Moons Discovered'},
        title='Number of Moons Discovered Over Time')\
    .update_xaxes(range=[1610, 2023])


# Initialize the Dash app
app = dash.Dash(__name__)

years = np.linspace(1610, 2023, 20)


# Set up the layout of the app
app.layout = html.Div([

    html.Div([
    ], style={'width': '20%', 'margin': 'auto'}),



    html.Div([

        html.H1('Moons of the Solar System', style={'textAlign': 'center'}),

        html.Br(),

        html.P('This dashboard displays information about the moons of the solar system. Use the slider to filter the data by year of discovery. The bar chart shows the number of moons discovered by each parent planet. The donut chart shows the distribution of moons discovered by parent planet.'),

        html.Hr(),

        html.Br(),

        html.H2('Interactive Table', style={'textAlign': 'center'}),

        dcc.Dropdown(
            id='column-selector',
            options=[{'label': col, 'value': col} for col in df.columns],
            multi=True,
            value=["name","parent", "discovery_year"]  # Default to all columns
        ),

        html.Br(),

        dash_table.DataTable(
            id='data-table',
            data=df.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df.columns],
            page_size=10,
            sort_action='native',

            style_cell={
                'fontFamily': 'Arial, sans-serif',
                'fontSize': '14px',
                'textAlign': 'left',
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['Date', 'Region']
            ],
            style_data={
                'color': 'black',
                'backgroundColor': 'white',
                'border': 'none'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(240, 240, 240)',
                }
            ],
            style_header={
                'backgroundColor': 'darkblue',
                'color': 'white',
                'fontWeight': 'bold',
                'border': 'black',
            },
            style_table={
                'overflowX': 'auto',
                'minWidth': '100%',
            },
            css=[{
                'selector': '.dash-spreadsheet-container .dash-spreadsheet-inner *',
                'rule': 'font-family: Arial, sans-serif;'
            }],
        ),

        html.Br(),

        html.H2('Interactive Plotly Chart', style={'textAlign': 'center'}),

        html.Br(),

        dcc.Graph(figure=fig, style={'width': '100%', 'height': '50%'}),

        html.Br(),

        html.H2('Charts with Callbacks', style={'textAlign': 'center'}),


        html.P('Year of Discovery:'),
        dcc.Slider(
            id='year-slider',
            min=1600,
            max=max(years),
            value=min(years),
            marks={int(year): {'label': str(int(year)), 'style': {'transform': 'rotateY(0deg) rotate(45deg)'}} for year in years},
            included=True
        ),

        html.Br(),
        
        html.Div([
            dcc.Graph(id='moons-bar-chart', style={'display': 'inline-block', 'width': '50%'}),
            dcc.Graph(id='moons-donut-chart', style={'display': 'inline-block', 'width': '50%'})
        ]),
    ], style={'width': '60%', 'margin': 'auto'}),

    html.Div([
    ], style={'width': '20%', 'margin': 'auto'}),

], style={'width': '100%', 'margin': 'auto','margin': '0', 'backgroundColor': 'white'})


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

@app.callback(
    Output('data-table', 'columns'),
    Input('column-selector', 'value')
)
def update_table(selected_columns):
    if selected_columns is None or not selected_columns:
        # If no columns are selected, display all columns
        return [{"name": i, "id": i} for i in df.columns]
    else:
        # Display only the selected columns
        return [{"name": i, "id": i} for i in selected_columns]



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
