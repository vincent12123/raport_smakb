from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import time
from itsdangerous import TimedSerializer as Serializer
from flask import current_app

# Model User - remove OrangTua relationship
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(10))  # 'admin', 'guru', dll.

    # Relasi satu-ke-satu dengan Guru
    guru = db.relationship('Guru', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

# Model Message
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(225))

# Model Jurusan
class Jurusan(db.Model):
    __tablename__ = 'jurusan'
    id_jurusan = db.Column(db.Integer, primary_key=True)
    nama_jurusan = db.Column(db.String, nullable=False)

    # Relasi ke Kelas
    kelas_list = db.relationship('Kelas', back_populates='jurusan')

    # Relasi ke Siswa
    siswa_list = db.relationship('Siswa', back_populates='jurusan')

# Model OrangTua - remove User relationship
class OrangTua(db.Model):
    __tablename__ = 'orang_tua'
    id_orang_tua = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(db.Integer, db.ForeignKey('siswa.id_siswa'))
    nama_orang_tua = db.Column(db.String(100))
    nomor_whatsapp = db.Column(db.String(15))

    # Relasi satu-ke-satu dengan Siswa
    siswa = db.relationship('Siswa', back_populates='orang_tua', uselist=False)

# OrangTuaAuth model remains the same
class OrangTuaAuth(db.Model):
    __tablename__ = 'orangtua_auth'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    id_orang_tua = db.Column(db.Integer, db.ForeignKey('orang_tua.id_orang_tua'), unique=True, nullable=False)
    role = db.Column(db.String(10), default='orangtua')
    # Relationship to OrangTua
    orang_tua = db.relationship('OrangTua', backref=db.backref('auth', uselist=False))

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def generate_auth_token(self, expires_in=600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'id': self.id, 'exp': time.time() + expires_in})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            if data['exp'] < time.time():
                return None
        except:
            return None
        return OrangTuaAuth.query.get(data['id'])

    # Flask-Login required properties
    @property
    def is_active(self):
        """Return True if this account is active."""
        return True

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    @property
    def is_anonymous(self):
        """Return False because this is not an anonymous user."""
        return False

    def get_id(self):
        """Return the ID as a string, as required by Flask-Login."""
        return str(self.id)


# Model Siswa

class Siswa(db.Model):
    __tablename__ = 'siswa'
    id_siswa = db.Column(db.Integer, primary_key=True)
    nisn = db.Column(db.String)  # NISN/NIS
    nama = db.Column(db.String)
    alamat = db.Column(db.String)
    id_kelas = db.Column(db.Integer, db.ForeignKey('kelas.id_kelas', name='fk_siswa_id_kelas'))
    id_jurusan = db.Column(db.Integer, db.ForeignKey('jurusan.id_jurusan', name='fk_siswa_id_jurusan'))

    # Relasi ke Kelas
    kelas = db.relationship('Kelas', back_populates='siswa_list', uselist=False)
    # Relasi ke Jurusan
    jurusan = db.relationship('Jurusan', back_populates='siswa_list')
    # Relasi satu-ke-satu dengan OrangTua
    orang_tua = db.relationship('OrangTua', back_populates='siswa', uselist=False)
    # Relasi ke model lain
    nilai_akhir_list = db.relationship('NilaiAkhir', back_populates='siswa')
    ekstrakurikuler_list = db.relationship('Ekstrakurikuler', back_populates='siswa')
    rekap_absensi_list = db.relationship('RekapAbsensi', back_populates='siswa')
    kegiatan_industri_list = db.relationship('KegiatanIndustri', back_populates='siswa')
    absensi_harian_list = db.relationship('AbsensiHarian', back_populates='siswa')
    # Relasi ke SiswaKelas
    siswa_kelas_list = db.relationship('SiswaKelas', back_populates='siswa')

# Model SiswaKelas
class SiswaKelas(db.Model):
    __tablename__ = 'siswa_kelas'
    id = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(db.Integer, db.ForeignKey('siswa.id_siswa', name='fk_siswakelas_id_siswa'), nullable=False)
    id_kelas = db.Column(db.Integer, db.ForeignKey('kelas.id_kelas', name='fk_siswakelas_id_kelas'), nullable=False)
    id_semester = db.Column(db.Integer, db.ForeignKey('semester.id', name='fk_siswakelas_id_semester'), nullable=False)
    tahun_ajaran = db.Column(db.String(9))  # Misal '2023/2024'

    # Relasi ke Siswa
    siswa = db.relationship('Siswa', back_populates='siswa_kelas_list')
    # Relasi ke Kelas
    kelas = db.relationship('Kelas', back_populates='siswa_kelas_list')
    # Relasi ke Semester
    semester = db.relationship('Semester', back_populates='siswa_kelas_list')

