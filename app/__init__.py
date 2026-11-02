"""Application factory SPK Rekomendasi Karier."""
import os

from dotenv import load_dotenv
from flask import Flask, redirect, request, url_for
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Silakan masuk terlebih dahulu."
login_manager.login_message_category = "warning"


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "ganti-secret-key-ini")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///spk_karier.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.auth import bp as auth_bp
    from app.admin import bp as admin_bp
    from app.spk import bp as spk_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(spk_bp)

    @app.before_request
    def _wajib_ganti_sandi():
        # Mahasiswa yang kata sandinya baru direset admin hanya boleh
        # membuka halaman ganti sandi (dan logout) sampai ia menetapkan
        # kata sandi pilihannya sendiri.
        if (
            current_user.is_authenticated
            and current_user.role == "mahasiswa"
            and current_user.wajib_ganti_sandi
            and request.endpoint
            not in (None, "auth.ganti_sandi", "auth.logout", "static")
        ):
            return redirect(url_for("auth.ganti_sandi"))

    with app.app_context():
        db.create_all()

    return app
