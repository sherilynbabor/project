import os

class Config:
    # ---------------- SECURITY ----------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_fallback_key")

    # ---------------- DATABASE ----------------
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///agriyu.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------------- FILE UPLOADS ----------------
    UPLOAD_FOLDER = os.path.join("static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    # ---------------- SESSION ----------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # overridden in production

    # ---------------- EXTRA ----------------
    REMEMBER_COOKIE_DURATION = 86400  # 1 day


# 🔧 DEVELOPMENT CONFIG
class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"


# 🚀 PRODUCTION CONFIG
class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"

    # 🔒 IMPORTANT SECURITY SETTINGS
    SESSION_COOKIE_SECURE = True   # only over HTTPS
    REMEMBER_COOKIE_SECURE = True

    # Recommended for deployment (Render, Heroku, etc.)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Prevent fallback in production
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL is required in production")