# Model Kelas
class Kelas(db.Model):
    id_kelas = db.Column(db.Integer, primary_key=True)
    nama_kelas = db.Column(db.String)
    tingkat = db.Column(db.Integer)
    id_guru = db.Column(db.Integer, db.ForeignKey('guru.id_guru', name='fk_kelas_id_guru'))
    id_sekolah = db.Column(db.Integer, db.ForeignKey('sekolah.id_sekolah', name='fk_kelas_id_sekolah'))
    id_jurusan = db.Column(db.Integer, db.ForeignKey('jurusan.id_jurusan', name='fk_kelas_id_jurusan'))

    # Relasi ke Guru (Wali Kelas)
    guru = db.relationship('Guru', back_populates='kelas', uselist=False)
    # Relasi ke Siswa
    siswa_list = db.relationship('Siswa', back_populates='kelas')
    # Relasi ke Mapel
    #mapel_list = db.relationship('Mapel', back_populates='kelas')
    # Relasi ke Pengajaran
    pengajaran_list = db.relationship('Pengajaran', back_populates='kelas')
    # Relasi ke Sekolah
    sekolah = db.relationship('Sekolah', back_populates='kelas_list')
    # Relasi ke Jurusan
    jurusan = db.relationship('Jurusan', back_populates='kelas_list')
    # Relasi ke SiswaKelas
    siswa_kelas_list = db.relationship('SiswaKelas', back_populates='kelas')

# Model Guru
class Guru(db.Model):
    id_guru = db.Column(db.Integer, primary_key=True)
    nama_guru = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relasi satu-ke-satu dengan User
    user = db.relationship('User', back_populates='guru')
    # Relasi ke Kelas (Wali Kelas)
    kelas = db.relationship('Kelas', back_populates='guru', uselist=False)
    # Relasi ke Pengajaran
    pengajaran_list = db.relationship('Pengajaran', back_populates='guru')

# Model Sekolah
class Sekolah(db.Model):
    __tablename__ = 'sekolah'
    id_sekolah = db.Column(db.Integer, primary_key=True)
    nama_sekolah = db.Column(db.String)
    alamat_sekolah = db.Column(db.String)
    # Informasi tambahan tentang sekolah jika diperlukan

    # Relasi ke Kelas
    kelas_list = db.relationship('Kelas', back_populates='sekolah')

# Model Mapel
class Mapel(db.Model):
    __tablename__ = 'mapel'
    id_mapel = db.Column(db.Integer, primary_key=True)
    nama_mapel = db.Column(db.String, nullable=False)
    deskripsi = db.Column(db.String)
    jumlah_jam = db.Column(db.Integer, nullable=False)
    kategori = db.Column(db.String, nullable=False)
    # id_kelas dihapus jika Mapel tidak terikat pada kelas tertentu

    # Relasi ke Pengajaran
    pengajaran_list = db.relationship('Pengajaran', back_populates='mapel')

# Model TahunAjaran
class TahunAjaran(db.Model):
    __tablename__ = 'tahun_ajaran'
    id = db.Column(db.Integer, primary_key=True)
    tahun = db.Column(db.String(9))  # Misal '2023/2024'
    aktif = db.Column(db.Boolean, default=True)

    # Relasi ke Semester
    semester_list = db.relationship('Semester', back_populates='tahun_ajaran')

# Model Semester
class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_tahun_ajaran = db.Column(db.Integer, db.ForeignKey('tahun_ajaran.id', name='fk_semester_id_tahun_ajaran'))
    semester = db.Column(db.String(2))      # Misal 'I', 'II'
    fase = db.Column(db.String(1))          # Misal 'E', 'F'
    aktif = db.Column(db.Boolean, default=False)
    # Relasi ke TahunAjaran
    tahun_ajaran = db.relationship('TahunAjaran', back_populates='semester_list')
    # Relasi ke Pengajaran
    pengajaran_list = db.relationship('Pengajaran', back_populates='semester')
    # Relasi ke model lain
    ekstrakurikuler_list = db.relationship('Ekstrakurikuler', back_populates='semester')
    rekap_absensi_list = db.relationship('RekapAbsensi', back_populates='semester')
    kegiatan_industri_list = db.relationship('KegiatanIndustri', back_populates='semester')
    # Relasi ke SiswaKelas
    siswa_kelas_list = db.relationship('SiswaKelas', back_populates='semester')

# Model Pengajaran
class Pengajaran(db.Model):
    __tablename__ = 'pengajaran'
    id_pengajaran = db.Column(db.Integer, primary_key=True)
    id_guru = db.Column(db.Integer, db.ForeignKey('guru.id_guru', name='fk_pengajaran_id_guru'), nullable=False)
    id_mapel = db.Column(db.Integer, db.ForeignKey('mapel.id_mapel', name='fk_pengajaran_id_mapel'), nullable=False)
    id_kelas = db.Column(db.Integer, db.ForeignKey('kelas.id_kelas', name='fk_pengajaran_id_kelas'), nullable=False)
    id_semester = db.Column(db.Integer, db.ForeignKey('semester.id', name='fk_pengajaran_id_semester'), nullable=False)
    tahun_ajaran = db.Column(db.String(9), nullable=False)  # Menambahkan tahun ajaran

    # Relasi ke model terkait
    guru = db.relationship('Guru', back_populates='pengajaran_list')
    mapel = db.relationship('Mapel', back_populates='pengajaran_list')
    kelas = db.relationship('Kelas', back_populates='pengajaran_list')
    semester = db.relationship('Semester', back_populates='pengajaran_list')
    nilai_akhir_list = db.relationship('NilaiAkhir', back_populates='pengajaran')

