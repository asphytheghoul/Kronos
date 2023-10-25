from dash import Dash, html

import pandas as pd

from . import bar_chart, month_dropdown, day_dropdown, time_dropdown


def create_layout(app: Dash) -> html.Div:
    return html.Div(
        className="app-div",
        children=[
            html.H1(app.title),
            html.Hr(),
            
            bar_chart.render(app),
        ],
        style={"textAlign": "center"},
    )
