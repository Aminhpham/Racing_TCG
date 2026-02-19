import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")

    # Database — set DATABASE_URL env var in production (Render sets this automatically)
    _db_url = os.environ.get("DATABASE_URL", "sqlite:///dev.db")

    # Fix old postgres:// prefix (Render/Heroku may use this format)
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SocketIO configuration (async_mode auto-detected)
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25
