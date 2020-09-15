
import pandas as pd
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import plotly.graph_objects as go
from stemmons import stemmons_dash_components as sdc
from db.CaseCalls import CaseCalls

class CaseHandler:
    '''Class to handle data tranformations for all case tabs,
        prefix all methods with tab it is associated with.'''

    def cases_layout(self, user, tab):
        dfs = []
        rows = []
        for action in ['Created', 'Assigned', 'Owned', 'Modified']:
            case_list = CaseCalls().query_case_list(user, tab, action)
            #case_list = case_list.sort_values(['Case Type', 'Case ID'], ascending=[True, False]).reset_index(drop=True)
            df1 = CaseCalls().groupby_case_type(case_list)
            #df2 = CaseCalls().groupby_due_status(case_list)
            df2 = CaseCalls().groupby_system_status(case_list)
            dfs.append(case_list)
            row = dbc.Row([
                dbc.Col(self.card(df1['Count of Cases'].sum(), action), width={'size':2}, align='center'),
                dbc.Col(self.bar_graph(df1, 'Case Type', 'Count of Cases', title='Count of Cases by Case Type', sort_x=True), width={'size':5}),
                #dbc.Col(self.bar_graph(df2, 'Due Status', 'Count of Cases', title='Count of Cases by Due Status', showlegend=False), width={'size':4}),
                dbc.Col(self.bar_graph(df2, 'System Status', 'Count of Cases', title='Count of Cases by System Status', sort_x=True), width={'size':5}),
            ])
            rows.append(row)
        data = pd.concat(dfs).drop_duplicates(keep='first').sort_values(['Case Type', 'Case ID'], ascending=[True, False]).reset_index(drop=True)
        print (data.shape)
        if tab=='Current':
            return [html.Div(rows), data]
        else:
            return html.Div(rows)



    def card(self, value, tag):
        return dbc.Card(dbc.CardBody([
            html.H6(value, className='card-title'),
            html.P(tag, className='card-text')
        ]), style={'height': '100px', 'border': '1px solid gray', 'border-radius': '10px', 'font-size': '13px', 'text-align': 'center'})

    def bar_graph(self, data, x, y, title=None, showlegend=True, sort_x=False):
        if data.shape[0]==0: return None
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
        return dcc.Graph(figure={'data': trace, 'layout': layout}, config={'displayModeBar': False})

