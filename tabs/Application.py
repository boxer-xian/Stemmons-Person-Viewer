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
    titles = EntityCalls().entity_title(application_id)
    icons = EntityCalls().application_icon(application_id)
    data = pd.merge(titles[['ENTITY_ID', 'TEXT']], icons[['ENTITY_ID', 'ENTITY_FILE_ID']], on='ENTITY_ID').sort_values(['TEXT']).reset_index(drop=True)
    
    url = 'http://cases.boxerproperty.com/AppSearch/?SearchID='
    items = []
    #for i in application_id:
    for i in range(len(data)):
        search_id = data.loc[i, 'ENTITY_ID']
        search_url = url+str(search_id)
        app_name = data.loc[i, 'TEXT']
        file_id = data.loc[i, 'ENTITY_FILE_ID']
        icon_src = 'http://entities.boxerproperty.com//Download.aspx?FileID='+str(file_id)

        item = icon_div(search_url, app_name, icon_src)
        items.append(item)

    return dbc.Row(items)


def icon_div(search_url, app_name, icon_src):
    return html.Div(
        html.Div([
            html.Div(
                html.A(html.Img(src=icon_src, className='Application-img'), href=search_url, target='_blank'),
                className='font-icon-wrapper AppBackgroundCover'),

            html.Div(html.A(app_name, href=search_url, target='_blank'), className='Application-img-text')
        ]),
        className='App-image-render'
    )