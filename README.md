# EDA Usaha - Flask Version

Aplikasi web berbasis Flask untuk melakukan Exploratory Data Analysis (EDA) dan processing data usaha, porting dari versi Streamlit.

## Fitur
- Upload data usaha (CSV/Excel) dan data wilayah.
- Cleaning nama kolom dan penamaan usaha.
- Format kode wilayah.
- Klasifikasi bentuk badan hukum (PT, CV, dll).
- Deteksi jaringan usaha.
- Isi nomor WhatsApp dari nomor telepon.
- Export hasil ke Excel dan CSV.

## Cara Menjalankan

1. Pastikan Python sudah terinstall.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   
   or install manually 

   pip install flask flask-session pandas openpyxl
   ```
3. Jalankan aplikasi:
   ```bash
   python app.py
   ```
4. Buka browser dan akses `http://127.0.0.1:5000`

## Struktur File
- `app.py`: Main Flask application.
- `processing.py`: Logika pemrosesan data (core logic).
- `templates/`: HTML templates.
- `static/`: CSS dan assets lainnya.
