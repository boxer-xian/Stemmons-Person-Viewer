from stemmons.Stemmons_Dash import Stemmons_Dash_App
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_bootstrap_components as dbc
from app import app

tabs = dbc.Tabs(
                [
                    dbc.Tab(label='Entites', tab_id='Entities'),
      
                ],
                id='entity-tabs',
                active_tab='Current'
                
            )

layout = html.Div([tabs, html.Div(id='content-entity')])

@app.callback( Output('content-entity','children'),
            [Input('entity-tabs','active_tab')])
def ind(selection):
    print(selection)
    if selection == 'Entities':
        return 'Entity'

   
