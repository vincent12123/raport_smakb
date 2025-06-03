from flask import request, Blueprint, current_app, flash, render_template, redirect, url_for, jsonify
from flask_login import login_required
from app import db
from app.models import Kelas, Siswa, Semester, NilaiAkhir, Pengajaran, Mapel, Guru, RekapAbsensi, TahunAjaran
from sqlalchemy.orm import joinedload

bulk_delete_bp = Blueprint('bulk_delete', __name__, url_prefix='/bulk_delete')



@bulk_delete_bp.route('/delete_rekap_absensi', methods=['GET', 'POST'])
@login_required
def delete_rekap_absensi():
    kelas_list = Kelas.query.order_by(Kelas.tingkat).all()
    # Perbaiki kueri dengan `join()` ke `TahunAjaran`
    semester_list = Semester.query.join(Semester.tahun_ajaran).order_by(TahunAjaran.tahun.asc(), Semester.semester.asc()).all()
    rekap_list = []

    if request.method == 'POST':
        kelas_id = request.form.get('kelas')
        semester_id = request.form.get('semester')

        if 'confirm_delete' in request.form:
            # Perform the delete action
            rekap_to_delete = db.session.query(RekapAbsensi).join(Siswa).filter(
                Siswa.id_kelas == kelas_id,
                RekapAbsensi.id_semester == semester_id
            ).all()

            for rekap in rekap_to_delete:
                db.session.delete(rekap)
            db.session.commit()
            
            flash('Rekap Absensi berhasil dihapus.', 'success')
            return redirect(url_for('delete_rekap_absensi'))

        if kelas_id and semester_id:
            # Fetch the rekap_absensi records for display
            rekap_list = db.session.query(RekapAbsensi, Siswa)\
                .join(Siswa, RekapAbsensi.id_siswa == Siswa.id_siswa)\
                .filter(Siswa.id_kelas == kelas_id, RekapAbsensi.id_semester == semester_id)\
                .all()
        else:
            flash('Pilih Kelas dan Semester.', 'danger')

    return render_template('delete_rekap_absensi.html', kelas_list=kelas_list, semester_list=semester_list, rekap_list=rekap_list)



@bulk_delete_bp.route('/nilai-akhir-v2', methods=['GET', 'POST'])
@login_required
def bulk_delete_nilai_akhir_v2():
    kelas = Kelas.query.all()
    semesters = Semester.query.join(TahunAjaran).order_by(TahunAjaran.tahun.asc(), Semester.semester.asc()).all()
    results = []

    if request.method == 'POST':
        kelas_id = request.form.get('kelas')
        guru_id = request.form.get('guru')
        mapel_id = request.form.get('mapel')
        semester_id = request.form.get('semester')
        token = request.form.get('token')

        if token == "123456" and all([kelas_id, guru_id, mapel_id, semester_id]):
            try:
                # Step 1: Get IDs to delete
                nilai_ids = db.session.query(NilaiAkhir.id_nilai)\
                    .join(Pengajaran)\
                    .filter(
                        Pengajaran.id_kelas == kelas_id,
                        Pengajaran.id_guru == guru_id,
                        Pengajaran.id_mapel == mapel_id,
                        Pengajaran.id_semester == semester_id
                    ).all()

                if nilai_ids:
                    # Step 2: Delete by IDs
                    ids_to_delete = [id[0] for id in nilai_ids]
                    deleted_count = NilaiAkhir.query.filter(
                        NilaiAkhir.id_nilai.in_(ids_to_delete)
                    ).delete(synchronize_session='fetch')
                    
                    db.session.commit()
                    flash(f'Berhasil menghapus {deleted_count} nilai akhir.', 'success')
                    return redirect(url_for('bulk_delete.bulk_delete_nilai_akhir_v2'))
                else:
                    flash('Tidak ada data yang ditemukan untuk dihapus.', 'warning')
            
            except Exception as e:
                db.session.rollback()
                flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        else:
            flash('Token tidak valid atau data tidak lengkap.', 'danger')

    # Handle GET request
    kelas_id = request.args.get('kelas')
    guru_id = request.args.get('guru')
    mapel_id = request.args.get('mapel')
    semester_id = request.args.get('semester')

    if all([kelas_id, guru_id, mapel_id, semester_id]):
        results = db.session.query(
            Siswa.nama.label('nama_siswa'),
            Mapel.nama_mapel,
            NilaiAkhir.nilai,
            NilaiAkhir.capaian_kompetensi
        ).select_from(NilaiAkhir)\
        .join(Pengajaran)\
        .join(Siswa)\
        .join(Mapel)\
        .filter(
            Pengajaran.id_kelas == kelas_id,
            Pengajaran.id_guru == guru_id,
            Pengajaran.id_mapel == mapel_id,  
            Pengajaran.id_semester == semester_id
        ).all()

    return render_template(
        'bulk_delete_nilai_akhir.html',
        kelas=kelas,
        semesters=semesters,
        results=results,
        selected_kelas=kelas_id,
        selected_guru=guru_id,
        selected_mapel=mapel_id,
        selected_semester=semester_id
    )


@bulk_delete_bp.route('/get-guru-by-kelas/<int:kelas_id>')
@login_required
def get_guru_by_kelas(kelas_id):
    # Mengambil guru yang mengajar di kelas tertentu melalui Pengajaran
    guru = db.session.query(Guru)\
        .join(Pengajaran, Pengajaran.id_guru == Guru.id_guru)\
        .filter(Pengajaran.id_kelas == kelas_id)\
        .distinct().all()

    # Membuat list guru dalam format JSON
    guru_list = [{'id': g.id_guru, 'name': g.nama_guru} for g in guru]
    return jsonify(guru_list)

@bulk_delete_bp.route('/get-mapel-by-guru/<int:guru_id>/<int:kelas_id>')
@login_required
def get_mapel_by_guru_and_kelas(guru_id, kelas_id):
    # Mengambil mapel yang diajar oleh guru tertentu di kelas tertentu melalui Pengajaran
    mapel_list = db.session.query(Mapel)\
        .join(Pengajaran, Pengajaran.id_mapel == Mapel.id_mapel)\
        .filter(Pengajaran.id_guru == guru_id, Pengajaran.id_kelas == kelas_id)\
        .distinct().all()

    return jsonify([{'id': mapel.id_mapel, 'name': mapel.nama_mapel} for mapel in mapel_list])

@bulk_delete_bp.route('/get-semester-by-kelas/<int:kelas_id>')
@login_required
def get_semester_by_kelas(kelas_id):
    # Updated to use Pengajaran instead of NilaiAkhir
    semester_list = db.session.query(Semester)\
        .join(Pengajaran, Pengajaran.id_semester == Semester.id)\
        .filter(Pengajaran.id_kelas == kelas_id)\
        .distinct().all()

    return jsonify([{
        'id': semester.id, 
        'name': f"{semester.tahun_ajaran.tahun} - Semester {semester.semester}"
    } for semester in semester_list])
