from app import app
from bases.CasesDiv import Cases
from db.CaseCalls import CaseCalls
from handler.CaseHandler import CaseHandler
from stemmons.Stemmons_Dash import Stemmons_Dash_App
#from stemmons 
import stemmons_dash_table as sdt
from stemmons import stemmons_dash_components as sdc

import urllib
import pandas as pd
from flask import request 
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash


tabs = dbc.Tabs(
                [
                    dbc.Tab(label='Current', tab_id='Current'),
                    dbc.Tab(label='Lifetime', tab_id='Lifetime'),
                    #dbc.Tab(label='Hopper', tab_id='Hopper'),
                    #dbc.Tab(label='Team', tab_id='Team'),
                    #dbc.Tab(label='Relationships', tab_id='Relationships'),
      
                ],
                id='cases-tabs',
                active_tab='Current'
                
            )


columns = ['Case ID', 'Case Title', 'Case Type', 'System Status', 'Due Status', 'Due Date', 'Created Date', 
           'Last Modified Date', 'Closed Date', 'Case Life Days', 'Created By', 'Assigned To', 'Owner', 'Last Modified By']



layout = html.Div([
    tabs, 
    dbc.Spinner(id='content-1-cases'),
    html.Div(id='content-2-cases'),
    dcc.Interval(id='clock-cases', max_intervals=1, interval=1),

    
    dcc.Store(id='user-cases', storage_type='memory'),
    dcc.Store(id='hopper-cases', storage_type='memory'),
    dcc.Store(id='team-cases', storage_type='memory'),

    # used for sharing data between callbacks
    html.Div(id='table-data', style={'display':'none'}),
    html.Div(id='filtered-data', style={'display':'none'}),
    html.Div(id='sorted-data', style={'display':'none'}),
    html.Div(id='previous-header-clicks', style={'display':'none'})
])



    #user = request.cookies['user']
    #cases = Cases(user) 


@app.callback(
    Output('cases-tabs', 'children'),
    [Input('clock-cases', 'n_intervals')],
    [State('cases-tabs', 'children')]
)
def append_tabs(n_intervals, cases_tabs):
    #print(n_intervals)
    if n_intervals != 1:
        return dash.exceptions.PreventUpdate

    user = request.cookies['user']
    #print ('user', user)

    hoppers = CaseCalls().query_hopper(user)
    if len(hoppers)>0:
        cases_tabs.append(dbc.Tab(label='Hopper', tab_id='Hopper'))

    supervisees = CaseCalls().query_team(user)['SHORT_USER_NAME'].unique()
    if len(supervisees)>0:
        cases_tabs.append(dbc.Tab(label='Team', tab_id='Team'))

    return cases_tabs



''' add Hopper tab when user has hoppers,
add Team tab when user has supervisees '''
@app.callback(
    [Output('user-cases', 'data'), Output('hopper-cases', 'data'), Output('team-cases', 'data')],
    [Input('clock-cases', 'n_intervals')],
)
def store(n_intervals):
    #print(n_intervals)
    if n_intervals != 1:
        return dash.exceptions.PreventUpdate
    
    user = request.cookies['user']
    cases = Cases(user)

    user_cases = cases.get_case_list()
    hopper_cases = cases.get_case_list('Hopper')
    team_cases = cases.get_case_list('Team')

    """print (user, 'user_cases', user_cases.shape)
    if hopper_cases is not None and hopper_cases.shape[0]>0: 
        print (user, 'hopper_cases', hopper_cases.shape)
    if team_cases is not None: 
        print (user, 'team_cases', team_cases.shape)"""

    return CaseHandler().to_json(user_cases), CaseHandler().to_json(hopper_cases), CaseHandler().to_json(team_cases)


