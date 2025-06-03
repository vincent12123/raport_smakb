from flask import Blueprint, jsonify, request
import pandas as pd
from datetime import datetime
from app import db
from app.models import Siswa, Semester, RekapAbsensi, NilaiAkhir, Ekstrakurikuler, KegiatanIndustri, Pengajaran, SiswaKelas

upload_api_bp = Blueprint('upload_api', __name__, url_prefix='/api/upload')

def validate_columns(dataframe, required_columns):
    """Validasi apakah kolom yang diperlukan ada dalam DataFrame."""
    missing_columns = [col for col in required_columns if col not in dataframe.columns]
    return missing_columns

@upload_api_bp.route('/nilai-akhir', methods=['POST'])
def upload_nilai_akhir():
    print("Raw Data:", request.get_data(as_text=True))
    print("Files:", request.files)
    print("Form:", request.form)
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # Load data from the uploaded Excel file
        df = pd.read_excel(file, engine='openpyxl')
        df.rename(columns={
            'Nama Siswa': 'nama_siswa',
            'ID Siswa Kelas': 'id_siswa_kelas',
            'ID Pengajaran': 'id_pengajaran',
            'Nilai': 'nilai',
            'Capaian Kompetensi': 'capaian_kompetensi'
        }, inplace=True)

        # Validate required columns
        required_columns = ['nama_siswa', 'id_siswa_kelas', 'id_pengajaran', 'nilai', 'capaian_kompetensi']
        missing_columns = validate_columns(df, required_columns)
        if missing_columns:
            return jsonify({"error": f"Missing columns: {', '.join(missing_columns)}"}), 400

        errors = []
        added_records = 0

        for _, row in df.iterrows():
            # Fetch related records from the database
            siswa = Siswa.query.filter_by(nama=row['nama_siswa']).first()
            siswa_kelas = SiswaKelas.query.filter_by(id=row['id_siswa_kelas']).first()
            pengajaran = Pengajaran.query.filter_by(id_pengajaran=row['id_pengajaran']).first()

            if not siswa:
                errors.append(f"Siswa '{row['nama_siswa']}' tidak ditemukan.")
                continue
            if not siswa_kelas:
                errors.append(f"Siswa Kelas ID '{row['id_siswa_kelas']}' tidak ditemukan.")
                continue
            if not pengajaran:
                errors.append(f"Pengajaran ID '{row['id_pengajaran']}' tidak ditemukan.")
                continue

            # Check if the record already exists
            existing_entry = NilaiAkhir.query.filter_by(
                id_siswa=siswa.id_siswa,
                id_siswa_kelas=siswa_kelas.id,
                id_pengajaran=pengajaran.id_pengajaran
            ).first()

            if existing_entry:
                errors.append(f"Data untuk siswa '{siswa.nama}' dengan ID siswa kelas '{siswa_kelas.id}' "
                              f"dan pengajaran ID '{pengajaran.id_pengajaran}' sudah ada.")
                continue

            # Add new record if not exists
            nilai_akhir = NilaiAkhir(
                id_siswa=siswa.id_siswa,
                id_siswa_kelas=siswa_kelas.id,
                id_pengajaran=pengajaran.id_pengajaran,
                nilai=row['nilai'],
                capaian_kompetensi=row['capaian_kompetensi']
            )
            db.session.add(nilai_akhir)
            added_records += 1

        # Commit all changes to the database
        db.session.commit()

        # Return appropriate response
        if errors:
            return jsonify({
                "message": f"Data uploaded with errors. {added_records} records added successfully.",
                "errors": errors
            }), 200
        return jsonify({"message": f"Data uploaded successfully. {added_records} records added."}), 201

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@upload_api_bp.route('/rekap-absensi', methods=['POST'])
def upload_rekap_absensi():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        df = pd.read_excel(file, engine='openpyxl')
        required_columns = ['nama_siswa', 'tahun_ajaran', 'semester', 'total_sakit', 'total_izin', 'total_tanpa_keterangan']
        missing_columns = validate_columns(df, required_columns)
        
        if missing_columns:
            return jsonify({"error": f"Missing columns: {', '.join(missing_columns)}"}), 400
        
        errors = []
        for _, row in df.iterrows():
            siswa = Siswa.query.filter_by(nama=row['nama_siswa']).first()
            semester = Semester.query.filter_by(tahun_ajaran=row['tahun_ajaran'], semester=row['semester']).first()
            
            if not siswa or not semester:
                errors.append(f"Invalid data for row: {row.to_dict()}")
                continue
            
            rekap_absensi = RekapAbsensi(
                id_siswa=siswa.id_siswa,
                tahun_ajaran=row['tahun_ajaran'],
                total_sakit=row['total_sakit'],
                total_izin=row['total_izin'],
                total_tanpa_keterangan=row['total_tanpa_keterangan'],
                id_semester=semester.id
            )
            db.session.add(rekap_absensi)
        
        db.session.commit()
        if errors:
            return jsonify({"message": "Data uploaded with errors", "errors": errors}), 200
        return jsonify({"message": "Data uploaded successfully"}), 201
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@upload_api_bp.route('/ekstrakurikuler', methods=['POST'])
def upload_ekstrakurikuler():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        df = pd.read_excel(file, engine='openpyxl')
        required_columns = ['nama_siswa', 'tahun_ajaran', 'semester', 'kegiatan', 'predikat', 'keterangan']
        missing_columns = validate_columns(df, required_columns)
        
        if missing_columns:
            return jsonify({"error": f"Missing columns: {', '.join(missing_columns)}"}), 400
        
        errors = []
        for _, row in df.iterrows():
            siswa = Siswa.query.filter_by(nama=row['nama_siswa']).first()
            semester = Semester.query.filter_by(tahun_ajaran=row['tahun_ajaran'], semester=row['semester']).first()
            
            if not siswa or not semester:
                errors.append(f"Invalid data for row: {row.to_dict()}")
                continue
            
            ekstrakurikuler = Ekstrakurikuler(
                id_siswa=siswa.id_siswa,
                kegiatan=row['kegiatan'],
                predikat=row['predikat'],
                keterangan=row['keterangan'],
                id_semester=semester.id
            )
            db.session.add(ekstrakurikuler)
        
        db.session.commit()
        if errors:
            return jsonify({"message": "Data uploaded with errors", "errors": errors}), 200
        return jsonify({"message": "Data uploaded successfully"}), 201
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
