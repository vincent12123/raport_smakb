from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Semester, SiswaKelas, Pengajaran, TahunAjaran
from app.decorators import admin_required

semester_admin_bp = Blueprint('semester_admin', __name__, url_prefix='/admin/semester')

@semester_admin_bp.route('/change', methods=['GET', 'POST'])
@login_required
#@admin_required
def change_active_semester():
    if request.method == 'POST':
        old_semester_id = request.form.get('old_semester')
        new_semester_id = request.form.get('new_semester')
        
        if old_semester_id == new_semester_id:
            flash('Silakan pilih semester yang berbeda', 'danger')
            return redirect(url_for('semester_admin.change_active_semester'))
            
        try:
            # Deactivate current semester
            old_semester = Semester.query.get(old_semester_id)
            if old_semester:
                old_semester.aktif = False
            
            # Activate new semester
            new_semester = Semester.query.get(new_semester_id)
            if new_semester:
                new_semester.aktif = True
                
                # Get tahun_ajaran value correctly
                tahun_ajaran_obj = TahunAjaran.query.get(new_semester.id_tahun_ajaran)
                tahun_ajaran_value = tahun_ajaran_obj.tahun if tahun_ajaran_obj else ""
                
                # Create new SiswaKelas entries for the new semester
                old_siswa_kelas = SiswaKelas.query.filter_by(id_semester=old_semester_id).all()
                for sk in old_siswa_kelas:
                    # Check if entry already exists to avoid duplicates
                    existing = SiswaKelas.query.filter_by(
                        id_siswa=sk.id_siswa,
                        id_kelas=sk.id_kelas,
                        id_semester=new_semester_id
                    ).first()
                    
                    if not existing:
                        new_sk = SiswaKelas(
                            id_siswa=sk.id_siswa,
                            id_kelas=sk.id_kelas,
                            id_semester=new_semester_id,
                            tahun_ajaran=tahun_ajaran_value
                        )
                        db.session.add(new_sk)
                    
                # Create new Pengajaran entries for the new semester
                old_pengajaran = Pengajaran.query.filter_by(id_semester=old_semester_id).all()
                for p in old_pengajaran:
                    # Check if entry already exists
                    existing = Pengajaran.query.filter_by(
                        id_guru=p.id_guru,
                        id_mapel=p.id_mapel,
                        id_kelas=p.id_kelas,
                        id_semester=new_semester_id
                    ).first()
                    
                    if not existing:
                        new_p = Pengajaran(
                            id_guru=p.id_guru,
                            id_mapel=p.id_mapel,
                            id_kelas=p.id_kelas,
                            id_semester=new_semester_id,
                            tahun_ajaran=tahun_ajaran_value
                        )
                        db.session.add(new_p)
            
            # Commit changes
            db.session.commit()
            flash('Semester berhasil diubah', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error mengubah semester: {str(e)}', 'danger')
            
        return redirect(url_for('admin.dashboard'))
        
    # GET request - display form
    # Fix the order_by clause by joining with TahunAjaran explicitly
    semesters = db.session.query(Semester)\
        .join(TahunAjaran, Semester.id_tahun_ajaran == TahunAjaran.id)\
        .order_by(TahunAjaran.tahun.desc(), Semester.semester.desc())\
        .all()
    
    active_semester = Semester.query.filter_by(aktif=True).first()
    
    return render_template(
        'admin/change_semester.html', 
        semesters=semesters, 
        active_semester=active_semester
    )

@semester_admin_bp.route('/')
@login_required
#@admin_required
def list_semester():
    semesters = db.session.query(Semester)\
        .join(TahunAjaran, Semester.id_tahun_ajaran == TahunAjaran.id)\
        .order_by(TahunAjaran.tahun.desc(), Semester.semester.desc())\
        .all()
    
    return render_template('admin/semester/list.html', semesters=semesters)

@semester_admin_bp.route('/create', methods=['GET', 'POST'])
@login_required
#@admin_required
def create_semester():
    tahun_ajaran_list = TahunAjaran.query.order_by(TahunAjaran.tahun.desc()).all()
    
    if request.method == 'POST':
        try:
            id_tahun_ajaran = request.form.get('id_tahun_ajaran')
            semester = request.form.get('semester')
            fase = request.form.get('fase')
            
            # Validate required fields
            if not id_tahun_ajaran or not semester:
                flash('Tahun ajaran dan semester harus diisi!', 'danger')
                return redirect(url_for('semester_admin.create_semester'))
            
            # Check if semester already exists for this academic year
            existing = Semester.query.filter_by(
                id_tahun_ajaran=id_tahun_ajaran,
                semester=semester
            ).first()
            
            if existing:
                flash('Semester ini sudah ada untuk tahun ajaran yang dipilih!', 'danger')
                return redirect(url_for('semester_admin.create_semester'))
            
            # Create new semester
            new_semester = Semester(
                id_tahun_ajaran=id_tahun_ajaran,
                semester=semester,
                fase=fase,
                aktif=False  # New semesters default to inactive
            )
            
            db.session.add(new_semester)
            db.session.commit()
            
            flash('Semester baru berhasil dibuat!', 'success')
            return redirect(url_for('semester_admin.list_semester'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal membuat semester baru: {str(e)}', 'danger')
    
    return render_template(
        'admin/semester/create.html',
        tahun_ajaran_list=tahun_ajaran_list
    )

@semester_admin_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
#@admin_required
def edit_semester(id):
    semester = Semester.query.get_or_404(id)
    tahun_ajaran_list = TahunAjaran.query.order_by(TahunAjaran.tahun.desc()).all()
    
    if request.method == 'POST':
        try:
            semester.id_tahun_ajaran = request.form.get('id_tahun_ajaran')
            semester.semester = request.form.get('semester')
            semester.fase = request.form.get('fase')
            
            db.session.commit()
            flash('Semester berhasil diupdate!', 'success')
            return redirect(url_for('semester_admin.list_semester'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengupdate semester: {str(e)}', 'danger')
    
    return render_template(
        'admin/semester/edit.html',
        semester=semester,
        tahun_ajaran_list=tahun_ajaran_list
    )

@semester_admin_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
#@admin_required
def delete_semester(id):
    semester = Semester.query.get_or_404(id)
    
    # Don't allow deletion of active semester
    if semester.aktif:
        flash('Tidak dapat menghapus semester yang sedang aktif!', 'danger')
        return redirect(url_for('semester_admin.list_semester'))
    
    # Check if semester has associated data
    if semester.pengajaran_list or semester.siswa_kelas_list:
        flash('Tidak dapat menghapus semester yang memiliki data terkait!', 'danger')
        return redirect(url_for('semester_admin.list_semester'))
    
    try:
        db.session.delete(semester)
        db.session.commit()
        flash('Semester berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus semester: {str(e)}', 'danger')
    
    return redirect(url_for('semester_admin.list_semester'))