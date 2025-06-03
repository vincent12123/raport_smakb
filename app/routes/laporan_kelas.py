from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Semester, Siswa, Pengajaran, Mapel, Guru, NilaiAkhir, Kelas, TahunAjaran


laporan_kelas_bp = Blueprint('laporan_kelas', __name__, url_prefix='/laporan-kelas')


@laporan_kelas_bp.route('/laporan_kelas', methods=['GET', 'POST'])
@login_required
def nilai_akhir():
    kelas = Kelas.query.order_by(Kelas.tingkat).all()

    # Join ke TahunAjaran untuk mengurutkan berdasarkan tahun dan semester
    semesters = db.session.query(Semester).join(TahunAjaran).order_by(TahunAjaran.tahun.asc(), Semester.semester.asc()).all()

    if request.method == 'POST':
        kelas_id = request.form.get('kelas')
        guru_id = request.form.get('guru')
        semester_id = request.form.get('semester')

        # Join dengan tabel Pengajaran karena id_guru dan id_mapel ada di Pengajaran
        hasil = db.session.query(NilaiAkhir, Siswa, Mapel, Guru)\
            .join(Siswa, NilaiAkhir.id_siswa == Siswa.id_siswa)\
            .join(Pengajaran, NilaiAkhir.id_pengajaran == Pengajaran.id_pengajaran)\
            .join(Mapel, Pengajaran.id_mapel == Mapel.id_mapel)\
            .join(Guru, Pengajaran.id_guru == Guru.id_guru)\
            .filter(Siswa.id_kelas == kelas_id, Guru.id_guru == guru_id, Pengajaran.id_semester == semester_id)\
            .all()

        # Mengambil data nilai di bawah 66
        nilai_bawah_76 = db.session.query(NilaiAkhir, Siswa, Mapel, Guru)\
            .join(Siswa, NilaiAkhir.id_siswa == Siswa.id_siswa)\
            .join(Pengajaran, NilaiAkhir.id_pengajaran == Pengajaran.id_pengajaran)\
            .join(Mapel, Pengajaran.id_mapel == Mapel.id_mapel)\
            .join(Guru, Pengajaran.id_guru == Guru.id_guru)\
            .filter(Siswa.id_kelas == kelas_id, Guru.id_guru == guru_id, Pengajaran.id_semester == semester_id, NilaiAkhir.nilai < 66)\
            .all()

        return render_template('laporan.html', hasil=hasil, kelas=kelas, semesters=semesters, nilai_bawah_76=nilai_bawah_76)

    else:
        return render_template('laporan.html', kelas=kelas, semesters=semesters)


