import os
from flask import Config, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from datetime import timedelta  # Add this import at the top


# Inisialisasi ekstensi
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
ckeditor = CKEditor()

def create_app(config_class=Config):
    app = Flask(__name__)

    # Konfigurasi aplikasi
    app.config['UPLOAD_FOLDER'] = 'app/static'  # Sesuaikan dengan lokasi penyimpanan Anda
    app.config['SECRET_KEY'] = 'mysecret'
    
    # Add session security settings
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True 
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:*", "http://10.0.2.2:*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
   # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rapot.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rapot_serversma.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Untuk mengurangi beban memori

    # Inisialisasi ekstensi
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    ckeditor.init_app(app)

    # Konfigurasi Flask-Login
    login_manager.login_view = 'auth.login'  # Sesuaikan dengan rute login Anda

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User, OrangTuaAuth  # Import model di dalam fungsi untuk menghindari circular import
        user = OrangTuaAuth.query.get(int(user_id))
        if user:
            return user
        return User.query.get(int(user_id))  # Jika bukan orang tua, cek User
            

    




    # Daftarkan Blueprint
    from .routes import register_blueprints
    register_blueprints(app)

    return app
