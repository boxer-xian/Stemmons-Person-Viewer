from tabs import Cases
from app import app, server
from stemmons.Stemmons_Dash import Stemmons_Dash_App

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash
from flask import request, session

#possible get the cookie 
app.server.secret_key = b'3gsm4bnR/qLz4rJXDZwtf21Oi+3FUXveVkNDxSq6hT/uUBnEfUn3dWn/oRRklFArfVj+bp3v5Y7ebwDhicrqbQ=='
@server.after_request
def user(req):
    user = request.cookies.get('byttTTojdr45', 'MarkF')
    req.set_cookie('user',user)
    #print(req.cookies['user'])
    return req


app.layout = html.Div(
    [html.Div([
        dcc.Interval(id='clock', max_intervals=1, interval=1),
        html.Div([html.Img(id='user-photo',
                        className='user-image')],
                        
                        className='user'),
            ############
            dbc.Tabs(
                [
                    dbc.Tab(label='Cases', tab_id='Cases'),
                    dbc.Tab(label='Entities', tab_id='Entites'),
                    #Every future page goes, here and must be added to the callback
                    #dbc.Tab(label='Quest', tab_id='Quest'),
                    
                ],
                id='tabs',
                active_tab='Cases',
                className='left-tabs'
            ),
        ##########
    ],className='left'),
    html.Div(
        [html.Div(id='content')],
     className='right'     
    )
    ],
    className='main'
)

@app.callback(Output('content', 'children'), 
             [Input('tabs', 'active_tab')])
def tabs(selected):

    if selected == 'Cases':
        return Cases.layout

    elif selected == 'Entites':
        return 'Entities.layout'
    
    #elif selected == 'Quest':
        #return 'Quest.layout'

@app.callback(Output('user-photo','src'),
                [Input('clock', 'n_intervals')])
def image(n_intervals):
    #print(n_intervals)
    if n_intervals == 1:
        user = request.cookies['user']
        #if production this should be pulled form teh db
        return f'http://services.boxerproperty.com/userphotos/DownloadPhoto.aspx?username={user}'
    else:
        raise dash.exceptions.PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True)