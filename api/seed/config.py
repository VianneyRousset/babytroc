import app


def get_config():
    return app.config.Config.from_env()
