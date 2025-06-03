# First install PyJWT:
# pip install PyJWT

from flask import Blueprint, request, jsonify, make_response, current_app
from flask_login import logout_user, login_required, current_user
from app import db
from app.models import Mapel, OrangTua, Siswa, OrangTuaAuth, NilaiAkhir, RekapAbsensi, Notification, Pengajaran, TahunAjaran, Semester
import jwt  # PyJWT import
from datetime import datetime, timedelta
from sqlalchemy import func
from functools import wraps

auth_orangtua_bp = Blueprint('auth_orangtua', __name__, url_prefix='/auth/orangtua')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token is missing'}), 401

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user = OrangTuaAuth.query.get(payload['id'])
            if not user:
                return jsonify({'message': 'Invalid token'}), 401
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
    return decorated

@auth_orangtua_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400

    user = OrangTuaAuth.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        payload = {
            'id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(
            payload, 
            current_app.config['SECRET_KEY'], 
            algorithm='HS256'
        )
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user_id': user.id,
            'orang_tua_id': user.id_orang_tua
        })
    
    return jsonify({'message': 'Invalid username or password'}), 401

@auth_orangtua_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['username', 'password', 'id_siswa', 'nama_orang_tua', 'nomor_whatsapp']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    if OrangTuaAuth.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400

    siswa = Siswa.query.get(data['id_siswa'])
    if not siswa:
        return jsonify({'message': 'Student not found'}), 404

    orang_tua = OrangTua(
        id_siswa=data['id_siswa'],
        nama_orang_tua=data['nama_orang_tua'],
        nomor_whatsapp=data['nomor_whatsapp']
    )
    db.session.add(orang_tua)
    db.session.flush()

    auth = OrangTuaAuth(
        username=data['username'],
        id_orang_tua=orang_tua.id_orang_tua,
        role='orangtua'
    )
    auth.set_password(data['password'])
    db.session.add(auth)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Registration successful'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_orangtua_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'})

