# EDA Usaha - Streamlit App

Aplikasi web interaktif untuk melakukan Exploratory Data Analysis (EDA) pada data usaha menggunakan Streamlit. Aplikasi ini dirancang untuk memproses data usaha yang terus bertambah (ongoing) dengan antarmuka yang mudah digunakan.

## 🎯 Tujuan

Aplikasi ini dibuat untuk memproses dan menganalisis data usaha secara efisien melalui antarmuka web yang user-friendly, sehingga pengguna tidak perlu menulis kode dari awal setiap kali memproses data baru.

## 📦 Fitur Utama

### 1. **Upload & Preview Data**
   - Upload data usaha dalam format CSV atau Excel (.xlsx, .xls)
   - Upload data wilayah (opsional) untuk lookup alamat
   - Preview data original dengan informasi dasar (jumlah rows, columns, duplicates)
   - Auto-detection encoding untuk file CSV (UTF-8, Latin-1, CP1252)

### 2. **Data Processing**
   - **Clean Column Names**: Menghapus newline characters dari nama kolom
   - **Format Kode Wilayah**: Zero-padding otomatis untuk kode provinsi (2 digit), kabupaten (2 digit), kecamatan (3 digit), dan desa (3 digit)
   - **Clean Penamaan Usaha**: Standarisasi format nama usaha dengan memindahkan bentuk badan hukum ke belakang dan mengubah semua jenis kurung menjadi format `<>`
   - **Merge dengan Data Wilayah**: Menggabungkan data usaha dengan lookup table wilayah untuk membuat alamat lengkap
   - **Klasifikasi Bentuk Badan Hukum**: Otomatis mengklasifikasikan bentuk badan hukum berdasarkan nama usaha menggunakan pattern matching
   - **Deteksi Jaringan Usaha**: Mendeteksi format `<XXXX>` dalam nama usaha dan otomatis mengisi `bentuk_badan_hukum_usaha=12` dan `jaringan_usaha=1`
   - **Isi Nomor WhatsApp**: Mengisi kolom nomor WhatsApp yang kosong dari nomor telepon dengan konversi format `08...` menjadi `+628...`

### 3. **Klasifikasi Bentuk Badan Hukum**
   - Visualisasi distribusi bentuk badan hukum dengan pie chart
   - Tabel ringkasan dengan jumlah dan persentase per kategori
   - Daftar sample nama usaha yang belum terklasifikasi
   - **Fitur Tambah Pattern Kustom**: Memungkinkan pengguna menambahkan pattern regex baru untuk meningkatkan akurasi klasifikasi

### 4. **Statistik Data**
   - Informasi detail setiap kolom (tipe data, jumlah non-null, null, unique values)
   - Memory usage dari dataset
   - Data shape (rows × columns)
   - Statistik kolom alamat (jumlah yang terisi)
   - Statistik kolom nomor WhatsApp (jumlah yang terisi)

### 5. **Export Data**
   - Download hasil dalam format **Excel (.xlsx)** dengan format terorganisir:
     - Header kategori di row 1 (IDENTITAS, KEBERADAAN, WILAYAH, KARAKTERISTIK, KEGIATAN, LAIN LAIN)
     - Header kolom di row 2
     - Auto-width columns
     - Freeze panes untuk navigasi mudah
   - Download dalam format **CSV (.csv)** untuk kompatibilitas

## 🚀 Quick Start

### Instalasi Dependencies

```bash
pip install -r requirements.txt
```

Atau install manual:

```bash
pip install streamlit pandas openpyxl plotly
```

### Menjalankan Aplikasi

```bash
streamlit run streamlit_app.py
```

Aplikasi akan otomatis membuka di browser default pada `http://localhost:8501`

## 📖 Panduan Penggunaan

### Langkah 1: Upload Data

1. **Upload Data Usaha** (Wajib)
   - Klik tombol "Browse files" di sidebar
   - Pilih file CSV atau Excel (.xlsx, .xls)
   - File harus memiliki kolom `nama_usaha` untuk klasifikasi
   - Setelah upload, data akan otomatis dimuat dan ditampilkan di tab "Data Preview"

2. **Upload Data Wilayah** (Opsional)
   - Upload file Excel yang berisi lookup table wilayah
   - File harus memiliki kolom: `kdprov`, `kdkab`, `kdkec`, `kddesa`, `nmdesa`, `nmkec`, `nmkab`, `nmprov`
   - Digunakan untuk mengisi kolom `alamat` yang kosong

