from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Semester, Siswa, Pengajaran, Mapel, Guru, NilaiAkhir, Kelas, TahunAjaran

laporan_siswa_bp = Blueprint('laporan_siswa', __name__, url_prefix='/laporan-siswa')

@laporan_siswa_bp.route('/chart1')
def chart1():
    return render_template('chart1.html')   