@auth_orangtua_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(user):
    try:
        orang_tua = user.orang_tua
        if not orang_tua:
            return jsonify({'message': 'Profile not found'}), 404

        result = {
            'id_orang_tua': orang_tua.id_orang_tua,
            'nama_orang_tua': orang_tua.nama_orang_tua,
            'nomor_whatsapp': orang_tua.nomor_whatsapp,
            'siswa': {
                'id': orang_tua.siswa.id_siswa,
                'nama': orang_tua.siswa.nama,
                'nisn': orang_tua.siswa.nisn,
                'kelas': orang_tua.siswa.kelas.nama_kelas if orang_tua.siswa.kelas else None
            }
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_orangtua_bp.route('/profile', methods=['PUT'])
@login_required 
def update_profile():
    data = request.get_json()
    orang_tua = current_user.orang_tua
    if not orang_tua:
        return jsonify({'message': 'Profile not found'}), 404

    if 'nama_orang_tua' in data:
        orang_tua.nama_orang_tua = data['nama_orang_tua']
    if 'nomor_whatsapp' in data:
        orang_tua.nomor_whatsapp = data['nomor_whatsapp']
        
    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Update failed: {str(e)}'}), 500

@auth_orangtua_bp.route('/nilai-akhir', methods=['GET'])
@token_required
def get_nilai_akhir(user):
    try:
        orang_tua = user.orang_tua
        if not orang_tua:
            return jsonify({'message': 'Profile not found'}), 404

        siswa = orang_tua.siswa
        if not siswa:
            return jsonify({'message': 'Student not found'}), 404

        # Define the custom order for subjects
        custom_order = [
            "Pendidikan Agama Islam dan Budi Pekerti",
            "Pendidikan Agama Kristen dan Budi Pekerti",
            "Pendidikan Agama Katolik dan Budi Pekerti",
            "Pendidikan Pancasila",
            "Bahasa Indonesia",
            "Matematika",
            "Fisika",
            "Kimia",
            "Biologi",
            "Sosiologi",
            "Ekonomi",
            "Sejarah",
            "Geografi",
            "Bahasa Inggris",
            "Pendidikan Jasmani Olahraga dan Kesehatan",
            "Informatika",
            "Seni Tari",
            "Bahasa Mandarin",
            "Teknologi Informasi dan Komunikasi (TIK)"
        ]

        # Fetch the subjects and sort them according to the custom order
        nilai_list = db.session.query(NilaiAkhir).filter_by(id_siswa=siswa.id_siswa).all()
        nilai_data = [{
            'mapel': n.pengajaran.mapel.nama_mapel,
            'nilai': n.nilai,
            'capaian_kompetensi': n.capaian_kompetensi
        } for n in nilai_list]

        # Sort the subjects according to the custom order
        nilai_data.sort(key=lambda x: custom_order.index(x['mapel']) if x['mapel'] in custom_order else len(custom_order))

        result = {
            'siswa': {
                'id': siswa.id_siswa,
                'nama': siswa.nama,
                'nisn': siswa.nisn,
                'kelas': siswa.kelas.nama_kelas if siswa.kelas else None
            },
            'nilai': nilai_data
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@auth_orangtua_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard(user):
    try:
        orang_tua = user.orang_tua
        if not orang_tua:
            return jsonify({'message': 'Profile not found'}), 404

        siswa = orang_tua.siswa
        if not siswa:
            return jsonify({'message': 'Student not found'}), 404

        # Ambil data absensi terbaru
        absensi_list = db.session.query(RekapAbsensi).filter_by(id_siswa=siswa.id_siswa).order_by(RekapAbsensi.id_rekap.desc()).limit(3).all()
        absensi_data = [{
            'semester': a.semester.semester,
            'total_sakit': a.total_sakit,
            'total_izin': a.total_izin,
            'total_tanpa_keterangan': a.total_tanpa_keterangan
        } for a in absensi_list]

        # Ambil notifikasi dari database
        notifications = Notification.query.order_by(Notification.date_created.desc()).limit(5).all()
        notifications_data = [n.to_dict() for n in notifications]

        result = {
            'siswa': {
                'id': siswa.id_siswa,
                'nama': siswa.nama,
                'nisn': siswa.nisn,
                'kelas': siswa.kelas.nama_kelas if siswa.kelas else None
            },
            'orang_tua': {
                'nama_orang_tua': orang_tua.nama_orang_tua,
                'nomor_whatsapp': orang_tua.nomor_whatsapp
            },
            'absensi': absensi_data,
            'notifications': notifications_data
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_orangtua_bp.route('/ranking_per_class/<int:class_id>/<int:semester_id>', methods=['GET'])
@token_required
def get_ranking_per_class(user, class_id, semester_id):
    # Get the child of the authenticated parent
    orang_tua = user.orang_tua
    if not orang_tua:
        return jsonify({'message': 'Profile not found'}), 404

    siswa = orang_tua.siswa
    if not siswa:
        return jsonify({'message': 'Student not found'}), 404

    # Query to get ranking based on average score per student
    results = db.session.query(
        Siswa.nama,
        func.avg(NilaiAkhir.nilai).label('avg_nilai')
    ).join(NilaiAkhir, NilaiAkhir.id_siswa == Siswa.id_siswa) \
     .join(Pengajaran, Pengajaran.id_pengajaran == NilaiAkhir.id_pengajaran) \
     .filter(Pengajaran.id_kelas == class_id, Pengajaran.id_semester == semester_id) \
     .group_by(Siswa.id_siswa) \
     .order_by(func.avg(NilaiAkhir.nilai).desc()).all()

    if not results:
        return jsonify({"message": "No data found for the given class and semester"}), 404

    # Filter results to include only the child of the authenticated parent
    data = [{'nama': row.nama, 'avg_nilai': round(row.avg_nilai, 2)} for row in results if row.nama == siswa.nama]
    if not data:
        return jsonify({"message": "No ranking data found for your child"}), 404

    return jsonify(data)

@auth_orangtua_bp.route('/send-notification', methods=['GET', 'POST'])
@login_required
def send_notification():
    if request.method == 'POST':
        title = request.form.get('title')
        message = request.form.get('message')
        id_siswa = request.form.get('id_siswa')
        id_orang_tua = request.form.get('id_orang_tua')

        if not title or not message:
            return jsonify({'message': 'Title and message are required'}), 400

        notification = Notification(
            title=title,
            message=message,
            id_siswa=id_siswa,
            id_orang_tua=id_orang_tua
        )
        db.session.add(notification)
        db.session.commit()

        return jsonify({'message': 'Notification sent successfully'}), 201

    # Render the HTML form
    return '''
    <html>
        <body>
            <h1>Send Notification</h1>
            <form method="post">
                <label for="title">Title:</label><br>
                <input type="text" id="title" name="title"><br><br>
                <label for="message">Message:</label><br>
                <textarea id="message" name="message"></textarea><br><br>
                <label for="id_siswa">Student ID (optional):</label><br>
                <input type="text" id="id_siswa" name="id_siswa"><br><br>
                <label for="id_orang_tua">Parent ID (optional):</label><br>
                <input type="text" id="id_orang_tua" name="id_orang_tua"><br><br>
                <input type="submit" value="Send Notification">
            </form>
        </body>
    </html>
    '''


@auth_orangtua_bp.route('/chart/nilai', methods=['GET'])
@token_required
def get_chart_nilai(user):
    try:
        orang_tua = user.orang_tua
        if not orang_tua:
            return jsonify({'message': 'Profile not found'}), 404

        siswa = orang_tua.siswa
        if not siswa:
            return jsonify({'message': 'Student not found'}), 404

        # Get all nilai for the student
        nilai_list = db.session.query(
            NilaiAkhir.nilai,
            Mapel.nama_mapel,
            Semester.semester,
            TahunAjaran.tahun
        ).join(
            Pengajaran, NilaiAkhir.id_pengajaran == Pengajaran.id_pengajaran
        ).join(
            Mapel, Pengajaran.id_mapel == Mapel.id_mapel
        ).join(
            Semester, Pengajaran.id_semester == Semester.id
        ).join(
            TahunAjaran, Semester.id_tahun_ajaran == TahunAjaran.id
        ).filter(
            NilaiAkhir.id_siswa == siswa.id_siswa
        ).order_by(
            TahunAjaran.tahun,
            Semester.semester
        ).all()

        # Format data for charts
        chart_data = {
            'labels': [],  # Semester labels
            'datasets': {}  # Data per subject
        }

        # Process data
        for nilai, mapel, semester, tahun in nilai_list:
            period = f"{semester} {tahun}"
            if period not in chart_data['labels']:
                chart_data['labels'].append(period)
            
            if mapel not in chart_data['datasets']:
                chart_data['datasets'][mapel] = {
                    'data': [],
                    'label': mapel
                }
            
            # Ensure data array is filled with nulls up to current position
            while len(chart_data['datasets'][mapel]['data']) < len(chart_data['labels']) - 1:
                chart_data['datasets'][mapel]['data'].append(None)
            
            chart_data['datasets'][mapel]['data'].append(nilai)

        # Calculate statistics
        stats = {
            'highest_score': max([nilai for nilai, _, _, _ in nilai_list], default=0),
            'lowest_score': min([nilai for nilai, _, _, _ in nilai_list], default=0),
            'average_score': sum([nilai for nilai, _, _, _ in nilai_list]) / len(nilai_list) if nilai_list else 0
        }

        result = {
            'chart_data': {
                'labels': chart_data['labels'],
                'datasets': [
                    {
                        'label': subject_data['label'],
                        'data': subject_data['data']
                    }
                    for subject_data in chart_data['datasets'].values()
                ]
            },
            'stats': stats,
            'siswa': {
                'nama': siswa.nama,
                'nisn': siswa.nisn,
                'kelas': siswa.kelas.nama_kelas if siswa.kelas else None
            }
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'message': str(e)}), 500  