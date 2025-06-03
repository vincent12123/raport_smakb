from flask import Blueprint, render_template, redirect, url_for, flash
from app.decorators import admin_required  # Adjust the import path as necessary
from flask_login import login_required
from app import db
from app.models import Sekolah
from app.forms import AddSekolahForm, EditSekolahForm  # Adjust the import path as necessary

crud_sekolah_bp = Blueprint('crud_sekolah', __name__, url_prefix='/crud-sekolah')

@crud_sekolah_bp.route('/add-sekolah', methods=['GET', 'POST'])
@login_required
#@admin_required
def add_sekolah():
    form = AddSekolahForm()
    if form.validate_on_submit():
        sekolah = Sekolah(nama_sekolah=form.nama_sekolah.data, alamat_sekolah=form.alamat_sekolah.data)
        db.session.add(sekolah)
        db.session.commit()
        flash('Sekolah baru telah ditambahkan', 'success')
        return redirect(url_for('list_sekolah'))  # Sesuaikan dengan fungsi tujuan

    return render_template('add_sekolah.html', title='Tambah Sekolah', form=form)

@crud_sekolah_bp.route('/edit-sekolah/<int:id>', methods=['GET', 'POST'])
@login_required
#@admin_required
def edit_sekolah(id):
    sekolah = Sekolah.query.get_or_404(id)
    form = EditSekolahForm(obj=sekolah)
    if form.validate_on_submit():
        sekolah.nama_sekolah = form.nama_sekolah.data
        sekolah.alamat_sekolah = form.alamat_sekolah.data
        db.session.commit()
        flash('Data sekolah telah diperbarui', 'success')
        return redirect(url_for('crud_sekolah.list_sekolah'))
    return render_template('edit_sekolah.html', form=form)

@crud_sekolah_bp.route('/delete-sekolah/<int:id>', methods=['POST'])
@login_required
#@admin_required
def delete_sekolah(id):
    sekolah = Sekolah.query.get_or_404(id)
    db.session.delete(sekolah)
    db.session.commit()
    flash('Sekolah telah dihapus', 'success')
    return redirect(url_for('crud_sekolah.list_sekolah'))


@crud_sekolah_bp.route('/list-sekolah')
@login_required
#@admin_required
def list_sekolah():
    sekolah = Sekolah.query.all()
    return render_template('list_sekolah.html', sekolah=sekolah)
