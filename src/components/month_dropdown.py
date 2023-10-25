import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from . import ids


def render(app: Dash, data: pd.DataFrame) -> html.Div:
    all_months: list[str] = data[DataSchema.MONTH].tolist()
    unique_months = sorted(set(all_months), key=int)

    @app.callback(
        Output(ids.MONTH_DROPDOWN, "value"),
        Input(ids.SELECT_ALL_MONTHS_BUTTON, "n_clicks"),
    )
    def select_all_months(_: int) -> list[str]:
        return unique_months

    # return html.Div(
    #     children=[
    #         html.H6("Month"),
    #         dcc.Dropdown(
    #             id=ids.MONTH_DROPDOWN,
    #             options=[{"label": month, "value": month} for month in unique_months],
    #             value=unique_months,
    #             multi=True,
    #         ),
    #         html.Button(
    #             className="dropdown-button",
    #             children=["Select All"],
    #             id=ids.SELECT_ALL_MONTHS_BUTTON,
    #             n_clicks=0,
    #         ),
    #     ]
    # )