# Model NilaiAkhir
class NilaiAkhir(db.Model):
    id_nilai = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(db.Integer, db.ForeignKey('siswa.id_siswa', name='fk_nilai_akhir_id_siswa'), nullable=False)
    id_siswa_kelas = db.Column(db.Integer, db.ForeignKey('siswa_kelas.id', name='fk_nilai_akhir_id_siswa_kelas'), nullable=False)
    id_pengajaran = db.Column(db.Integer, db.ForeignKey('pengajaran.id_pengajaran', name='fk_nilai_akhir_id_pengajaran'), nullable=False)
    nilai = db.Column(db.Integer)
    capaian_kompetensi = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi ke Siswa
    siswa = db.relationship('Siswa', back_populates='nilai_akhir_list')
    # Relasi ke SiswaKelas
    siswa_kelas = db.relationship('SiswaKelas')
    # Relasi ke Pengajaran
    pengajaran = db.relationship('Pengajaran', back_populates='nilai_akhir_list')

# Model Ekstrakurikuler
class Ekstrakurikuler(db.Model):
    __tablename__ = 'ekstrakurikuler'
    id_ekstra = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(db.Integer, db.ForeignKey('siswa.id_siswa'))
    kegiatan = db.Column(db.String)
    predikat = db.Column(db.String)
    keterangan = db.Column(db.String)
    id_semester = db.Column(db.Integer, db.ForeignKey('semester.id'))

    # Relasi ke Siswa dan Semester
    siswa = db.relationship('Siswa', back_populates='ekstrakurikuler_list')
    semester = db.relationship('Semester', back_populates='ekstrakurikuler_list')

# Model RekapAbsensi
class RekapAbsensi(db.Model):
    __tablename__ = 'rekap_absensi'
    id_rekap = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(db.Integer, db.ForeignKey('siswa.id_siswa'))
    total_sakit = db.Column(db.Integer)
    total_izin = db.Column(db.Integer)
    total_tanpa_keterangan = db.Column(db.Integer)
    id_semester = db.Column(db.Integer, db.ForeignKey('semester.id'))

    # Relasi ke Siswa dan Semester
    siswa = db.relationship('Siswa', back_populates='rekap_absensi_list')
    semester = db.relationship('Semester', back_populates='rekap_absensi_list')

# Model AbsensiHarian
class AbsensiHarian(db.Model):
    __tablename__ = 'absensi_harian'
    id_absensi = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(db.Integer, db.ForeignKey('siswa.id_siswa'))
    tanggal = db.Column(db.Date, nullable=False)
    status_kehadiran = db.Column(db.String)  # 'hadir', 'sakit', 'izin', 'alfa', dll.
    keterangan = db.Column(db.String)

    # Relasi ke Siswa
    siswa = db.relationship('Siswa', back_populates='absensi_harian_list')

# Model KegiatanIndustri
class KegiatanIndustri(db.Model):
    __tablename__ = 'kegiatan_industri'
    id_kegiatan = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(db.Integer, db.ForeignKey('siswa.id_siswa'))
    mitra_induka = db.Column(db.String)
    lokasi = db.Column(db.String)
    keterangan = db.Column(db.String)
    id_semester = db.Column(db.Integer, db.ForeignKey('semester.id'))

    # Relasi ke Siswa dan Semester
    siswa = db.relationship('Siswa', back_populates='kegiatan_industri_list')
    semester = db.relationship('Semester', back_populates='kegiatan_industri_list')

# Fungsi untuk menetapkan wali kelas
def assign_wali_kelas(guru_id, kelas_id):
    guru = Guru.query.get(guru_id)
    kelas = Kelas.query.get(kelas_id)
    if guru and kelas:
        kelas.id_guru = guru_id
        db.session.commit()

# Fungsi untuk memeriksa apakah seorang guru adalah wali kelas
def is_wali_kelas(guru_id, kelas_id):
    kelas = Kelas.query.get(kelas_id)
    return kelas and kelas.id_guru == guru_id



class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Opsional: Jika notifikasi terkait dengan siswa atau orang tua tertentu
    id_siswa = db.Column(db.Integer, db.ForeignKey('siswa.id_siswa'), nullable=True)
    id_orang_tua = db.Column(db.Integer, db.ForeignKey('orang_tua.id_orang_tua'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'date_created': self.date_created.isoformat(),
        }