### Langkah 2: Konfigurasi Pengaturan

1. **Skip Rows**
   - Jumlah baris yang akan dilewati dari atas file saat load data
   - Default: `0` (tidak skip baris)
   - Contoh: `1` untuk skip header pertama, `5` untuk skip 5 baris pertama
   - Berguna jika file memiliki header atau baris kosong di awal

2. **Kode Kota**
   - Masukkan kode kabupaten yang sebenarnya adalah Kota (bukan Kabupaten)
   - Default: `71` (Kota Gorontalo)
   - Untuk multiple kode, pisahkan dengan koma: `71,72,73`
   - Digunakan untuk menentukan prefix "Kota" vs "Kabupaten" saat membuat alamat

3. **Format Output**
   - Pilih format output: Excel (.xlsx) atau CSV (.csv)
   - Masukkan nama file output (default: `hasil_eda`)

### Langkah 3: Proses Data

1. Buka tab **"🔧 Processing"**
2. Pilih langkah-langkah processing yang diinginkan:
   - ✅ **Clean column names**: Bersihkan nama kolom dari karakter newline
   - ✅ **Format kode wilayah**: Format kode wilayah dengan zero-padding
   - ✅ **Clean penamaan usaha**: Standarisasi format nama usaha (memindahkan bentuk badan hukum ke belakang, mengubah kurung menjadi `<>`)
   - ✅ **Merge dengan data wilayah**: Gabungkan dengan data wilayah (hanya aktif jika file wilayah diupload)
   - ✅ **Klasifikasi bentuk badan hukum**: Klasifikasi otomatis berdasarkan nama usaha
   - ✅ **Deteksi jaringan usaha tunggal/perorangan (format <XXXX>)**: Deteksi format `<XXXX>` dan isi `bentuk_badan_hukum_usaha=12` dan `jaringan_usaha=1`
   - ✅ **Isi nomor WhatsApp dari nomor telepon**: Konversi nomor telepon format `08...` menjadi nomor WhatsApp format `+628...`
3. Klik tombol **"🚀 Proses Data"**
4. Tunggu proses selesai (progress bar akan menampilkan progress)
5. Data yang sudah diproses akan tersimpan di session state dan dapat dilihat di tab lainnya

### Langkah 4: Analisis & Review

1. **Tab "📊 Klasifikasi Badan Hukum"**
   - Lihat distribusi bentuk badan hukum dalam bentuk tabel dan pie chart
   - Review sample nama usaha yang belum terklasifikasi
   - Tambah pattern kustom jika diperlukan:
     - Pilih kode kategori
     - Masukkan regex pattern
     - Klik "Apply Pattern" untuk mengklasifikasikan data yang cocok

2. **Tab "📈 Statistik"**
   - Review informasi detail setiap kolom
   - Cek memory usage dan data shape
   - Verifikasi kelengkapan data (terutama kolom alamat dan nomor WhatsApp)

### Langkah 5: Download Hasil

1. Buka tab **"💾 Download"**
2. Preview data yang akan didownload (opsional)
3. Klik tombol download sesuai format yang dipilih:
   - **📥 Download Excel (.xlsx)**: Format terorganisir dengan header kategori
   - **📥 Download CSV (.csv)**: Format standar CSV

## 📊 Klasifikasi Bentuk Badan Hukum

Aplikasi mengklasifikasikan bentuk badan hukum ke dalam 12 kategori berdasarkan pattern matching pada nama usaha:

| Kode | Bentuk Badan Hukum | Contoh Pattern |
|------|-------------------|----------------|
| 1 | Perseroan (PT) | PT, P.T, PERSEROAN, PERSERO |
| 2 | Yayasan | YAYASAN, YYS |
| 3 | Koperasi | KOPERASI, KOP, KOPKAR, KSU, KSP, KUD |
| 4 | Dana Pensiun | DANA PENSIUN, DAPEN, DP |
| 5 | Perum/Perumda | PERUM, PERUMDA, PERUMNAS |
| 6 | BUM Desa | BUMDES, BUM DESA |
| 7 | CV | CV, C.V |
| 8 | Firma | FIRMA, FA |
| 9 | Persekutuan Perdata | PERSEKUTUAN, MAATSCHAP |
| 10 | Kantor Perwakilan LN | PERWAKILAN, REPRESENTATIVE OFFICE |
| 11 | Badan Usaha LN | LLC, LTD, LIMITED, INC, INCORPORATED, CORP, GMBH, AG, BV, NV |
| 12 | Usaha Perseorangan | UD, U.D, PD, TOKO, WARUNG, KIOS, KEDAI, DEPOT, SALON, BENGKEL, LAUNDRY, dll |
| 99 | Lainnya | Tidak terklasifikasi |

