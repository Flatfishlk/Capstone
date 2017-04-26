import plotly
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.offline as offline
import plotly.plotly as py
import pandas as pd
import numpy as np

def trade_count(df):
    for i in range(len(df)):
        pair = '-'.join(s for s in sorted([df['Importer'].iloc[i],df['Exporter'].iloc[i]]))
        df.loc[i,'pair'] = pair
    return df.groupby(['Year', 'pair'],as_index=False).sum()

def clean_country(df, lst):
    for i in lst:
        return df.drop(df[df['P1']==i].index)

def world_map(df, year):
    country = [ dict(
        type = 'scattergeo',
        lon = df_ref['longitude'],
        lat = df_ref['latitude'],
        hoverinfo = 'text',
        text = df_ref['Name'],
        mode = 'markers',
        marker = dict(
            size=2,
            color='rgb(255, 0, 0)',
            line = dict(
                width=3,
                color='rgba(68, 68, 68, 0)'
            )
        ))]

        edge_paths = []
    for i in range( len( df ) ):
        edge_paths.append(
            dict(
                type = 'scattergeo',
                lon = [ df['long1'][i], df['long2'][i] ],
                lat = [ df['lat1'][i], df['lat2'][i] ],
                mode = 'lines',
                line = dict(
                    width = 1,
                    color = 'red',
                ),
                opacity = float(df['Vol'][i])/float(df['Vol'].max()),
            )
        )

    layout = dict(
            title = '%d Animal Trade Network' % year,
            showlegend = False,
            geo = dict(
                projection=dict( type='equirectangular' ),
                showland = True,
                landcolor = 'rgb(243, 243, 243)',
                countrycolor = 'rgb(204, 204, 204)',
            ),
        )

    fig = dict( data=edge_paths + country, layout=layout )
    offline.iplot( fig, filename='trade')



if __name__ == '__main__':
    df = pd.read_csv('trade_complete.csv')
    df_ref = pd.read_csv('joined_country_lat_lon.csv')
### take only year, improter, exporter information
    df_trade = df[['Year','Importer','Exporter','Unnamed: 0']]
    df_trade = df_trade.rename(index=str, columns={"Unnamed: 0": "Vol"})
    df_trade = df_trade.dropna()
    df_groupby = df_trade.groupby(['Year','Importer','Exporter'],as_index=False).count()
### find number of trade for every pair of trade partners by year
    df_pair = trade_count(df_groupby)
### split importers and exporters and add back to original df_pair
    df_split = pd.DataFrame(df_pair.pair.str.split('-',1).tolist(),columns = ['P1','P2'])
    df_concat = pd.concat([df_pair, df_split], axis = 1)
### clean unwanted clean_country
    country_list = ['XX','XV','ZZ']
    df_clean = clean_country(df_concat,country_list)
### get lat and long information for each importer and exporter
    df_clean = df_clean.rename(index=str, columns={"P1": "country"})
    df_lat_long = df_clean.merge(df_ref, on='country', how='left')
    df_lat_long = df_lat_long[['Year','pair','Vol','country','P2','latitude','longitude']]
    df_lat_long = df_lat_long.rename(index=str, columns={'country':'country1','P2':'country','latitude':'lat1', 'longitude':'long1'})
    df_lat_long = df_lat_long.merge(df_ref, on='country', how='left')
    df_lat_long = df_lat_long[['Year','pair','Vol','country1','country','lat1','long1','latitude','longitude']]
    df_lat_long = df_lat_long.rename(index=str, columns={'country':'country2','latitude':'lat2','longitude':'long2'})
### print world map based on year
    df_1975 = df_lat_long[df_lat_long['Year']==1975]
    world_map(df_1975, 1975)
    df_1975 = df_lat_long[df_lat_long['Year']==1995]
    world_map(df_1995, 1995)
    df_1975 = df_lat_long[df_lat_long['Year']==2015]
    world_map(df_2015, 2015)
