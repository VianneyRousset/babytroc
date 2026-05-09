# babycli/__main__.py
from cyclopts import App

app = App(
    name="babycli",
    help="Babytroc API operations CLI.",
)

from .check import check_app
from .danger import danger_mode_app
from .logs import logs_app

app.command(check_app)
app.command(danger_mode_app)
app.command(logs_app)


def main():
    app()


if __name__ == "__main__":
    main()
