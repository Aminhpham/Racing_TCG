import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    # PostgreSQL connection string
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://Minh:Audifan1996%40@localhost:5432/racing_tcg"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SocketIO configuration
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25
