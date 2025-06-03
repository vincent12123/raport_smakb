# test_db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Siswa, NilaiAkhir, Kelas

engine = create_engine('sqlite:///rapot.db')
Session = sessionmaker(bind=engine)
session = Session()

kelas_id = 1  # Ubah sesuai kebutuhan
results = session.query(Siswa.nama, NilaiAkhir.nilai).join(NilaiAkhir).filter(Siswa.id_kelas == kelas_id).order_by(NilaiAkhir.nilai.desc()).all()

if not results:
    print("No data found.")
else:
    data = [{'nama': row.nama, 'nilai': row.nilai} for row in results]
    print(data)