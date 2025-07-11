=== Panduan Menjalankan Proyek Ini ===

Ikuti langkah-langkah berikut untuk menjalankan aplikasi secara lokal:

1. Clone Repository
-------------------
Clone terlebih dahulu repository ini ke komputer kamu:

    git clone https://github.com/ichsanmust/python_fast_api_template.git
    cd python_fast_api_template

2. Pastikan Python & pip Sudah Terinstall
-----------------------------------------
- Gunakan Python versi terbaru (disarankan ≥ 3.9)
- Periksa apakah sudah terinstall dengan perintah berikut:

    python --version
    pip --version

3. Buat Virtual Environment
---------------------------
Buat environment virtual agar dependensi terisolasi:

    python -m venv ..python_fast_api_template

atau 
    python3 -m venv ..python_fast_api_template

4. Aktifkan Virtual Environment
-------------------------------
- Windows:

    .python_fast_api_template\Scripts\activate

- macOS/Linux:

    source .python_fast_api_template/bin/activate

5. Install Dependencies
-----------------------
Install semua pustaka yang dibutuhkan dari file requirements.txt:

    pip install -r requirements.txt

6. Buat Database di mysql dan sesuaikan file .env, import file sql di mysql/import.sql ke database tersebut
--------------------

7. Jalankan Aplikasi
--------------------
Gunakan perintah berikut untuk menjalankan aplikasi secara lokal di port 8000:

    uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

Lalu buka browser dan akses: http://localhost:9000 atau http://0.0.0.0:9000
Untuk Rapidoc : http://localhost:9000/rapidoc atau http://0.0.0.0:9000/rapidoc
Untuk Scalar : http://localhost:9000/scalar atau http://0.0.0.0:9000/scalar


9. Test dengan endpoint /auth/signup (create user)
--------------------

Catatan:
--------
- Gunakan --reload hanya saat development (otomatis reload saat ada perubahan kode).
- Untuk produksi, pertimbangkan menjalankan dengan gunicorn + uvicorn.workers.UvicornWorker.
