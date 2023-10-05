import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from ..data.loader import DataSchema
from . import ids


def render(app: Dash, data: pd.DataFrame) -> html.Div:
    all_days: list[str] = data[DataSchema.DAY].tolist()
    unique_days = sorted(set(all_days))

    @app.callback(
        Output(ids.DAY_DROPDOWN, "value"),
        [
            Input(ids.MONTH_DROPDOWN, "value"),
            Input(ids.SELECT_ALL_DAYS_BUTTON, "n_clicks"),
        ],
    )
    def select_all_days(months: list[str], _: int) -> list[str]:
        filtered_data = data.query("month in @months")
        return sorted(set(filtered_data[DataSchema.DAY].tolist()))

    # return html.Div(
    #     children=[
    #         html.H6("Day"),
    #         dcc.Dropdown(
    #             id=ids.DAY_DROPDOWN,
    #             options=[{"label": day, "value": day} for day in unique_days],
    #             value=unique_days,
    #             multi=True,
    #         ),
    #         html.Button(
    #             className="dropdown-button",
    #             children=["Select All"],
    #             id=ids.SELECT_ALL_DAYS_BUTTON,
    #             n_clicks=0,
    #         ),
    #     ]
    # )