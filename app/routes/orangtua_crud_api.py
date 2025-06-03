from flask import Blueprint, request, jsonify
from app import db
from app.models import OrangTua, Siswa

orangtua_api_bp = Blueprint('orangtua_api', __name__, url_prefix='/api/orangtua')

@orangtua_api_bp.route('/', methods=['GET'])
def get_all_orangtua():
    orangtua_list = OrangTua.query.all()
    result = []
    for orangtua in orangtua_list:
        result.append({
            'id_orang_tua': orangtua.id_orang_tua,
            'id_siswa': orangtua.id_siswa,
            'nama_orang_tua': orangtua.nama_orang_tua,
            'nomor_whatsapp': orangtua.nomor_whatsapp,
            'nama_siswa': orangtua.siswa.nama if orangtua.siswa else None
        })
    return jsonify(result)

@orangtua_api_bp.route('/<int:id>', methods=['GET'])
def get_orangtua(id):
    orangtua = OrangTua.query.get_or_404(id)
    result = {
        'id_orang_tua': orangtua.id_orang_tua,
        'id_siswa': orangtua.id_siswa,
        'nama_orang_tua': orangtua.nama_orang_tua,
        'nomor_whatsapp': orangtua.nomor_whatsapp,
        'nama_siswa': orangtua.siswa.nama if orangtua.siswa else None
    }
    return jsonify(result)

@orangtua_api_bp.route('/', methods=['POST'])
def create_orangtua():
    data = request.get_json()
    new_orangtua = OrangTua(
        id_siswa=data['id_siswa'],
        nama_orang_tua=data['nama_orang_tua'],
        nomor_whatsapp=data['nomor_whatsapp']
    )
    db.session.add(new_orangtua)
    db.session.commit()
    return jsonify({'message': 'OrangTua created successfully'}), 201

@orangtua_api_bp.route('/<int:id>', methods=['PUT'])
def update_orangtua(id):
    data = request.get_json()
    orangtua = OrangTua.query.get_or_404(id)
    orangtua.id_siswa = data['id_siswa']
    orangtua.nama_orang_tua = data['nama_orang_tua']
    orangtua.nomor_whatsapp = data['nomor_whatsapp']
    db.session.commit()
    return jsonify({'message': 'OrangTua updated successfully'})

@orangtua_api_bp.route('/<int:id>', methods=['DELETE'])
def delete_orangtua(id):
    orangtua = OrangTua.query.get_or_404(id)
    db.session.delete(orangtua)
    db.session.commit()
    return jsonify({'message': 'OrangTua deleted successfully'})