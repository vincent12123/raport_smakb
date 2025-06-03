import os
from flask import Blueprint, render_template, send_file, request, flash, session, redirect, url_for, current_app
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from flask_login import login_required
from datetime import datetime
from sqlalchemy.orm import joinedload
from app import db
from app.models import Kelas, Pengajaran, Siswa, KegiatanIndustri, Ekstrakurikuler, Semester, RekapAbsensi, NilaiAkhir, SiswaKelas, TahunAjaran
from app.decorators import admin_required  # Import the custom decorator if needed

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

def read_config():
    """Baca tanggal dari file konfigurasi."""
    config = {}
    try:
        with open('config.txt', 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                config[key] = datetime.strptime(value, '%Y-%m-%d')
    except Exception as e:
        print(f"Error reading config file: {e}")
    return config

def clear_session_data():
    session.pop('df_nilai_akhir', None)
    session.pop('df', None)
    session.pop('df_rekap_absensi', None)
    session.pop('df_ekstrakurikuler', None)
    session.pop('df_kegiatan_industri', None)


@upload_bp.route('/nilai-akhir', methods=['GET', 'POST'])
@login_required
def upload_nilai_akhir():
    clear_session_data()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        if file:
            df = pd.read_excel(file, engine='openpyxl')
            df.rename(columns={
                'Nama Siswa': 'nama_siswa',
                'ID Siswa Kelas': 'id_siswa_kelas',
                'ID Pengajaran': 'id_pengajaran',
                'Nilai': 'nilai',
                'Capaian Kompetensi': 'capaian_kompetensi'
            }, inplace=True)
            required_columns = ['nama_siswa', 'id_siswa_kelas', 'id_pengajaran', 'nilai', 'capaian_kompetensi']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                flash(f"Missing columns in the uploaded file: {', '.join(missing_columns)}", 'error')
                return redirect(request.url)
            
            session['df_nilai_akhir'] = df.to_html(classes='table table-striped', index=False, border=0)
            flash('Data berhasil di-upload', 'success')
    return render_template('upload_nilai_akhir.html', data=session.get('df_nilai_akhir'))


BATCH_SIZE = 100  # Jumlah data per batch

@upload_bp.route('/submit', methods=['POST'])
@login_required
def submit_nilai_akhir():
    if 'df_nilai_akhir' not in session:
        flash("Tidak ada data untuk disubmit. Harap upload file terlebih dahulu.", "error")
        return redirect(url_for('upload.upload_nilai_akhir'))

    try:
        # Membaca data dari session
        df = pd.read_html(session['df_nilai_akhir'])[0]
        error_messages = []

        # Memproses data dalam batch
        for i in range(0, len(df), BATCH_SIZE):
            batch = df.iloc[i:i + BATCH_SIZE]
            data_to_insert = []

            for _, row in batch.iterrows():
                siswa = Siswa.query.filter_by(nama=row['nama_siswa']).first()
                siswa_kelas = SiswaKelas.query.filter_by(id=row['id_siswa_kelas']).first()
                pengajaran = Pengajaran.query.filter_by(id_pengajaran=row['id_pengajaran']).first()

                if not siswa:
                    error_messages.append(f"Siswa '{row['nama_siswa']}' tidak ditemukan.")
                    continue
                if not siswa_kelas:
                    error_messages.append(f"Siswa Kelas dengan ID '{row['id_siswa_kelas']}' tidak ditemukan.")
                    continue
                if not pengajaran:
                    error_messages.append(f"Pengajaran dengan ID '{row['id_pengajaran']}' tidak ditemukan.")
                    continue

                existing_entry = NilaiAkhir.query.filter_by(
                    id_siswa=siswa.id_siswa,
                    id_siswa_kelas=siswa_kelas.id,
                    id_pengajaran=pengajaran.id_pengajaran
                ).first()

                if existing_entry:
                    error_messages.append(f"Data untuk siswa '{siswa.nama}', siswa kelas ID '{siswa_kelas.id}', dan pengajaran ID '{pengajaran.id_pengajaran}' sudah ada.")
                    continue

                # Siapkan data untuk bulk insert
                data_to_insert.append({
                    "id_siswa": siswa.id_siswa,
                    "id_siswa_kelas": siswa_kelas.id,
                    "id_pengajaran": pengajaran.id_pengajaran,
                    "nilai": row['nilai'],
                    "capaian_kompetensi": row['capaian_kompetensi']
                })

            # Lakukan bulk insert untuk batch ini
            if data_to_insert:
                db.session.bulk_insert_mappings(NilaiAkhir, data_to_insert)
                db.session.commit()

        if error_messages:
            for msg in error_messages:
                flash(msg, 'error')
        else:
            flash('Data berhasil disubmit', 'success')
            session.pop('df_nilai_akhir', None)  # Hapus data dari session setelah submit berhasil

    except Exception as e:
        current_app.logger.error("Error during submission: %s", e)
        flash("Terjadi kesalahan saat memproses data. Silakan coba lagi.", "error")

    return redirect(url_for('upload.upload_nilai_akhir'))



@upload_bp.route('/rekap-absensi', methods=['GET', 'POST'])
@login_required
def upload_rekap_absensi():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Tidak ada file yang diunggah.', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('File tidak dipilih.', 'error')
            return redirect(request.url)

        # Validasi file upload
        if not file.filename.endswith(('.xls', '.xlsx')):
            flash('File harus berupa Excel (.xls atau .xlsx).', 'error')
            return redirect(request.url)

        try:
            df = pd.read_excel(file, engine='openpyxl')
        except Exception as e:
            flash(f'Error saat membaca file: {str(e)}', 'error')
            return redirect(request.url)

        # Validasi kolom yang diperlukan
        required_columns = ['nama_siswa', 'tahun_ajaran', 'semester', 'total_sakit', 'total_izin', 'total_tanpa_keterangan']
        if not all(col in df.columns for col in required_columns):
            flash(f'File Excel harus memiliki kolom: {", ".join(required_columns)}.', 'error')
            return redirect(request.url)

        error_messages = []  # Untuk menyimpan pesan kesalahan

        for _, row in df.iterrows():
            siswa = Siswa.query.filter_by(nama=row['nama_siswa']).first()
            if not siswa:
                error_messages.append(f"Siswa dengan nama '{row['nama_siswa']}' tidak ditemukan.")
                continue

            semester = Semester.query.options(joinedload(Semester.tahun_ajaran)).filter(
                Semester.tahun_ajaran.has(tahun=row['tahun_ajaran']),
                Semester.semester == row['semester']
            ).first()

            if not semester:
                error_messages.append(f"Semester '{row['semester']}' untuk tahun ajaran '{row['tahun_ajaran']}' tidak ditemukan.")
                continue

            # Buat atau perbarui data RekapAbsensi
            rekap_absensi = RekapAbsensi.query.filter_by(id_siswa=siswa.id_siswa, id_semester=semester.id).first()
            if rekap_absensi:
                rekap_absensi.total_sakit = row['total_sakit']
                rekap_absensi.total_izin = row['total_izin']
                rekap_absensi.total_tanpa_keterangan = row['total_tanpa_keterangan']
            else:
                rekap_absensi = RekapAbsensi(
                    id_siswa=siswa.id_siswa,
                    id_semester=semester.id,
                    total_sakit=row['total_sakit'],
                    total_izin=row['total_izin'],
                    total_tanpa_keterangan=row['total_tanpa_keterangan']
                )
                db.session.add(rekap_absensi)

        db.session.commit()

        if error_messages:
            flash('Beberapa entri tidak bisa diproses:\n' + '\n'.join(error_messages), 'error')
        else:
            flash('Data berhasil di-submit.', 'success')

        # Simpan data untuk ditampilkan di halaman
        session['df'] = df.to_html(classes='table table-striped', index=False, border=0)

    return render_template('upload_rekap_absensi.html', data=session.get('df'))

@upload_bp.route('/ekstrakurikuler', methods=['GET', 'POST'])
@login_required
def upload_ekstrakurikuler():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        if file:
            try:
                df = pd.read_excel(file, engine='openpyxl')
                
                # Validate required columns
                required_columns = ['nama_siswa', 'tahun_ajaran', 'semester', 'kegiatan', 'predikat', 'keterangan']
                if not all(col in df.columns for col in required_columns):
                    flash(f'File Excel harus memiliki kolom: {", ".join(required_columns)}.', 'error')
                    return redirect(request.url)

                error_messages = []

                for _, row in df.iterrows():
                    # Find student
                    siswa = Siswa.query.filter_by(nama=row['nama_siswa']).first()
                    if not siswa:
                        error_messages.append(f"Siswa dengan nama '{row['nama_siswa']}' tidak ditemukan.")
                        continue

                    # Find semester
                    semester = Semester.query.join(TahunAjaran).filter(
                        TahunAjaran.tahun == row['tahun_ajaran'],
                        Semester.semester == row['semester']
                    ).first()
                    if not semester:
                        error_messages.append(f"Semester '{row['semester']}' untuk tahun ajaran '{row['tahun_ajaran']}' tidak ditemukan.")
                        continue

                    # Create ekstrakurikuler record
                    ekstrakurikuler = Ekstrakurikuler(
                        id_siswa=siswa.id_siswa,
                        kegiatan=row['kegiatan'],
                        predikat=row['predikat'],
                        keterangan=row['keterangan'],
                        id_semester=semester.id
                    )
                    db.session.add(ekstrakurikuler)

                try:
                    db.session.commit()
                    if error_messages:
                        flash('Beberapa entri tidak bisa diproses:\n' + '\n'.join(error_messages), 'warning')
                    flash('Data ekstrakurikuler berhasil di-upload', 'success')
                    session['df_ekstrakurikuler'] = df.to_html(classes='table table-striped', index=False, border=0)
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error saat menyimpan data: {str(e)}', 'error')
            except Exception as e:
                flash(f'Error saat memproses file: {str(e)}', 'error')

    return render_template('upload_ekstrakurikuler.html', data=session.get('df_ekstrakurikuler'))

@upload_bp.route('/kegiatan-industri', methods=['GET', 'POST'])
@login_required
def upload_kegiatan_industri():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        if file:
            df = pd.read_excel(file, engine='openpyxl')

            # Check if required columns exist
            required_columns = ['nama_siswa', 'tahun_ajaran', 'semester', 'mitra_induka', 'lokasi', 'keterangan']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                flash(f"Missing columns in the uploaded file: {', '.join(missing_columns)}", 'error')
                return redirect(request.url)
            
            error_messages = []  # Untuk menyimpan pesan kesalahan
            for _, row in df.iterrows():
                siswa = Siswa.query.filter_by(nama=row['nama_siswa']).first()
                if not siswa:
                    error_messages.append(f"Siswa dengan nama '{row['nama_siswa']}' tidak ditemukan.")
                    continue  # Lanjutkan ke baris berikutnya

                semester = Semester.query.filter_by(tahun_ajaran=row['tahun_ajaran'], semester=row['semester']).first()
                if not semester:
                    error_messages.append(f"Semester '{row['semester']}' untuk tahun ajaran '{row['tahun_ajaran']}' tidak ditemukan.")
                    continue  # Lanjutkan ke baris berikutnya

                kegiatan_industri = KegiatanIndustri(
                    id_siswa=siswa.id_siswa,
                    mitra_induka=row['mitra_induka'],
                    lokasi=row['lokasi'],
                    keterangan=row['keterangan'],
                    id_semester=semester.id
                )
                db.session.add(kegiatan_industri)
            db.session.commit()
            flash('Data berhasil di-submit', 'success')
            # Tampilkan pesan kesalahan (jika ada)
            if error_messages:
                flash('Beberapa entri tidak bisa diproses:\n' + '\n'.join(error_messages), 'error')

            session['df_kegiatan_industri'] = df.to_html(classes='table table-striped', index=False, border=0)

    return render_template('upload_kegiatan_industri.html', data=session.get('df_kegiatan_industri'))

