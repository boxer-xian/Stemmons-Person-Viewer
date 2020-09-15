from bases.base import Base
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_bootstrap_components as dbc
from db.CaseCalls import CaseCalls
from handler.CaseHandler import CaseHandler
from stemmons import stemmons_dash_table as sdt



class Cases(Base):
    '''Class for creating and organizing cases tab, try and 
    only return layouts here, you can add your own functions 
    to keep room. All data manipulation '''
    #you get access to the user with self.user

        

    def current(self):
        '''Returns current tabs and all layouts'''
        user = self.user
        return CaseHandler().cases_layout(user, 'Current')

    def lifetime(self):
        user = self.user
        return CaseHandler().cases_layout(user, 'Lifetime')

    def relationships(self):
        pass

    def create_grid(self):
        return 'my-grid'

    def case_list_table(self, columns):
        return html.Div([
            dbc.Spinner(html.Table(sdt.generate_table_head(columns, url_col=['Case Title']), id='table-head', className='case_list')),
            dbc.Spinner([
                html.Table(id='table-body', className='case_list'),
                html.Div(  
                    html.A('Download Table Data', id='download-link-table', download='case_list.csv', target='_blank'), 
                    style={'width': '100%', 'display': 'inline-block', 'text-align': 'right', 'vertical-align': 'middle', 'font-size': '12px', 'padding': '10px'})
            ])
        ], style={'margin-top': '50px'})