from tabs import Cases, Application
from db.EntityCalls import EntityCalls
from app import app, server
from stemmons.Stemmons_Dash import Stemmons_Dash_App

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash
from flask import request, session, make_response

server = app.server

#possible get the cookie 
app.server.secret_key = b'3gsm4bnR/qLz4rJXDZwtf21Oi+3FUXveVkNDxSq6hT/uUBnEfUn3dWn/oRRklFArfVj+bp3v5Y7ebwDhicrqbQ=='
@server.after_request
def cookie_user(req):
    user = request.cookies.get('byttTTojdr45', '')
    req.set_cookie('user', user)
    return req

"""@server.route('/')
def args():
   username = request.args.get('User')
   print ('username', username)
   return "username: {}".format(username)"""


app.layout = html.Div(
    [
        html.Div(
            [
                #dcc.Interval(id='clock', max_intervals=1, interval=1),
                html.Div(
                    [html.Img(id='user-photo', className='user-image')],
                    className='user'
                ),
                ############
                dbc.Tabs(
                    [
                        dbc.Tab(label='Cases', tab_id='Cases'),
                        #dbc.Tab(label='Entities', tab_id='Entites'),
                        #Every future page goes, here and must be added to the callback
                        #dbc.Tab(label='Quest', tab_id='Quest'),
                        
                    ],
                    id='tabs',
                    active_tab='Cases',
                    className='left-tabs'
                ),
                ##########
            ], 
        className='left'
        ),

        html.Div(
            [html.Div(id='content')],
            className='right'     
        ),

        dcc.Store(id='param_user', storage_type='session'),
        dcc.Location(id='url', refresh=False),
    ],
    className='main'
)


''' 
url like: ./Username
store username in session storage, diffrent users' pages could be opened at the same time
if use cookie, can only open one person's page at one time '''
'''@app.callback(
    Output('param_user', 'data'),
    #[Input('url', 'pathname')])
    [Input('url', 'search')])
def user(pathname):
    print (pathname)
    pathname = str(pathname)
    user = request.cookies['user']

    if pathname.startswith('/'):
        param = pathname.split('/')[-1]
        if len(param)>0:
            user = param
    #print ('\npathname:', pathname, user)
    return user'''


''' 
url like: ./?username=user
store username in session storage, diffrent users' pages could be opened at the same time
if use cookie, can only open one person's page at one time '''
@app.callback(
    Output('param_user', 'data'),
    [Input('url', 'search')])
def user(search):
    print (search)
    search = str(search)
    user = request.cookies['user']

    if search.startswith('?'):
        user = search.split('username=')[1]
    print (user)
    return user



@app.callback(
    Output('tabs', 'children'), #Output('application_id', 'children')],
    [Input('param_user', 'data')],
    [State('tabs', 'children')]
)
def add_tabs(user, tabs):
    if user is None:
        raise dash.exceptions.PreventUpdate
    
    application_id = EntityCalls().user_application(user)
    #print (application_id)
    if len(application_id)>0:
        tabs.append(dbc.Tab(label='Application', tab_id='Application'))
        
    return tabs
    #, application_id
    



@app.callback(Output('content', 'children'), 
             [Input('tabs', 'active_tab')])   #, Input('application_id', 'children')
def tabs(selected):

    if selected == 'Cases':
        return Cases.layout

    elif selected == 'Entites':
        return 'Entities.layout'
    
    elif selected == 'Application':
        return Application.layout


"""@app.callback(
    Output('user-photo', 'src'),
    [Input('clock', 'n_intervals')])
def image(n_intervals):
    #print(n_intervals)
    if n_intervals == 1:
        user = request.cookies['user']
        #if production this should be pulled form teh db
        return f'http://services.boxerproperty.com/userphotos/DownloadPhoto.aspx?username={user}'
    else:
        raise dash.exceptions.PreventUpdate"""

@app.callback(
    Output('user-photo', 'src'),
    [Input('param_user', 'data')])
def image(user):
    if user is not None: 
        #if production this should be pulled form teh db
        return f'http://services.boxerproperty.com/userphotos/DownloadPhoto.aspx?username={user}'
        #print ('image:', user)
    else:
        raise dash.exceptions.PreventUpdate
        


if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(debug=False, host='192.168.0.147', port='8055')

    
