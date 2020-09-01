from stemmons.Stemmons_Dash import Stemmons_Dash_App
from flask import request 
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash
from app import app
from bases.CasesDiv import Cases

tabs = dbc.Tabs(
                [
                    dbc.Tab(label='Current', tab_id='Current'),
                    dbc.Tab(label='Lifetime', tab_id='Lifetime'),
                    #dbc.Tab(label='Relationships', tab_id='Relationships'),
      
                ],
                id='cases-tabs',
                active_tab='Current'
                
            )

layout = html.Div([tabs, html.Div(id='content-cases')])

@app.callback( Output('content-cases','children'),
            [Input('cases-tabs','active_tab')])
def index(selection):
    user = request.cookies['user']
    
    cases = Cases(user)
    if selection == 'Current':
        #should look like cases.current(*args,**kwargs)
        return 'Current ' + user

    elif selection == 'Lifetime':
        #should look like cases.lifetime(*args,**kwargs)
        return 'Livetime'

    elif selection == 'Relationships':
        #should look like cases.relationships(*args,**kwargs)
        return 'Relationships'

    