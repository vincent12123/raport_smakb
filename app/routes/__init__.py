from flask import Flask
from .auth import auth_bp
from .guru import guru_bp
from .admin import admin_bp
from .api import api_bp
from .progress_guru import progress_guru_bp
from .download import download_files_bp
from .upload import upload_bp
from .generate_rapor import generate_bp
from .bulk_delete import bulk_delete_bp
from .crud_sekolah import crud_sekolah_bp
from .crud_siswa import crud_siswa_bp
from .crud_kelas import crud_kelas_bp
from .crud_mapel import crud_mapel_bp
from .laporan_kelas import laporan_kelas_bp
from .laporan_guru import laporan_guru_bp
from .laporan_guru_mengajar import laporan_guru_mengajar_bp
from .laporan_siswa import laporan_siswa_bp
from .generate_api import generate_api_bp
from .upload_api import upload_api_bp
from .api_chart import api_chart_bp
from .orangtua_crud_api import orangtua_api_bp  # Import the new Blueprint
from .auth_orangtua import auth_orangtua_bp  # Import the new Blueprint
from .semester_admin import semester_admin_bp  # Add this line

def register_blueprints(app):
    app.register_blueprint(guru_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(progress_guru_bp)
    app.register_blueprint(download_files_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(generate_bp)
    app.register_blueprint(bulk_delete_bp)
    app.register_blueprint(crud_sekolah_bp)
    app.register_blueprint(crud_siswa_bp)
    app.register_blueprint(crud_kelas_bp)
    app.register_blueprint(crud_mapel_bp)
    app.register_blueprint(laporan_kelas_bp)
    app.register_blueprint(laporan_guru_bp)
    app.register_blueprint(laporan_guru_mengajar_bp)
    app.register_blueprint(laporan_siswa_bp)
    app.register_blueprint(generate_api_bp)
    app.register_blueprint(upload_api_bp)
    app.register_blueprint(api_chart_bp)
    app.register_blueprint(orangtua_api_bp)  # Register the new Blueprint
    app.register_blueprint(auth_orangtua_bp)  # Register the new Blueprint
    app.register_blueprint(semester_admin_bp)  # Add this line
