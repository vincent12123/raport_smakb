from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Kelas, Guru
from app.forms import KelasForm
from app.decorators import admin_required

crud_kelas_bp = Blueprint('crud_kelas', __name__, url_prefix='/crud-kelas')

@crud_kelas_bp.route('/add-kelas', methods=['GET', 'POST'])
@login_required
@admin_required
def add_kelas():
    form = KelasForm()
    # Isi pilihan id_guru dengan daftar guru
    form.id_guru.choices = [(guru.id_guru, guru.nama_guru) for guru in Guru.query.all()]
    
    if form.validate_on_submit():
        kelas = Kelas(nama_kelas=form.nama_kelas.data, tingkat=form.tingkat.data, id_guru=form.id_guru.data)
        db.session.add(kelas)
        db.session.commit()
        flash('Kelas baru telah ditambahkan', 'success')
        return redirect(url_for('list_kelas'))

    return render_template('add_kelas.html', form=form)

@crud_kelas_bp.route('/edit-kelas/<int:id_kelas>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_kelas(id_kelas):
    kelas = Kelas.query.get_or_404(id_kelas)
    form = KelasForm(obj=kelas)
    form.id_guru.choices = [(guru.id_guru, guru.nama_guru) for guru in Guru.query.all()]
    if form.validate_on_submit():
        form.populate_obj(kelas)
        db.session.commit()
        flash('Kelas berhasil diubah', 'success')
        return redirect(url_for('list_kelas'))
    return render_template('edit_kelas.html', form=form, kelas=kelas)

@crud_kelas_bp.route('/delete-kelas/<int:id_kelas>', methods=['POST'])
@login_required
@admin_required
def delete_kelas(id_kelas):
    kelas = Kelas.query.get_or_404(id_kelas)
    db.session.delete(kelas)
    db.session.commit()
    flash('Kelas telah dihapus', 'success')
    return redirect(url_for('list_kelas'))

@crud_kelas_bp.route('/list-kelas')
@login_required
def list_kelas():
    
    kelas = Kelas.query.all()
    return render_template('list_kelas.html', kelas=kelas)

