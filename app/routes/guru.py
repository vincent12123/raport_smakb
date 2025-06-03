# app/routes/guru.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from functools import wraps
from flask_login import current_user
from flask_login import login_required

from app.models import Guru
from app.forms import GuruForm, EditGuruForm
from app.decorators import admin_required  # Asumsi Anda memiliki dekorator ini

guru_bp = Blueprint('guru', __name__, url_prefix='/guru')
from app import db  # Pastikan 'app' sesuai dengan struktur proyek Anda


@guru_bp.route("/add", methods=['GET', 'POST'])
@login_required
@admin_required
def add_guru():
    form = GuruForm()
    if form.validate_on_submit():
        guru = Guru(nama_guru=form.nama_guru.data, user_id=form.user_id.data)
        db.session.add(guru)
        db.session.commit()
        flash('Guru baru telah ditambahkan', 'success')
        return redirect(url_for('guru.list_guru'))
    return render_template('add_guru.html', title='Tambah Guru', form=form)

@guru_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_guru(id):
    guru = Guru.query.get_or_404(id)
    form = EditGuruForm(obj=guru)
    if form.validate_on_submit():
        guru.nama_guru = form.nama_guru.data
        db.session.commit()
        flash('Data guru telah diperbarui', 'success')
        return redirect(url_for('guru.list_guru'))
    return render_template('edit_guru.html', form=form)

@guru_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_guru(id):
    guru = Guru.query.get_or_404(id)
    db.session.delete(guru)
    db.session.commit()
    flash('Guru telah dihapus', 'success')
    return redirect(url_for('guru.list_guru'))

@guru_bp.route('/list')
@login_required
def list_guru():
    guru = Guru.query.all()
    return render_template('list_guru.html', guru=guru)
