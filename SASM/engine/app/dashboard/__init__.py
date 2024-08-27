# -*- coding: utf-8 -*-
# 
# Script : SASM/engine/app/dashboard/__init__.py
# Author : Hoon
#
# ====================== Comments ======================
#  

import pandas         as pd
import plotly.express as px
import dash_draggable
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc

def init_dashboard( app ):
    df  = pd.read_csv( 'https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv' )
    app = Dash(
          server                   = app
        , routes_pathname_prefix   = '/dashboard/'
    )

    app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
                
                <script type="text/javascript">
                    document.oncontextmenu = function(){ return false; }
                </script>
            </body>
        </html>
        '''

    app.layout = html.Div( [
            dash_draggable.GridLayout(
                  id       = 'dashboard-draggable'
                , children = [
                      html.Div( style={ 'width': '280px', 'height': '200px' }, children=[
                          
                        dbc.Card( style={ 'paddingBlock':'10px', "backgroundColor":'Red', 'border':'none', 'borderRadius':'5px' }, children=[

                            dbc.CardBody( style={ 'color': 'white', 'textAlign': 'left' }, children=[

                                  html.H4( 'HIGH LISK', className="high-risk" , style={ 'margin': '0px', 'fontSize': '25px', 'fontWeight': 'bold' } )
                                , html.P ( [ 1234 ]   , className="card-value", style={ 'margin': '0px', 'fontSize': '22px', 'fontWeight': 'bold' } )

                            ] )

                        ] )
                        
                      ] )
                    , dcc.Graph(
                          figure = px.histogram( df, x='continent', y='lifeExp', histfunc='avg' )
                        , style  = { 'height' : '100%', 'width'  : '100%' }
                      )
                ]
            )
    ] )
        

    return app.server