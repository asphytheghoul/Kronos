from dash import Dash, html

import pandas as pd

from . import bar_chart, month_dropdown, day_dropdown, time_dropdown


def create_layout(app: Dash, data:pd.DataFrame) -> html.Div:
    return html.Div(
        className="app-div",
        children=[
            html.H1(app.title),
            html.Hr(),
            html.Div(
                className="dropdown-container",
                children=[
                    month_dropdown.render(app, data),
                    day_dropdown.render(app, data),
                    time_dropdown.render(app, data),
                ],
            ),
            bar_chart.render(app, data)
        ],
    )
