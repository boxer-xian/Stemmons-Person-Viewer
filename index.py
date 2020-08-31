from stemmons.Stemmons_Dash import Stemmons_Dash_App
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from tabs.Cases import app as cases
from tabs import Cases
from app import app


app.layout = html.Div(
    [html.Div([
        html.Div([html.Img(src='http://services.boxerproperty.com/userphotos/DownloadPhoto.aspx?username=MichaelAF',className='user-image')],
                    className='user'),
            ############
            dbc.Tabs(
                [
                    dbc.Tab(label='Cases', tab_id='Cases'),
                    dbc.Tab(label='Entities', tab_id='Entites'),
                    #Every future page goes, here and must be added to the callback
                    #dbc.Tab(label='Quest', tab_id='Quest'),
                    
                ],
                id='tabs',
                active_tab='Cases',
                className='left-tabs'
            ),
        ##########
    ],className='left'),
    html.Div(
        [html.Div(id='content')],
     className='right'     
    )
    ],
    className='main'
)

@app.callback(Output('content', 'children'), 
             [Input('tabs', 'active_tab')])
def tabs(selected):

    if selected == 'Cases':
        return Cases.layout

    elif selected == 'Entites':
        return 'Entities().page()'
    
    #elif selected == 'Quest':
        #return 'Quest().page()'

    return html.P('This shouldn\'t ever be displayed...')


if __name__ == '__main__':
    app.run_server(debug=True)