### Menambah Pattern Kustom

Jika ada nama usaha yang belum terklasifikasi, Anda dapat menambahkan pattern regex kustom:

1. Buka tab **"📊 Klasifikasi Badan Hukum"**
2. Scroll ke bagian **"➕ Tambah Pattern Kustom"**
3. Pilih kode kategori yang sesuai
4. Masukkan regex pattern (contoh: `(?i)\b(KEYWORD1|KEYWORD2)\b`)
5. Klik **"Apply Pattern"**
6. Data yang cocok dengan pattern akan langsung terklasifikasi

**Tips Pattern Regex:**
- `(?i)` = case-insensitive matching
- `\b` = word boundary
- `|` = OR operator
- Contoh: `(?i)\b(TOKO|WARUNG|KIOS)\b` akan match "Toko", "WARUNG", atau "kios"

## 🔧 Detail Fitur Processing

### 1. Clean Column Names
- Menghapus karakter newline (`\n`) dari nama kolom
- Berguna jika nama kolom memiliki line breaks yang tidak diinginkan

### 2. Format Kode Wilayah
- **kdprov**: Format menjadi 2 digit (contoh: `1` → `01`, `71` → `71`)
- **kdkab**: Format menjadi 2 digit (contoh: `1` → `01`, `71` → `71`)
- **kdkec**: Format menjadi 3 digit (contoh: `1` → `001`, `71` → `071`)
- **kddesa**: Format menjadi 3 digit (contoh: `1` → `001`, `71` → `071`)

### 3. Clean Penamaan Usaha
Fitur ini melakukan standarisasi format nama usaha dengan aturan berikut:

1. **Mengubah semua jenis kurung menjadi format `<>`**:
   - Kurung biasa `(content)` → `<content>`
   - Kurung siku `[content]` → `<content>`
   - Kurung kurawal `{content}` → `<content>`
   - Tanda kutip ganda `"content"` → `<content>`
   - Tanda kutip tunggal `'content'` → `<content>`
   - Backtick `` `content` `` → `<content>`

2. **Memindahkan bentuk badan hukum dari depan ke belakang**:
   - `PT. ANJUNG MAKMUR` → `ANJUNG MAKMUR, PT`
   - `CV. KARTIKA PUTRI` → `KARTIKA PUTRI, CV`
   - `UD. TOKO MAKMUR` → `TOKO MAKMUR, UD`

3. **Menangani bentuk badan hukum di belakang dengan titik**:
   - `MAKALE TORAJA MINING. PT` → `MAKALE TORAJA MINING, PT`
   - `PERUSAHAAN ABC CV.` → `PERUSAHAAN ABC, CV`

4. **Membersihkan spasi ganda dan koma berulang**

**Contoh Transformasi:**
- `PT. ANJUNG MAKMUR` → `ANJUNG MAKMUR, PT`
- `CV. KARTIKA PUTRI` → `KARTIKA PUTRI, CV`
- `MAKALE TORAJA MINING. PT` → `MAKALE TORAJA MINING, PT`
- `JUAL BELI ROTAN (ARDIN)` → `JUAL BELI ROTAN <ARDIN>`
- `TOKO "MAKMUR"` → `TOKO <MAKMUR>`

**Catatan**: Jika nama usaha sudah dalam format yang benar (sudah ada `, PT`, `, CV`, dll di belakang), maka hanya akan dilakukan cleaning kurung saja, tanpa memproses bentuk badan hukum.

### 4. Merge dengan Data Wilayah
Proses merge akan:
1. Format kode wilayah di lookup table
2. Membuat kolom `alamat_new` dari data wilayah dengan format:
   - "Desa [nama_desa], Kecamatan [nama_kec], [Kota/Kabupaten] [nama_kab], Provinsi [nama_prov]"
3. Merge dengan data usaha berdasarkan kode wilayah (kdprov, kdkab, kdkec, kddesa)
4. Mengisi kolom `alamat` yang kosong dengan `alamat_new`
5. Fallback mechanism:
   - Jika tidak match di level desa, coba match di level kecamatan
   - Jika tidak match di level kecamatan, coba match di level kabupaten
   - Jika tidak match di level kabupaten, coba match di level provinsi
   - Jika semua gagal, gunakan format kode: "[Kode: Prov:XX, Kab:XX, Kec:XXX, Desa:XXX]"

