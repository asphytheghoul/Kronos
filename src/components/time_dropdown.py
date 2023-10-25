import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from . import ids


def render(app: Dash, data: pd.DataFrame) -> html.Div:
    all_times: list[str] = data[DataSchema.TIME].tolist()
    unique_times: list[str] = sorted(set(all_times))

    @app.callback(
        Output(ids.TIME_DROPDOWN, "value"),
        [
            Input(ids.MONTH_DROPDOWN, "value"),
            Input(ids.DAY_DROPDOWN, "value"),
            Input(ids.SELECT_ALL_TIMES_BUTTON, "n_clicks"),
        ],
    )
    def select_all_times(months: list[str], days: list[str], _: int) -> list[str]:
        filtered_data = data.query("month in @months and day in @days")
        return sorted(set(filtered_data[DataSchema.TIME].tolist()))

    # return html.Div(
    #     children=[
    #         html.H6("Time"),
    #         dcc.Dropdown(
    #             id=ids.TIME_DROPDOWN,
    #             options=[
    #                 {"label": time, "value": time}
    #                 for time in unique_times
    #             ],
    #             value=unique_times,
    #             multi=True,
    #             placeholder="Select",
    #         ),
    #         html.Button(
    #             className="dropdown-button",
    #             children=["Select All"],
    #             id=ids.SELECT_ALL_TIMES_BUTTON,
    #             n_clicks=0,
    #         ),
    #     ],
    # )