from dash import Dash
from dash_bootstrap_components.themes import BOOTSTRAP

from src.components.layout import create_layout

DATA_PATH = "./data/GOOGL.csv"
DATA_2_PATH = "./data/SNAP.csv"

def main() -> None:
    app = Dash(external_stylesheets=[BOOTSTRAP], suppress_callback_exceptions=True)
    app.title = "Stocks Analysis"
    app.layout = create_layout(app)
    app.run(debug=True)


if __name__ == "__main__":
    main()
