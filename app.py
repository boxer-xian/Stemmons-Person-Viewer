
from stemmons.Stemmons_Dash import Stemmons_Dash_App
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

app = Stemmons_Dash_App( name=__name__, 
                        suppress_callback_exceptions=True,
                        external_stylesheets=[dbc.themes.BOOTSTRAP])


