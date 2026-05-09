# babycli/__main__.py
from cyclopts import App

app = App(
    name="babycli",
    help="Babytroc API operations CLI.",
)

from .check import check_app
from .config import config_app
from .danger import danger_mode_app
from .db import db_app
from .logs import logs_app
from .server import server_app

app.command(check_app)
app.command(config_app)
app.command(danger_mode_app)
app.command(db_app)
app.command(logs_app)
app.command(server_app)


def main():
    app()


if __name__ == "__main__":
    main()
