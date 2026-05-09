# babycli/logs.py
from cyclopts import App

logs_app = App(
    name="logs",
    help="Log management (stub — not yet configured).",
)


@logs_app.default
def logs_default():
    """Show logging status."""
    print("Logging not yet configured. See docs for Grafana/Loki setup.")
