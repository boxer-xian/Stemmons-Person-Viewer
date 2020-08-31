from stemmons.Stemmons_Dash import Stemmons_Dash_App
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_bootstrap_components as dbc
from app import app

tabs = dbc.Tabs(
                [
                    dbc.Tab(label='Current', tab_id='Current'),
                    dbc.Tab(label='Lifetime', tab_id='Lifetime'),
                    dbc.Tab(label='Relationships', tab_id='Relationships'),
      
                ],
                id='cases-tabs',
                active_tab='Current'
                
            )

layout = html.Div([tabs, html.Div(id='content-cases')])

@app.callback( Output('content-cases','children'),
            [Input('cases-tabs','active_tab')])
def index(selection):
    print(selection)
    if selection == 'Current':
        #should look like Cases().current(*args,**kwargs)
        return 'Current'

    elif selection == 'Lifetime':
        #should look like Cases().lifetime(*args,**kwargs)
        return 'Livetime'

    elif selection == 'Relationships':
        #should look like Cases().relationships(*args,**kwargs)
        return 'Relationships'
