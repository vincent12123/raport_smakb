from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app.decorators import admin_required
from app.models import Semester,Kelas  # Add this import

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
#@admin_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')