''' pick data according to selected tab,
show table header first '''
@app.callback(
    [Output('content-2-cases', 'children'), Output('table-data', 'children')],
    [Input('cases-tabs', 'active_tab'), Input('user-cases', 'data'), Input('hopper-cases', 'data'), Input('team-cases', 'data')]
)
def index(selection, user_cases, hopper_cases, team_cases):
    user = request.cookies['user']
    cases = Cases(user)

    user_cases = pd.read_json(user_cases, orient='split')
    #team_cases = pd.read_json(team_cases, orient='split')

    if selection == 'Current':
        ''' assume null system code is not closed case '''
        case_list = user_cases[user_cases['STATUS_SYSTEM_CODE'].fillna('')!='CLOSE'].reset_index(drop=True)
        return cases.table(columns), CaseHandler().to_json(case_list)
        
    elif selection == 'Lifetime':
        ''' not showing Last Modified cases in Lifetime '''
        case_list = user_cases[(user_cases['CREATED_BY_SAM'].str.lower()==user.lower()) | 
                                (user_cases['ASSIGNED_TO_SAM'].str.lower()==user.lower()) |
                                (user_cases['OWNER_SAM'].str.lower()==user.lower())].reset_index(drop=True)
        return cases.table(columns), CaseHandler().to_json(case_list)

    elif selection == 'Hopper':
        return cases.table(columns), hopper_cases

    elif selection == 'Team':
        ''' not showing Last Modified cases in Lifetime '''
        '''case_list = team_cases[(team_cases['CREATED_BY_SAM'].str.lower()==user.lower()) | 
                                (team_cases['ASSIGNED_TO_SAM'].str.lower()==user.lower()) |
                                (team_cases['OWNER_SAM'].str.lower()==user.lower())].reset_index(drop=True)'''
        #return cases.table(columns), CaseHandler().to_json(case_list)
        return cases.table(columns), team_cases

    elif selection == 'Relationships':
        return 'Relationships', None


''' 
filter table,
and according to filtered table data adjusting graphs '''
@app.callback(
    [Output('content-1-cases', 'children'), Output('filtered-data', 'children')],
    [Input('cases-tabs', 'active_tab'), Input('table-data', 'children'), Input({'type': 'filter', 'colname': ALL}, 'value'), Input({'type': 'filter', 'colname': ALL}, 'id')]
)
def filter(selection, data, filter_values, filter_ids):
    if data is None: 
        #raise dash.exceptions.PreventUpdate
        return dbc.Col('No Data Available!'), None
    data = pd.read_json(data, orient='split')
    data = sdt.filter_table(data, filter_values, filter_ids, url_col=['Case Title'])  
    

    user = request.cookies['user']
    cases = Cases(user)
    #return cases.cases_graphs(data, selection), data.to_json(orient='split')
    if selection == 'Current':
        #should look like cases.current(*args,**kwargs)
        return cases.current(data), data.to_json(orient='split')
        
    elif selection == 'Lifetime':
        #should look like cases.lifetime(*args,**kwargs)
        return cases.lifetime(data), data.to_json(orient='split')

    elif selection == 'Hopper':
        #should look like cases.hopper(*args,**kwargs)
        return cases.hopper(data), data.to_json(orient='split')

    elif selection == 'Team':
        #should look like cases.hopper(*args,**kwargs)
        return cases.team(data), data.to_json(orient='split')

    elif selection == 'Relationships':
        #should look like cases.relationships(*args,**kwargs)
        return 'Relationships'


''' 
click on column names to sort table
odd number of times: ascending, even number of times: descending 

when table data is too big, only show the first 1000 rows
'''
@app.callback(
    [Output('table-body', 'children'), Output('download-link-table', 'href'), Output('previous-header-clicks', 'children')],
    [Input('filtered-data', 'children'), Input({'type': 'header', 'colname': ALL}, 'n_clicks'), Input({'type': 'header', 'colname': ALL}, 'id')],
    [State('previous-header-clicks', 'children')]
)
def sort(data, header_clicks, header_ids, previous_header_clicks):
    if data is None: 
        #return None, None
        raise dash.exceptions.PreventUpdate 
    data = pd.read_json(data, orient='split')
    data['Case Title'] = data.apply(lambda row: [row['Case Title'], row['Case URL']], axis=1)
    data = data[columns]
    data = data.sort_values(['Case Type', 'Case ID'], ascending=[True, False]).reset_index(drop=True)
    data = sdt.sort_table(data, header_clicks, header_ids, previous_header_clicks, url_col=['Case Title'])

    download_csv = 'data:text/csv;charset=utf-8,' + urllib.parse.quote(data.to_csv(index=False, encoding='utf-8'))
    return sdt.generate_table_body(data.head(1000), url_col=['Case Title']), download_csv, header_clicks