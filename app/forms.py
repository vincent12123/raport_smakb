from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, validators, SubmitField, PasswordField, IntegerField, DateField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo, ValidationError
from app.models import  User, Siswa

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('guru', 'Guru'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

class GuruForm(FlaskForm):
    nama_guru = StringField('Nama Guru', validators=[DataRequired(), Length(min=2, max=50)])
    user_id = IntegerField('User ID', validators=[DataRequired()])
    submit = SubmitField('Tambah Guru')

class AddSekolahForm(FlaskForm):
    nama_sekolah = StringField('Nama Sekolah', validators=[DataRequired()])
    alamat_sekolah = StringField('Alamat Sekolah', validators=[DataRequired()])
    submit = SubmitField('Tambah Sekolah')

class EditGuruForm(FlaskForm):
    nama_guru = StringField('Nama Guru', validators=[DataRequired()])
    submit = SubmitField('Update Guru')

class EditSekolahForm(FlaskForm):
    nama_sekolah = StringField('Nama Sekolah', validators=[DataRequired()])
    alamat_sekolah = StringField('Alamat Sekolah', validators=[DataRequired()])
    submit = SubmitField('Update Sekolah')

class SiswaForm(FlaskForm):
    nisn = StringField('NISN', validators=[DataRequired()])
    nama = StringField('Nama', validators=[DataRequired()])
    alamat = StringField('Alamat')
    id_kelas = IntegerField('ID Kelas', validators=[DataRequired()])
    submit = SubmitField('Submit')

class KelasForm(FlaskForm):
    nama_kelas = StringField('Nama Kelas', validators=[DataRequired()])
    tingkat = IntegerField('Tingkat', validators=[DataRequired()])
    id_guru = SelectField('Guru Wali Kelas', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

class MapelForm(FlaskForm):
    nama_mapel = StringField('Nama Mata Pelajaran', validators=[DataRequired()])
    deskripsi = StringField('Deskripsi')
    jumlah_jam = IntegerField('Jumlah Jam', validators=[DataRequired()])
    kategori = StringField('Kategori', validators=[DataRequired()])
    id_kelas = SelectField('Kelas', coerce=int, validators=[DataRequired()])
    id_guru = SelectField('Guru', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class NilaiAkhirForm(FlaskForm):
    id_siswa = SelectField('Siswa', validators=[DataRequired()])
    id_mapel = SelectField('Mapel', validators=[DataRequired()])
    id_guru = SelectField('Guru', validators=[DataRequired()])
    nilai = IntegerField('Nilai', validators=[DataRequired(), NumberRange(min=0, max=100)])
    capaian_kompetensi = StringField('Capaian Kompetensi', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LaporanKelasForm(FlaskForm):
    kelas = SelectField('Kelas', coerce=int)
    submit = SubmitField('Submit')



class AbsensiHarianForm(FlaskForm):
    id_kelas = SelectField('Kelas', coerce=int, validators=[DataRequired()])
    id_siswa = SelectField('Siswa', coerce=int, validators=[DataRequired()])
    #id_orang_tua = SelectField('Orang Tua', coerce=int, validators=[DataRequired()])
    tanggal = DateField('Tanggal', format='%Y-%m-%d', validators=[DataRequired()])
    status_kehadiran = SelectField('Status Kehadiran', choices=[('hadir', 'Hadir'), ('sakit', 'Sakit'), ('izin', 'Izin'), ('alpha', 'Alpha')], validators=[DataRequired()])
    keterangan = StringField('Keterangan')
    submit = SubmitField('Submit')        