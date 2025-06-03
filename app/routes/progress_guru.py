from flask import Blueprint, jsonify, render_template

from app import db
from sqlalchemy import func

progress_guru_bp = Blueprint('progress_guru', __name__, url_prefix='/progress_guru')


@progress_guru_bp.route('/',endpoint='progress_guru')
def progress_guru():
    return render_template('progress_guru.html')
