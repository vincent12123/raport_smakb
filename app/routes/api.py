# app/routes/api.py
from flask import Blueprint, jsonify
from app.models import Semester, Kelas, Siswa, RekapAbsensi, TahunAjaran, NilaiAkhir,Pengajaran, Mapel, Guru  # Pastikan model ini ada
from app import db
from sqlalchemy import func

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/classes')
def get_classes():
    classes = Kelas.query.order_by(Kelas.nama_kelas.asc()).all()
    data = [{'id': kelas.id_kelas, 'nama': kelas.nama_kelas} for kelas in classes]
    return jsonify(data)

@api_bp.route('/semesterall')
def get_semester_all():
    # Mengambil semua semester, diurutkan berdasarkan tahun ajaran (tahun) dan semester
    semesters = Semester.query.join(Semester.tahun_ajaran).order_by(TahunAjaran.tahun.asc(), Semester.semester.asc()).all()

    if not semesters:
        return jsonify({"message": "No semesters found"}), 404

    # Menyiapkan data untuk dikembalikan dalam format JSON
    data = [{
        'id': semester.id,
        'tahun_ajaran': semester.tahun_ajaran.tahun if semester.tahun_ajaran else None,  # Akses atribut 'tahun' dari relasi TahunAjaran
        'semester': semester.semester
    } for semester in semesters]
    
    # Mengembalikan data sebagai respons JSON
    return jsonify(data), 200


@api_bp.route('/classes_absensi')
def get_classes_absensi():
    classes = Kelas.query.order_by(Kelas.nama_kelas.asc()).all()

    if not classes:
        return jsonify({"message": "No classes found"}), 404

    data = [{'id': kelas.id_kelas, 'nama': kelas.nama_kelas} for kelas in classes]
    return jsonify(data)

@api_bp.route('/class_absensi/<int:class_id>/<int:semester_id>')
def class_absensi(class_id, semester_id):
    results = db.session.query(
        Siswa.nama,
        func.sum(RekapAbsensi.total_sakit).label('total_sakit'),
        func.sum(RekapAbsensi.total_izin).label('total_izin'),
        func.sum(RekapAbsensi.total_tanpa_keterangan).label('total_tanpa_keterangan')
    ).join(RekapAbsensi).filter(
        Siswa.id_kelas == class_id,
        RekapAbsensi.id_semester == semester_id
    ).group_by(Siswa.id_siswa).all()

    data = [{'nama': row.nama, 'total_sakit': row.total_sakit, 'total_izin': row.total_izin, 'total_tanpa_keterangan': row.total_tanpa_keterangan} for row in results]
    return jsonify(data)
 
@api_bp.route('/students_in_class/<int:class_id>')
def get_students_in_class(class_id):
    # Validasi apakah class_id ada
    kelas = Kelas.query.get(class_id)
    if not kelas:
        # Jika kelas tidak ditemukan, kembalikan pesan error
        return jsonify({"message": "Class not found"}), 404

    # Ambil daftar siswa di kelas yang dipilih
    students = Siswa.query.filter_by(id_kelas=class_id).order_by(Siswa.nama.asc()).all()

    # Jika tidak ada siswa ditemukan, kembalikan pesan error
    if not students:
        return jsonify({"message": "No students found in this class"}), 404

    # Jika siswa ditemukan, kembalikan data dalam bentuk JSON
    data = [{'id': student.id_siswa, 'nama': student.nama} for student in students]
    return jsonify(data)

@api_bp.route('/ranking_per_class/<int:class_id>/<int:semester_id>')
def get_ranking_per_class(class_id, semester_id):
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

    data = [{'nama': row.nama, 'avg_nilai': round(row.avg_nilai, 2)} for row in results]
    return jsonify(data)

@api_bp.route('/student_subject_scores/<int:student_id>')
def get_student_subject_scores(student_id):
    # Validasi apakah student_id ada
    student = Siswa.query.get(student_id)
    if not student:
        return jsonify({"message": "Student not found"}), 404

    results = db.session.query(
        Mapel.nama_mapel,
        Semester.semester,
        func.avg(NilaiAkhir.nilai).label('avg_nilai')
    ).select_from(NilaiAkhir)\
     .join(Pengajaran, Pengajaran.id_pengajaran == NilaiAkhir.id_pengajaran)\
     .join(Mapel, Pengajaran.id_mapel == Mapel.id_mapel)\
     .join(Semester, Pengajaran.id_semester == Semester.id)\
     .filter(NilaiAkhir.id_siswa == student_id)\
     .group_by(Mapel.nama_mapel, Semester.semester)\
     .order_by(Semester.semester).all()

    if not results:
        return jsonify({"message": "No subject scores found for this student"}), 404

    data = [{'mapel': row.nama_mapel, 'semester': row.semester, 'avg_nilai': round(row.avg_nilai, 2)} for row in results]
    return jsonify(data)

