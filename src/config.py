"""
src/config.py
--------------
Centralized, environment-driven configuration.

Nothing here is secret by default — sensible local-dev fallbacks are
provided for every value so the app still boots without a `.env` file.
For any real deployment, set these via environment variables (see
`.env.example`) rather than editing this file.
"""
import os


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class Config:
    # --- Flask -----------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    DEBUG = _env_bool("FLASK_DEBUG", False)
    HOST = os.environ.get("FLASK_HOST", "127.0.0.1")
    PORT = _env_int("FLASK_PORT", 5000)

    # --- Uploads -----------------------------------------------------
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
    ALLOWED_EXTENSIONS = {"pdf"}
    # 20 MB default cap — large enough for most contracts, small enough
    # to keep a single request from tying up a worker for too long.
    MAX_CONTENT_LENGTH = _env_int("MAX_UPLOAD_MB", 20) * 1024 * 1024
    # Delete uploaded PDFs after this many hours (cleanup runs at startup).
    UPLOAD_RETENTION_HOURS = _env_int("UPLOAD_RETENTION_HOURS", 24)

    # --- Model -------------------------------------------------------
    MODEL_DIR = os.environ.get("MODEL_DIR", "models/bert_model")
    MAX_TOKEN_LENGTH = _env_int("MAX_TOKEN_LENGTH", 256)

    # --- Evaluation artifacts -----------------------------------------
    EVALUATION_DIR = os.environ.get("EVALUATION_DIR", "evaluation")


config = Config()
