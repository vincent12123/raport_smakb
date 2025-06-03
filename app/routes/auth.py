from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash
from app.forms import RegistrationForm
from app import db
from app.models import User
from app.forms import LoginForm
from app.models import Message

auth_bp = Blueprint('auth', __name__)
 

@auth_bp.route("/")
def index():
    return redirect(url_for('auth.login'))

# auth.py

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            # Periksa role pengguna dan arahkan ke dashboard yang sesuai
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'guru':
                return redirect(url_for('guru.list_guru'))  # Sesuaikan dengan Blueprint 'guru'
            elif user.role == 'orangtua':
                return redirect(url_for('orangtua.dashboard'))  # Sesuaikan dengan Blueprint 'orangtua'
            else:
                # Jika role tidak dikenal, arahkan ke halaman utama atau halaman error
                flash('Role pengguna tidak dikenal', 'danger')
                return redirect(url_for('auth.login'))
        else:
            flash('Login Gagal. Silakan periksa username dan password', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash('Anda telah berhasil logout', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # Pengguna yang sudah login tidak perlu registrasi

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', title='Register', form=form)

@auth_bp.route('/create', methods=['POST'])
def create():
    new_message = request.form.get('new_message')
    if new_message:
        message = Message(message=new_message)
        db.session.add(message)
        db.session.commit()
    return redirect(url_for('admin.dashboard'))
