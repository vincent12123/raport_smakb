from flask import Blueprint, render_template, send_file
from flask_login import login_required
from app.models import Pengajaran, Mapel, Guru, Kelas
from app import db
from app.forms import LaporanKelasForm
import pandas as pd
import io


laporan_guru_mengajar_bp = Blueprint('laporan_guru_mengajar', __name__, url_prefix='/laporan-guru-mengajar')

@laporan_guru_mengajar_bp.route('/laporan-kelas1', methods=['GET', 'POST'])
@login_required
def laporan():
    form = LaporanKelasForm()
    form.kelas.choices = [(kelas.id_kelas, kelas.nama_kelas) for kelas in Kelas.query.all()]
    
    if form.validate_on_submit():
        kelas = Kelas.query.get(form.kelas.data)
        
        # Query Pengajaran untuk mendapatkan data mapel dan guru terkait kelas tersebut, dengan filter distinct
        pengajaran_list = db.session.query(Pengajaran)\
            .join(Mapel, Pengajaran.id_mapel == Mapel.id_mapel)\
            .join(Guru, Pengajaran.id_guru == Guru.id_guru)\
            .filter(Pengajaran.id_kelas == kelas.id_kelas)\
            .distinct(Pengajaran.id_mapel, Pengajaran.id_guru)\
            .all()

        # Membuat pasangan mapel dan guru
        mapel_guru_pairs = [(pengajaran.mapel, pengajaran.guru) for pengajaran in pengajaran_list]
        
        # Mendapatkan wali kelas
        wali_kelas = kelas.guru

        return render_template('laporan_kelas.html', kelas=kelas, mapel_guru_pairs=mapel_guru_pairs, wali_kelas=wali_kelas)
    
    return render_template('laporan_form_kelas.html', form=form)


@laporan_guru_mengajar_bp.route('/download-laporan-kelas/<int:id_kelas>')
@login_required
def download_laporan_kelas(id_kelas):
    excel_buffer = generate_excel(id_kelas)
    return send_file(
        excel_buffer,
        as_attachment=True,
        download_name=f'laporan_kelas_{id_kelas}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def generate_excel(kelas_id):
    kelas = Kelas.query.get(kelas_id)
    mapel = Mapel.query.filter_by(id_kelas=kelas.id_kelas).all()

    # Membuat DataFrame
    data = {
        "Nama Mata Pelajaran": [m.nama_mapel for m in mapel],
        "No Id Mata Pelajaran": [m.id_mapel for m in mapel],
        "Guru Pengajar": [m.guru.nama_guru for m in mapel],
        "No Id Guru": [m.id_guru for m in mapel]
    }
    df = pd.DataFrame(data)

    # Mengonversi DataFrame ke Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Laporan Kelas", index=False)

    excel_buffer.seek(0)
    return excel_buffer

