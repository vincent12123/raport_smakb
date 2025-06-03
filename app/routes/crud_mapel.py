from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Kelas, Guru, Mapel, Pengajaran
from app.forms import MapelForm
from app.decorators import admin_required

crud_mapel_bp = Blueprint('crud_mapel', __name__, url_prefix='/crud-mapel')

@crud_mapel_bp.route('/add-mapel', methods=['GET', 'POST'])
@login_required
@admin_required
def add_mapel():
    form = MapelForm()
    form.id_kelas.choices = [(kelas.id_kelas, kelas.nama_kelas) for kelas in Kelas.query.all()]
    form.id_guru.choices = [(guru.id_guru, guru.nama_guru) for guru in Guru.query.all()]  # Menambahkan pilihan guru ke dalam form
    if form.validate_on_submit():
        mapel = Mapel(
            nama_mapel=form.nama_mapel.data,
            deskripsi=form.deskripsi.data,
            jumlah_jam=form.jumlah_jam.data,
            kategori=form.kategori.data,
            id_kelas=form.id_kelas.data,
            id_guru=form.id_guru.data  # Menyimpan id guru yang dipilih dari form
        )
        db.session.add(mapel)
        db.session.commit()
        flash('Mata pelajaran berhasil ditambahkan!')
        return redirect(url_for('list_mapel'))
    return render_template('add_mapel.html', form=form)

@crud_mapel_bp.route('/edit-mapel/<int:id_mapel>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_mapel(id_mapel):
    mapel = Mapel.query.get_or_404(id_mapel)
    form = MapelForm(obj=mapel)
    form.id_kelas.choices = [(kelas.id_kelas, kelas.nama_kelas) for kelas in Kelas.query.all()]
    if form.validate_on_submit():
        mapel.nama_mapel = form.nama_mapel.data
        mapel.deskripsi = form.deskripsi.data
        mapel.jumlah_jam = form.jumlah_jam.data
        mapel.kategori = form.kategori.data
        mapel.id_kelas = form.id_kelas.data
        db.session.commit()
        flash('Mata pelajaran berhasil diperbarui!')
        return redirect(url_for('crud_mapel.list_mapel'))
    return render_template('edit_mapel.html', form=form, mapel=mapel)

@crud_mapel_bp.route('/delete-mapel/<int:id_mapel>', methods=['POST'])
@login_required
@admin_required
def delete_mapel(id_mapel):
    mapel = Mapel.query.get_or_404(id_mapel)
    db.session.delete(mapel)
    db.session.commit()
    flash('Mata pelajaran berhasil dihapus!')
    return redirect(url_for('crud_mapel.list_mapel'))

@crud_mapel_bp.route('/list-mapel')
@login_required
def list_mapel():
    mapel_list = db.session.query(Mapel, Kelas)\
        .join(Pengajaran, Pengajaran.id_mapel == Mapel.id_mapel)\
        .join(Kelas, Pengajaran.id_kelas == Kelas.id_kelas)\
        .all()
    
    # Ubah tampilan `list_mapel.html` agar bisa mengakses nama kelas dari `Kelas` yang sudah di-join
    return render_template('list_mapel.html', mapel_list=mapel_list)
