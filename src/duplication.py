import pandas as pd
import numpy as np
import io
import re
from difflib import SequenceMatcher
from openpyxl import load_workbook

# ==========================================
# KONFIGURASI (Dari Flask)
# ==========================================
HEADER_ROW_PANDAS = 1
DATA_START_ROW_EXCEL = 3

COL_INDEX_IDSBR = 1
COL_INDEX_STATUS = 13
COL_INDEX_MASTER_ID = 14

THRESHOLD = 0.98

KAMUS_TYPO = {
    'JL': 'JALAN', 'JLN': 'JALAN', 'DSN': 'DUSUN', 'KP': 'KAMPUNG',
    'KEC': 'KECAMATAN', 'KAB': 'KABUPATEN', 'NO': 'NOMOR',
    'RT': '', 'RW': '', 'BLK': 'BLOK',
    'KOMPLEK': 'KOMPLEKS', 'WARUNG': 'TOKO', 'WR': 'TOKO',
    'UD': '', 'CV': '', 'PT': '', 'TB': 'TOKO'
}


def clean_text(text):
    if pd.isna(text): return ""
    text = str(text).upper()
    text = re.sub(r'[^\w\s]', ' ', text)
    words = text.split()
    fixed_words = [KAMUS_TYPO.get(w, w) for w in words]
    text = " ".join(fixed_words)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def process_duplication(uploaded_file):
    """
    Memproses file Excel untuk cek duplikasi.
    Returns: BytesIO object (file Excel hasil)
    """
    # Reset pointer file ke awal agar aman
    uploaded_file.seek(0)

    # 1. BACA DATA
    df = pd.read_excel(uploaded_file, header=HEADER_ROW_PANDAS)

    # --- [LOGIKA SKOR MASTER] ---
    df_score = df.copy()

    # Langkah A: Normalisasi Nilai Kosong
    df_score = df_score.replace(0, np.nan)
    df_score = df_score.replace(r'^[\s\-\.]*$', np.nan, regex=True)

    # Langkah B: Hitung Jumlah Kolom Terisi
    cols_to_score = [c for c in df_score.columns if c != 'idsbr']
    df['column_count_score'] = df_score[cols_to_score].notna().sum(axis=1)

    # Langkah C: Hitung Total Panjang Karakter
    df['char_length_score'] = df_score[cols_to_score].fillna('').astype(str).apply(
        lambda x: x.str.len().sum(), axis=1)

    # --- 2. PEMBERSIHAN DATA ---
    # Pastikan kolom ada sebelum apply
    if 'nama_usaha' not in df.columns or 'alamat' not in df.columns:
        raise ValueError("File harus memiliki kolom 'nama_usaha' dan 'alamat'")

    df['nama_clean'] = df['nama_usaha'].apply(clean_text)
    df['alamat_clean'] = df['alamat'].apply(clean_text)
    df['sort_key'] = df['nama_clean'] + " " + df['alamat_clean']

    # --- 3. LOGIKA FUZZY 98% (STRICT) ---
    df = df.sort_values(by=['sort_key', 'idsbr'])

    df['group_id'] = -1
    records = df.to_dict('records')

    current_group = 0
    prev_nama = ""
    prev_alamat = ""
    grouped_records = []

    for i, row in enumerate(records):
        curr_nama = row['nama_clean']
        curr_alamat = row['alamat_clean']

        if i == 0:
            row['group_id'] = current_group
            prev_nama = curr_nama
            prev_alamat = curr_alamat
        else:
            # Cek Nama
            if prev_nama == "" or curr_nama == "":
                ratio_nama = 0
            elif prev_nama == curr_nama:
                ratio_nama = 1.0
            else:
                ratio_nama = SequenceMatcher(None, prev_nama, curr_nama).ratio()

            # Cek Alamat
            if prev_alamat == "" or curr_alamat == "":
                ratio_alamat = 0
            elif prev_alamat == curr_alamat:
                ratio_alamat = 1.0
            else:
                ratio_alamat = SequenceMatcher(None, prev_alamat, curr_alamat).ratio()

            # SYARAT DUPLIKAT
            if ratio_nama >= THRESHOLD and ratio_alamat >= THRESHOLD:
                row['group_id'] = current_group
            else:
                current_group += 1
                row['group_id'] = current_group
                prev_nama = curr_nama
                prev_alamat = curr_alamat

        grouped_records.append(row)

    df_processed = pd.DataFrame(grouped_records)

    # --- 4. PENENTUAN MASTER ---
    df_processed = df_processed.sort_values(
        by=['group_id', 'column_count_score', 'char_length_score', 'idsbr'],
        ascending=[True, False, False, False]
    )

    df_processed['master_id_final'] = df_processed.groupby('group_id')['idsbr'].transform('first')

    def get_final_status(row):
        if not row['nama_clean']: return None, None
        if row['idsbr'] == row['master_id_final']:
            return 1, None
        else:
            return 9, row['master_id_final']

    results = df_processed.apply(get_final_status, axis=1, result_type='expand')
    df_processed['final_status'] = results[0]
    df_processed['final_master_id'] = results[1]

    # --- 5. TULIS KE EXCEL (OpenPyXL) ---
    data_map = {}
    for _, row in df_processed.iterrows():
        str_id = str(row['idsbr']).strip()
        data_map[str_id] = {'status': row['final_status'], 'master': row['final_master_id']}

    # Load ulang file asli untuk menjaga format/style
    uploaded_file.seek(0)
    book = load_workbook(uploaded_file)
    sheet = book.active

    for row in sheet.iter_rows(min_row=DATA_START_ROW_EXCEL, max_col=COL_INDEX_MASTER_ID):
        # Hati-hati dengan index 0-based vs 1-based
        cell_id = row[COL_INDEX_IDSBR - 1]
        val_id = str(cell_id.value).strip() if cell_id.value is not None else ""

        if val_id in data_map:
            vals = data_map[val_id]
            if vals['status'] is not None:
                row[COL_INDEX_STATUS - 1].value = vals['status']
                val_master = vals['master']
                if pd.isna(val_master): val_master = None
                row[COL_INDEX_MASTER_ID - 1].value = val_master

    output = io.BytesIO()
    book.save(output)
    output.seek(0)

    return output