**Catatan**: Proses ini hanya mengisi kolom alamat yang **kosong**. Alamat yang sudah ada tidak akan di-overwrite.

### 5. Klasifikasi Bentuk Badan Hukum
- Menggunakan pattern matching dengan regex
- Case-insensitive (tidak membedakan huruf besar/kecil)
- Mencari pattern di seluruh nama usaha
- Overwrite kolom `bentuk_badan_hukum_usaha` dengan kode yang sesuai
- Jika tidak ada pattern yang match, kolom akan diisi `None`

### 6. Deteksi Jaringan Usaha
Fitur ini mendeteksi format `<XXXX>` dalam nama usaha dan secara otomatis:
- Mengisi `bentuk_badan_hukum_usaha` dengan kode `12` (Usaha Perseorangan)
- Mengisi `jaringan_usaha` dengan nilai `1`

**Contoh:**
- `PANGKAS RAMBUT MDC < APDIANTO RIO TUBUAN >` → Terdeteksi sebagai jaringan usaha
- `TOKO MAKMUR <JOHN DOE>` → Terdeteksi sebagai jaringan usaha

**Catatan**: Fitur ini akan override hasil klasifikasi bentuk badan hukum sebelumnya jika terdeteksi format `<XXXX>`.

### 7. Isi Nomor WhatsApp
Fitur ini mengisi kolom `nomor_whatsapp` yang kosong dari kolom `nomor_telepon` dengan konversi format:
- Nomor telepon format `08...` → Nomor WhatsApp format `+628...`
- Hanya nomor yang dimulai dengan `08` yang akan dikonversi
- Karakter non-digit akan dihapus sebelum konversi

**Contoh:**
- `081234567890` → `+6281234567890`
- `0812-3456-7890` → `+6281234567890`
- `0812 3456 7890` → `+6281234567890`

**Catatan**: 
- Hanya mengisi kolom `nomor_whatsapp` yang **kosong**
- Nomor WhatsApp yang sudah ada tidak akan di-overwrite
- Jika nomor telepon tidak dimulai dengan `08`, tidak akan dikonversi

## 📁 Struktur File

```
BPS/script/eda_umkm/
├── streamlit_app.py      # Aplikasi Streamlit utama
├── requirements.txt      # Dependencies Python
├── readme.MD            # Dokumentasi (file ini)
└── [data files]         # File data input/output pengguna
```

## 📋 Format Data Input

### Data Usaha
**Kolom Wajib:**
- `nama_usaha`: Untuk klasifikasi bentuk badan hukum

**Kolom Opsional (untuk format kode wilayah):**
- `kdprov`: Kode provinsi
- `kdkab`: Kode kabupaten
- `kdkec`: Kode kecamatan
- `kddesa`: Kode desa

**Kolom Opsional (untuk merge wilayah):**
- `alamat`: Kolom alamat (akan diisi jika kosong)

**Kolom Opsional (untuk fill nomor WhatsApp):**
- `nomor_telepon`: Kolom nomor telepon (digunakan untuk mengisi nomor WhatsApp)
- `nomor_whatsapp`: Kolom nomor WhatsApp (akan diisi jika kosong)

**Kolom Opsional (untuk deteksi jaringan usaha):**
- `jaringan_usaha`: Kolom jaringan usaha (akan diisi dengan `1` jika terdeteksi format `<XXXX>`)

### Data Wilayah (Lookup Table)
**Kolom Wajib:**
- `kdprov`: Kode provinsi
- `kdkab`: Kode kabupaten
- `kdkec`: Kode kecamatan
- `kddesa`: Kode desa
- `nmprov`: Nama provinsi
- `nmkab`: Nama kabupaten
- `nmkec`: Nama kecamatan
- `nmdesa`: Nama desa

## 💡 Tips & Best Practices

1. **Data Besar**: Untuk dataset yang sangat besar (>100K rows), proses merge wilayah mungkin memakan waktu. Sabar menunggu progress bar.

2. **Encoding CSV**: Jika file CSV tidak terbaca dengan benar, coba ubah encoding file ke UTF-8 atau gunakan format Excel.

