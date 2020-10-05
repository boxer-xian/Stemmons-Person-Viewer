from app import app
from db.EntityCalls import EntityCalls
from stemmons import stemmons_dash_components as sdc

import urllib
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash



layout = html.Div(id='application-content')

@app.callback(
    Output('application-content', 'children'),
    [Input('param_user', 'data')]
)
def index(user):
    if user is None:
        raise dash.exceptions.PreventUpdate

    application_id = EntityCalls().user_application(user)
    url = 'http://cases.boxerproperty.com/AppSearch/?SearchID='
    items = []
    for i in application_id:
        title = EntityCalls().entity_title(i)
        
        file_id = EntityCalls().application_icon(i)
        icon_src = 'http://entities.boxerproperty.com//Download.aspx?FileID='+str(file_id)

        item = html.Div(
            html.Div([
                html.Div(
                    html.A(html.Img(src=icon_src, className='Application-img'), href=url+str(i), target='_blank'),
                    className='font-icon-wrapper AppBackgroundCover'),

                html.Div(html.A(title, href=url+str(i), target='_blank'), className='Application-img-text')
            ]),
            className='App-image-render'
        )
        items.append(item)

    return dbc.Row(items)