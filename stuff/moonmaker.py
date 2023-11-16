# First, import the necessary libraries
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

df.to_csv('moons.csv', index=False)