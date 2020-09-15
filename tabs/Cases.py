from stemmons.Stemmons_Dash import Stemmons_Dash_App
from stemmons import stemmons_dash_table as sdt
from stemmons import stemmons_dash_components as sdc
import urllib
import pandas as pd
from flask import request 
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash
from app import app
from bases.CasesDiv import Cases
from db.CaseCalls import CaseCalls

tabs = dbc.Tabs(
                [
                    dbc.Tab(label='Current', tab_id='Current'),
                    dbc.Tab(label='Lifetime', tab_id='Lifetime'),
                    #dbc.Tab(label='Relationships', tab_id='Relationships'),
      
                ],
                id='cases-tabs',
                active_tab='Current'
                
            )

layout = html.Div([
    tabs, 
    html.Div(id='content-cases'),
    html.Div(id='table-data', style={'display':'none'}),
    html.Div(id='sorted-data', style={'display':'none'}),
    html.Div(id='previous-header-clicks', style={'display':'none'})
])

@app.callback(
    [Output('content-cases','children'), Output('table-data','children')],
    [Input('cases-tabs','active_tab')]
)
def index(selection):
    user = request.cookies['user']
    cases = Cases(user)
    columns = ['Case ID', 'Case Title', 'Case Type', 'System Status', 'Due Status', 'Due Date', 'Created Date', 'Modified Date', 'Closed Date', 'Created By', 'Assigned To', 'Owner', 'Modified By']
    
    if selection == 'Current':
        #should look like cases.current(*args,**kwargs)
        children = cases.current()
        graphs = children[0]
        data = children[1]
        return html.Div([graphs, cases.case_list_table(columns)]), data.to_json(orient='split')   
        # if data.shape[0]>0 else None
        #return cases.current()

    elif selection == 'Lifetime':
        #should look like cases.lifetime(*args,**kwargs)
        return cases.lifetime(), None

    elif selection == 'Relationships':
        #should look like cases.relationships(*args,**kwargs)
        return 'Relationships'


@app.callback(
    [Output('sorted-data', 'children'), Output('previous-header-clicks', 'children')],
    [Input('table-data', 'children'), Input({'type': 'header', 'colname': ALL}, 'n_clicks'), Input({'type': 'header', 'colname': ALL}, 'id')],
    [State('previous-header-clicks', 'children')]
)
def sort_table_body(data, header_clicks, header_ids, previous_header_clicks):
    if data is None: raise dash.exceptions.PreventUpdate 
    data = pd.read_json(data, orient='split')
    data['Case Title'] = data.apply(lambda row: [row['Case Title'], row['Case URL']], axis=1)
    columns = ['Case ID', 'Case Title', 'Case Type', 'System Status', 'Due Status', 'Due Date', 'Created Date', 'Modified Date', 'Closed Date', 'Created By', 'Assigned To', 'Owner', 'Modified By']
    data = data[columns]
    data = sdt.sort_table(data, header_clicks, header_ids, previous_header_clicks, url_col=['Case Title'])
    return data.to_json(orient='split'), header_clicks

@app.callback(
    [Output('table-body', 'children'), Output('download-link-table', 'href')],
    [Input('sorted-data', 'children'), Input({'type': 'filter', 'colname': ALL}, 'value'), Input({'type': 'filter', 'colname': ALL}, 'id')]
)
def update_table_body(data, filter_values, filter_ids):
    if data is None: raise dash.exceptions.PreventUpdate
    data = pd.read_json(data, orient='split')
    data = sdt.filter_table(data, filter_values, filter_ids, url_col=['Case Title'])  
    download_csv = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(data.to_csv(index=False, encoding='utf-8'))
    return sdt.generate_table_body(data, url_col=['Case Title']), download_csv
