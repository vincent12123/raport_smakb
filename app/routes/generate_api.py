from flask import jsonify, request, Blueprint, send_file
from zipfile import ZipFile
from app import db
from app.models import Kelas, Siswa, Semester, NilaiAkhir, Pengajaran, Mapel, Ekstrakurikuler, RekapAbsensi, KegiatanIndustri
from docx import Document
import io
import tempfile
import os

generate_api_bp = Blueprint('generate_api', __name__, url_prefix='/api/generate')

# Mapel ke baris dictionary
mapel_ke_baris = {
    "Pendidikan Agama Islam dan Budi Pekerti": 2,
    "Pendidikan Agama Kristen dan Budi Pekerti": 2,
    "Pendidikan Agama Katolik dan Budi Pekerti": 2,
    "Pendidikan Pancasila": 3,
    "Bahasa Indonesia": 4,
    "Matematika": 5,
    "Fisika": 6,
    "Kimia": 7,
    "Biologi": 8,
    "Sosiologi": 9,
    "Ekonomi": 10,
    "Sejarah": 11,
    "Geografi": 12,
    "Bahasa Inggris": 13,
    "Pendidikan Jasmani Olahraga dan Kesehatan": 14,
    "Informatika": 15,
    "Seni Tari": 16,
    "Bahasa Mandarin": 17,
    "Teknologi Informasi dan Komunikasi (TIK)": 18,
}

# Endpoint: GET daftar siswa berdasarkan kelas
@generate_api_bp.route('/siswa/<int:kelas_id>', methods=['GET'])
def get_siswa_by_kelas(kelas_id):
    siswa_list = Siswa.query.filter_by(id_kelas=kelas_id).order_by(Siswa.nama.asc()).all()
    if not siswa_list:
        return jsonify({"error": "Siswa tidak ditemukan"}), 404

    data = [{'id_siswa': s.id_siswa, 'nama': s.nama} for s in siswa_list]
    return jsonify(data), 200


# Endpoint: Generate rapor siswa tertentu
@generate_api_bp.route('/rapor/siswa', methods=['POST'])
def generate_raporsiswa():
    if request.method == 'POST':
        kelas_id = request.json.get('kelas')
        siswa_id = request.json.get('siswa')
        semester_id = request.json.get('semester')

        if kelas_id and siswa_id and semester_id:
            siswa = Siswa.query.filter_by(id_siswa=siswa_id).first()

            nilai_akhir = db.session.query(NilaiAkhir, Mapel).join(Pengajaran, NilaiAkhir.id_pengajaran == Pengajaran.id_pengajaran)\
                .join(Mapel, Pengajaran.id_mapel == Mapel.id_mapel)\
                .filter(NilaiAkhir.id_siswa == siswa_id, Pengajaran.id_semester == semester_id).all()

            ekstrakurikuler = Ekstrakurikuler.query.filter_by(id_siswa=siswa_id, id_semester=semester_id).all()
            rekap_absensi = RekapAbsensi.query.filter_by(id_siswa=siswa_id, id_semester=semester_id).first()
            kegiatan_industri = KegiatanIndustri.query.filter_by(id_siswa=siswa_id, id_semester=semester_id).all()
            semester = Semester.query.filter_by(id=semester_id).first()

            nilai_akhir_list = [
                {
                    "mapel": nilai.Mapel.nama_mapel,
                    "nilai": nilai.NilaiAkhir.nilai,
                    "capaian_kompetensi": nilai.NilaiAkhir.capaian_kompetensi,
                    "baris": mapel_ke_baris.get(nilai.Mapel.nama_mapel, None)
                }
                for nilai in nilai_akhir
            ]

            ekstrakurikuler_list = [
                {"kegiatan": ekstra.kegiatan, "keterangan": ekstra.keterangan} for ekstra in ekstrakurikuler
            ]

            kegiatan_industri_list = [
                {"mitra_induka": kegiatan.mitra_induka, "lokasi": kegiatan.lokasi, "keterangan": kegiatan.keterangan} for kegiatan in kegiatan_industri
            ]

            return {
                "siswa": {
                    "nama": siswa.nama,
                    "nisn": siswa.nisn,
                    "kelas": siswa.kelas.nama_kelas,
                },
                "nilai_akhir": nilai_akhir_list,
                "ekstrakurikuler": ekstrakurikuler_list,
                "rekap_absensi": {
                    "sakit": rekap_absensi.total_sakit,
                    "izin": rekap_absensi.total_izin,
                    "tanpa_keterangan": rekap_absensi.total_tanpa_keterangan,
                } if rekap_absensi else {},
                "kegiatan_industri": kegiatan_industri_list,
                "semester": {
                    "tahun_ajaran": semester.tahun_ajaran.tahun,
                    "semester": semester.semester
                }
            }, 200

        return {"error": "Parameter tidak lengkap."}, 400
    
    
# Endpoint: Generate rapor untuk semua siswa dalam kelas tertentu
@generate_api_bp.route('/rapor/kelas', methods=['POST'])
def generate_rapor_kelas():
    data = request.get_json()
    kelas_id = data.get('kelas_id')
    semester_id = data.get('semester_id')

    if not (kelas_id and semester_id):
        return jsonify({"error": "kelas_id dan semester_id wajib disediakan"}), 400

    kelas = Kelas.query.get(kelas_id)
    if not kelas:
        return jsonify({"error": "Kelas tidak ditemukan"}), 404

    siswa_list = Siswa.query.filter_by(id_kelas=kelas_id).all()
    if not siswa_list:
        return jsonify({"error": "Tidak ada siswa di kelas ini"}), 404

    # Buat file ZIP untuk menyimpan semua rapor
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, 'a') as zip_file:
        for siswa in siswa_list:
            doc = Document('template_rapor_x.docx')
            doc.paragraphs[0].text = f"Rapor Siswa: {siswa.nama}"  # Contoh pengisian data

            # Simpan file rapor siswa ke sementara
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
            doc.save(temp_file.name)
            temp_file.close()

            # Tambahkan file ke ZIP
            zip_file.write(temp_file.name, f"rapor_{siswa.nama}.docx")
            os.unlink(temp_file.name)

    # Kirim file ZIP sebagai respons
    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name=f"rapor_kelas_{kelas.nama_kelas}.zip")


# Error handling untuk 404
@generate_api_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Endpoint tidak ditemukan"}), 404
