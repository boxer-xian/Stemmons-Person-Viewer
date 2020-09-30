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
            #return self.cases_graphs(case_list, users)
            rows = []
            for tag in ['Assigned To', 'Created', 'Owned', 'Last Modified']:
                rows.append(self.cases_graph(case_list, users, tag))
            return html.Div(rows)



    def lifetime(self, case_list):
        if case_list is None or case_list.shape[0]==0:
            return dbc.Col('No Data Available!')
        else:
            users = [self.user]
            #return self.cases_graphs(case_list, users)
            rows = []
            for tag in ['Assigned To', 'Created', 'Owned']:
                rows.append(self.cases_graph(case_list, users, tag))
            return html.Div(rows)


    def hopper(self, case_list):
        if case_list is None or case_list.shape[0]==0:
            return dbc.Col('No Data Available!')
        else:
            users = CaseCalls().query_hopper(self.user)
            #return self.cases_graphs(case_list, users)
            rows = []
            for tag in ['Assigned To', 'Created', 'Owned', 'Last Modified']:
                rows.append(self.cases_graph(case_list, users, tag))
            return html.Div(rows)


    def team(self, case_list):
        if case_list is None or case_list.shape[0]==0:
            return dbc.Col('No Data Available!')
        else:
            users_data = CaseCalls().query_team(self.user)
            return self.team_cards(case_list, users_data)


    def relationships(self):
        pass

    def create_grid(self):
        return 'my-grid'
            

    def get_case_list(self, identity=None):
        user = self.user
        if identity == 'Hopper':
            users = CaseCalls().query_hopper(user)
            return CaseCalls().query_case_list(users, 'Active')
            #print ('Hopper:', users)
        elif identity == 'Team':
            users = CaseCalls().query_team(user)['SHORT_USER_NAME'].unique()
            return CaseCalls().query_case_list(users, 'Active')
        else:
            users = [user]
            return CaseCalls().query_case_list(users)


    def cases_graph(self, case_list, users, tag):
        tag_dict = {'Assigned To':'ASSIGNED_TO_SAM', 'Created': 'CREATED_BY_SAM', 'Owned':'OWNER_SAM', 'Last Modified':'MODIFIED_BY_SAM'}
        col = tag_dict[tag]
        df = case_list[case_list[col].str.lower().isin([s.lower() for s in users])].reset_index(drop=True)
        
        if df.shape[0]>0:
            df1 = CaseHandler().groupby_case_type(df)
            df2 = CaseHandler().groupby_system_status(df)
            return dbc.Row([
                dbc.Col(self.card(df1['Count of Cases'].sum(), tag), width={'size':2}, align='center'),
                dbc.Col(self.bar_graph(df1, 'Case Type', 'Count of Cases', title='Count of Cases by Case Type', sort_x=True), width={'size':6}),
                dbc.Col(self.bar_graph(df2, 'System Status', 'Count of Cases', title='Count of Cases by System Status', sort_x=True), width={'size':4}),
            ])
        else:
            return None


    def team_cards(self, case_list, users_data):
        cards = []
        for i in range(users_data.shape[0]):
            user = users_data.loc[i, 'SHORT_USER_NAME']
            display_name = users_data.loc[i, 'DISPLAY_NAME']
            #print (user, display_name)
            case_count = []
            pct_past_due = []
            oldest_days = []
            #oldest_days = 0

            for col in ['ASSIGNED_TO_SAM', 'CREATED_BY_SAM', 'OWNER_SAM']:   #, 'MODIFIED_BY_SAM'
                df = case_list[case_list[col].str.lower()==user.lower()].reset_index(drop=True)
                
                active_cases = df['Case ID'].nunique()
                case_count.append(active_cases)
                pct = df[df['Due Status']=='Past Due']['Case ID'].nunique()/active_cases if active_cases>0 else 0
                pct_past_due.append(pct)

                days = df['Case Life Days'].max() if df.shape[0]>0 else 0
                oldest_days.append(days)
                #oldest_days = oldest_days if oldest_days > days else days
            cards.append(self.user_card(user, display_name, case_count, pct_past_due, oldest_days))

        return html.Div(dbc.Row(cards))



    def card(self, value, tag):
        return dbc.Card(dbc.CardBody([
            html.H6(value, className='card-title'),
            html.P(tag, className='card-text')
        ]), style={'height': '100px', 'border': '1px solid gray', 'border-radius': '10px', 'font-size': '13px', 'text-align': 'center'})


    def user_card(self, username, display_name, case_count, pct_past_due, oldest_days):
        #url = f'?User={username}'
        return dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    #html.H6(display_name, className='card-title'),
                    html.H6(html.A(display_name, href=username, target='_blank'), className='card-title'),
                    html.P('Current:', className='card-text'),
                    html.P('Assigned To: {}, Past Due: {:.1%}, Oldest: {} days'.format(case_count[0], pct_past_due[1], oldest_days[0]), className='card-text'),
                    html.P('Created: {}, Past Due: {:.1%}, Oldest: {} days'.format(case_count[1], pct_past_due[0], oldest_days[1]), className='card-text'),
                    html.P('Owned: {}, Past Due: {:.1%}, Oldest: {} days'.format(case_count[2], pct_past_due[2], oldest_days[2]), className='card-text'),
                    #html.P('Last Modified: {},  Past Due: {:.1%}'.format(case_count[3], pct_past_due[3]), className='card-text')
                    #html.P('Oldest Case Life: {}'.format(oldest_days), className='card-text'),
                ]), 
                style={'height': '220px', 'border': '1px solid gray', 'border-radius': '10px', 'font-size': '13px'} 
            ),
            width={'size': 3},
            style={'padding': '15px'}
        )


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
        return dcc.Graph(figure={'data': trace, 'layout': layout}, config={'displayModeBar': False})    #


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


    


        