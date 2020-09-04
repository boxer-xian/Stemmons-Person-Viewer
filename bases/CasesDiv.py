from bases.base import Base
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_html_components as html
import dash_bootstrap_components as dbc
from db.casecalls import CaseCalls
from handler.casehandler import CaseHander


class Cases(Base):
    '''Class for creating and organizing cases tab, try and 
    only return layouts here, oyu can add your cown functions 
    to keepy room. All data manipulation '''
    #you get access to the user with self.user

        

    def current(self):
        '''Returns current tabs and all layouts'''
        return html.Div('hello worl!', id='hello-world')

    def lifetime(self):
        
        pass

    def relationships(self):
        pass

    def create_grid(self):
        return 'my-grid'