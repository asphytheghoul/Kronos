from dash import Dash
from dash_bootstrap_components.themes import BOOTSTRAP

from src.components.layout import create_layout
from src.data.loader import load_data

DATA_PATH = "./data/GOOGL.csv"
DATA_2_PATH = "./data/SNAP.csv"

def main() -> None:
    data = load_data(
        DATA_PATH
    )
    data2 = load_data(
        DATA_2_PATH
    )  # modify as required when querying db instead of reading from csv
    app = Dash(external_stylesheets=[BOOTSTRAP], suppress_callback_exceptions=True)
    app.title = "Stocks Analysis"
    app.layout = create_layout(app, [data,data2])
    app.run(debug=True)


if __name__ == "__main__":
    main()