3. **Skip Rows**: Gunakan fitur "Skip Rows" jika file memiliki header ganda atau baris kosong di awal. Contoh: jika ada 2 baris header, set skip rows = 1 untuk melewati header pertama.

4. **Clean Nama Usaha**: Fitur ini akan memindahkan bentuk badan hukum ke belakang dan mengubah semua kurung menjadi format `<>`. Pastikan ini sesuai dengan kebutuhan Anda sebelum memproses.

5. **Deteksi Jaringan Usaha**: Fitur ini akan override klasifikasi bentuk badan hukum jika terdeteksi format `<XXXX>`. Pastikan format ini memang menunjukkan jaringan usaha sebelum mengaktifkan fitur ini.

6. **Nomor WhatsApp**: Konversi hanya berlaku untuk nomor yang dimulai dengan `08`. Nomor dengan format lain (misalnya `+62`, `62`, atau `021`) tidak akan dikonversi.

7. **Klasifikasi**: Review sample yang tidak terklasifikasi secara berkala dan tambahkan pattern baru untuk meningkatkan akurasi.

8. **Backup Data**: Selalu backup data original sebelum memproses, terutama jika melakukan overwrite.

9. **Format Excel**: Format Excel output sudah terorganisir dengan header kategori. Jika perlu menyesuaikan, edit langsung di Excel setelah download.

10. **Session State**: Data yang sudah diproses tersimpan di session state. Refresh browser akan menghapus session state, jadi pastikan sudah download hasil sebelum refresh.

## ⚠️ Catatan Penting

- **Data tidak tersimpan permanen**: Aplikasi ini tidak menyimpan data ke server. Semua data hanya ada di session browser. Refresh browser akan menghapus semua data yang sudah diproses.

- **File upload limit**: Streamlit memiliki default upload limit. Untuk file yang sangat besar, pertimbangkan untuk memproses dalam batch atau meningkatkan limit di konfigurasi Streamlit.

- **Kolom alamat**: Proses merge hanya mengisi kolom alamat yang **kosong**. Alamat yang sudah ada tidak akan diubah.

- **Kode wilayah**: Pastikan format kode wilayah di data input sudah benar. Aplikasi akan melakukan zero-padding, tapi jika format awal salah, hasilnya mungkin tidak sesuai.

## 🐛 Troubleshooting

### Data tidak ter-load
- Pastikan format file benar (CSV atau Excel)
- Cek encoding file CSV (coba ubah ke UTF-8)
- Pastikan file tidak corrupt

### Merge wilayah tidak bekerja
- Pastikan file wilayah sudah diupload
- Cek kolom kode wilayah di data usaha dan data wilayah sudah sesuai
- Pastikan format kode wilayah sudah benar (akan diformat otomatis)

### Klasifikasi tidak akurat
- Review sample yang tidak terklasifikasi
- Tambahkan pattern kustom untuk kategori yang sering muncul
- Pastikan nama usaha tidak terlalu singkat atau ambigu

### Download Excel error
- Pastikan tidak ada karakter khusus di nama file output
- Cek memory tersedia (untuk file besar)
- Coba download format CSV sebagai alternatif

### Nomor WhatsApp tidak terisi
- Pastikan kolom `nomor_telepon` ada dan berisi data
- Pastikan nomor telepon dimulai dengan `08` (format Indonesia)
- Cek apakah kolom `nomor_whatsapp` sudah ada di data (akan dibuat otomatis jika tidak ada)

### Clean nama usaha tidak bekerja sesuai harapan
- Pastikan nama usaha tidak terlalu kompleks atau memiliki format yang tidak standar
- Cek hasil cleaning di preview sebelum melanjutkan proses
- Jika perlu, edit manual di Excel setelah download

## 📝 Changelog

### Versi 1.0
- Upload data usaha (CSV/Excel)
- Upload data wilayah (opsional)
- Skip rows setting untuk load data
- Clean column names
- Format kode wilayah
- Clean penamaan usaha (standarisasi format)
- Merge dengan data wilayah
- Klasifikasi bentuk badan hukum (12 kategori)
- Deteksi jaringan usaha dari format `<XXXX>`
- Isi nomor WhatsApp dari nomor telepon
- Statistik data (termasuk statistik nomor WhatsApp)
- Export Excel dengan format terorganisir
- Export CSV
- Tambah pattern kustom untuk klasifikasi

## 📞 Support

Untuk pertanyaan atau masalah, silakan hubungi tim pengembang atau buat issue di repository project.

---

**Happy Analyzing! 📊**
