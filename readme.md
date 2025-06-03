# Raport Ortu SMA Karya Bangsa

Sistem ini adalah aplikasi web untuk mengelola dan menghasilkan raport siswa SMA Karya Bangsa, termasuk nilai, kehadiran, dan catatan ekstrakurikuler, serta fitur download raport dalam format docx.

## Table of Contents

- [Raport Ortu SMA Karya Bangsa](#raport-ortu-sma-karya-bangsa)
  - [Table of Contents](#table-of-contents)
  - [Pendahuluan](#pendahuluan)
  - [Fitur](#fitur)
  - [Instalasi](#instalasi)
  - [Penggunaan](#penggunaan)
  - [Konfigurasi Database](#konfigurasi-database)
  - [Catatan Tambahan](#catatan-tambahan)

## Pendahuluan

Aplikasi ini memudahkan guru dan admin sekolah dalam:
- Menginput dan mengelola nilai siswa
- Mengelola data kehadiran dan ekstrakurikuler
- Menghasilkan raport otomatis (docx) per siswa/kelas
- Menyediakan dashboard performa siswa dan kelas

## Fitur

- Generate raport per siswa dan per kelas (format docx)
- Rekap nilai, kehadiran, dan ekstrakurikuler
- Download raport satuan atau massal (zip)
- Dashboard performa akademik dan absensi
- Manajemen data siswa, guru, kelas, mapel, semester
- Otentikasi user (admin, guru, orang tua)
- API untuk integrasi data

## Instalasi

1. **Clone repository:**
   ```bash
   git clone https://github.com/your-username/raport_ortu_smakb.git
   cd raport_ortu_smakb
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```
3. **Konfigurasi .env:**
   - Salin file `.env.example` menjadi `.env`
   - Sesuaikan konfigurasi database dan aplikasi lainnya

## Penggunaan

Untuk menjalankan aplikasi, gunakan perintah berikut:
```bash
npm start
```
Akses aplikasi di `http://localhost:3000` pada browser Anda.

## Konfigurasi Database

Aplikasi ini menggunakan database MySQL. Pastikan Anda telah menginstall dan mengkonfigurasi MySQL di sistem Anda. Buat database baru dan import file `schema.sql` untuk membuat tabel yang diperlukan.

## Catatan Tambahan

- Untuk mengubah logo dan nama sekolah pada raport, edit file `config/raport.js`.
- Pastikan semua file laporan disimpan di folder yang benar sesuai konfigurasi.
- Untuk bantuan lebih lanjut, kunjungi [Wiki](https://github.com/your-username/raport_ortu_smakb/wiki) atau hubungi pengembang.