# API to get top performers
@api_bp.route('/top_performers/<int:class_id>/<int:semester_id>')
def get_top_performers(class_id, semester_id):
    top_students = db.session.query(
        Siswa.nama,
        Mapel.nama_mapel,
        func.avg(NilaiAkhir.nilai).label('avg_nilai')
    ).join(NilaiAkhir, Siswa.id_siswa == NilaiAkhir.id_siswa)\
    .join(Pengajaran, NilaiAkhir.id_pengajaran == Pengajaran.id_pengajaran)\
    .join(Mapel, Pengajaran.id_mapel == Mapel.id_mapel)\
    .filter(Siswa.id_kelas == class_id, Pengajaran.id_semester == semester_id)\
    .group_by(Siswa.id_siswa, Mapel.id_mapel)\
    .order_by(func.avg(NilaiAkhir.nilai).desc())\
    .limit(5).all()

    if not top_students:
        return jsonify({"message": "No data found for this class and semester"}), 404

    # Organizing the data for radar chart
    students = {}
    subjects = set()

    for student, subject, avg_nilai in top_students:
        if student not in students:
            students[student] = {}
        students[student][subject] = avg_nilai
        subjects.add(subject)

    subjects = list(subjects)
    data = {
        'subjects': subjects,
        'students': [
            {
                'name': student,
                'scores': [students[student].get(subject, 0) for subject in subjects]
            }
        for student in students]
    }

    return jsonify(data)

# API to get individual student performance in a specific class and semester
@api_bp.route('/student_performance/<int:class_id>/<int:semester_id>/<int:student_id>')
def get_student_performance(class_id, semester_id, student_id):
    # Query individual student performance
    student_results = db.session.query(
        Mapel.nama_mapel,
        NilaiAkhir.nilai
    ).join(Pengajaran, NilaiAkhir.id_pengajaran == Pengajaran.id_pengajaran)\
     .join(Mapel, Pengajaran.id_mapel == Mapel.id_mapel)\
     .filter(
         Pengajaran.id_kelas == class_id,
         Pengajaran.id_semester == semester_id,
         NilaiAkhir.id_siswa == student_id
     ).all()

    if not student_results:
        return jsonify({"message": "No performance data found for this student"}), 404

    # Extract subjects and student scores
    subjects = [row.nama_mapel for row in student_results]
    student_scores = [row.nilai for row in student_results]

    # Calculate class average for each subject
    class_averages = []
    for subject in subjects:
        avg_result = db.session.query(
            db.func.avg(NilaiAkhir.nilai)
        ).join(Pengajaran, NilaiAkhir.id_pengajaran == Pengajaran.id_pengajaran)\
         .join(Mapel, Pengajaran.id_mapel == Mapel.id_mapel)\
         .filter(
             Pengajaran.id_kelas == class_id,
             Pengajaran.id_semester == semester_id,
             Mapel.nama_mapel == subject
         ).scalar()  # `scalar()` to get a single value from avg function

        class_averages.append(round(avg_result, 2) if avg_result else 0)

    # Prepare JSON response
    data = {
        "subjects": subjects,
        "scores": student_scores,
        "class_average": class_averages
    }
    return jsonify(data)


@api_bp.route('/progress_per_class/<int:class_id>/<int:semester_id>')
def get_progress_per_class(class_id, semester_id):
    # Calculate the total number of students in the class
    total_students = db.session.query(Siswa).filter_by(id_kelas=class_id).count()

    # Handle the case where there are no students in the class to avoid division by zero
    if total_students == 0:
        return jsonify([])

    # Query to get progress for each teacher and subject
    results = db.session.query(
        Guru.nama_guru,
        Mapel.nama_mapel,
        func.count(NilaiAkhir.id_nilai).label('nilai_count'),
        (func.count(NilaiAkhir.id_nilai) * 100 / total_students).label('progress')
    ).join(Pengajaran, Pengajaran.id_pengajaran == NilaiAkhir.id_pengajaran) \
     .join(Guru, Pengajaran.id_guru == Guru.id_guru) \
     .join(Mapel, Pengajaran.id_mapel == Mapel.id_mapel) \
     .filter(Pengajaran.id_kelas == class_id, Pengajaran.id_semester == semester_id) \
     .group_by(Guru.nama_guru, Mapel.nama_mapel).all()

    data = [{'guru': row.nama_guru, 'mapel': row.nama_mapel, 'progress': round(row.progress, 2)} for row in results]
    return jsonify(data)

# API to get attendance data for a student
@api_bp.route('/attendance/<int:student_id>', methods=['GET'])
def get_attendance(student_id):
    attendance = db.session.query(RekapAbsensi).filter_by(id_siswa=student_id).first()

    if not attendance:
        return jsonify({"message": "No attendance data found for this student"}), 404

    data = {
        'total_sakit': attendance.total_sakit,
        'total_izin': attendance.total_izin,
        'total_tanpa_keterangan': attendance.total_tanpa_keterangan
    }
    return jsonify(data)

# API to get ranking in a class for a specific semester
@api_bp.route('/ranking/<int:class_id>/<int:semester_id>', methods=['GET'])
def get_ranking(class_id, semester_id):
    ranking_data = db.session.query(
        Siswa.nama,
        func.rank().over(
            order_by=func.avg(NilaiAkhir.nilai).desc()
        ).label('rank')
    ).join(NilaiAkhir, Siswa.id_siswa == NilaiAkhir.id_siswa)\
    .join(Pengajaran, NilaiAkhir.id_pengajaran == Pengajaran.id_pengajaran)\
    .filter(
        Pengajaran.id_kelas == class_id,
        Pengajaran.id_semester == semester_id
    ).group_by(Siswa.id_siswa).all()

    if not ranking_data:
        return jsonify({"message": "No ranking data found for this class and semester"}), 404

    data = [{'nama': nama, 'rank': rank} for nama, rank in ranking_data]
    return jsonify(data)

