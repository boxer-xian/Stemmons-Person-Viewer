from app import app
from bases.base import Base
from db.CaseCalls import CaseCalls
from handler.CaseHandler import CaseHandler
from stemmons import stemmons_dash_table as sdt
from stemmons import stemmons_dash_components as sdc

from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
from datetime import date


class Cases(Base):
    '''Class for creating and organizing cases tab, try and 
    only return layouts here, you can add your own functions 
    to keep room. All data manipulation '''
    #you get access to the user with self.user
    
    
    def current(self, case_list):
        '''Returns current tabs and all layouts'''
        if case_list is None or case_list.shape[0]==0:
            return dbc.Col('No Data Available!')
        else:
            users = [self.user]
            return self.cases_graphs(case_list, users)


    def lifetime(self, case_list):
        if case_list is None or case_list.shape[0]==0:
            return dbc.Col('No Data Available!')
        else:
            users = [self.user]
            return self.cases_graphs(case_list, users)


    def hopper(self, case_list):
        if case_list is None or case_list.shape[0]==0:
            return dbc.Col('No Data Available!')
        else:
            users = CaseCalls().query_hopper(self.user)
            return self.cases_graphs(case_list, users)

    def relationships(self):
        pass

    def create_grid(self):
        return 'my-grid'
            

    def get_case_list(self, identity=None):
        user = self.user
        if identity == 'Hopper':
            users = CaseCalls().query_hopper(user)
            print ('Hopper:', users)
        else:
            users = [user]
        return CaseCalls().query_case_list(users)
        

    
        





    def cases_graphs(self, case_list, users):
        case_list = case_list.sort_values(['Case Type', 'Case ID'], ascending=[True, False]).reset_index(drop=True)
        rows = []
        for tag, col in zip(['Created', 'Assigned', 'Owned', 'Last Modified'], ['CREATED_BY_SAM', 'ASSIGNED_TO_SAM', 'OWNER_SAM', 'MODIFIED_BY_SAM']):
            """if len(users)==1:
                tag = tag + '<br>' + users[0]
            else:
                tag = tag + '<br>Hopper'"""
            df = case_list[case_list[col].isin(users)].reset_index(drop=True)
            
            if df.shape[0]>0:
                df1 = CaseHandler().groupby_case_type(df)
                df2 = CaseHandler().groupby_system_status(df)
                row = dbc.Row([
                    dbc.Col(self.card(df1['Count of Cases'].sum(), tag), width={'size':2}, align='center'),
                    dbc.Col(self.bar_graph(df1, 'Case Type', 'Count of Cases', title='Count of Cases by Case Type', sort_x=True), width={'size':6}),
                    dbc.Col(self.bar_graph(df2, 'System Status', 'Count of Cases', title='Count of Cases by System Status', sort_x=True), width={'size':4}),
                ])
                rows.append(row)
        
        return html.Div(rows)

    def card(self, value, tag):
        return dbc.Card(dbc.CardBody([
            html.H6(value, className='card-title'),
            html.P(tag, className='card-text')
        ]), style={'height': '100px', 'border': '1px solid gray', 'border-radius': '10px', 'font-size': '13px', 'text-align': 'center'})


    def bar_graph(self, data, x, y, title=None, showlegend=True, sort_x=False):
        if data is None or data.shape[0]==0: return None
        if sort_x==True: 
            df_x = pd.DataFrame(data[x].unique(), columns=[x])
        trace = []
        for due_status, color in zip(['No Due Date', 'Not Due', 'Due', 'Past Due'], ['black', 'grey', 'lightgrey', 'darkorange']):
            df = data[data['Due Status']==due_status].reset_index(drop=True)
            if sort_x==True: 
                df = df_x.merge(df, on=x, how='outer')
            trace.append(go.Bar(
                x=df[x],
                y=df[y],
                marker={'color': color},
                width=0.5,
                hovertemplate='<b>'+due_status+'</b><br><br>'+x+': %{x}<br>'+y+': %{y:,}<extra></extra>',
                name=due_status
            ))       
        layout = dict(
            title={'text': title, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
            xaxis={'title': x, 'automargin': True, 'showgrid': False, 'showline': True, 'linewidth': 1, 'linecolor': 'black'},
            yaxis={'title': 'Count of Cases', 'rangemode': 'tozero'},
            barmode='stack',
            showlegend=showlegend,
            hovermode='closest',
            font={'size': 11},
            clickmode=None)
        return dcc.Graph(figure={'data': trace, 'layout': layout})    #, config={'displayModeBar': False}


    def table(self, columns):
        return dbc.Col(html.Div([
            dbc.Spinner(html.Table(sdt.generate_table_head(columns, url_col=['Case Title']), id='table-head', className='case_list')),
            dbc.Spinner([
                html.Table(id='table-body', className='case_list'),
                html.Div(  
                    html.A('Download Table Data', id='download-link-table', download='case_list.csv', target='_blank'), 
                    style={'width': '100%', 'display': 'inline-block', 'text-align': 'right', 'vertical-align': 'middle', 'font-size': '12px', 'padding': '10px'})
            ])
        ]), style={'margin-top': '50px'})


    


        