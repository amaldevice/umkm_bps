import pandas as pd
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from typing import Optional, Dict


def load_data(uploaded_file, skiprows=0):
    """Load data dari uploaded file (CSV atau Excel)."""
    file_name = uploaded_file.name.lower()
    skiprows = max(0, int(skiprows)) if skiprows else 0

    if file_name.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(uploaded_file, skiprows=skiprows)
    else:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8', skiprows=skiprows)
        except UnicodeDecodeError:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='latin-1', skiprows=skiprows)
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='cp1252', skiprows=skiprows)
    return df


def organize_columns_by_category(df: pd.DataFrame) -> tuple:
    """Organisir kolom berdasarkan kategori yang ditentukan."""
    df = df.copy()

    categories = {
        'IDENTITAS USAHA/PERUSAHAAN': [
            'idsbr', 'nama_usaha', 'nama_komersial_usaha', 'alamat', 'nama_sls',
            'kodepos', 'nomor_te', 'nomor_wemail', 'website', 'latitude', 'longitude'
        ],
        'KEBERADAAN USAHA/PERUSAHAAN': [
            'keberadaan_usaha', 'keberadaan_usaha/perusahaan', 'idsbr_master',
            'kdprov_pindah', 'kdkab_pindah', 'kdkec_pindah', 'kddesa_pindah'
        ],
        'WILAYAH USAHA/PERUSAHAAN': [
            'kdprov', 'kdkab', 'kdkec', 'kddesa', 'nmprov', 'nmkab', 'nmkec', 'nmdesa'
        ],
        'KARAKTERISTIK USAHA/PERUSAHAAN': [
            'bentuk_badan_hukum_usaha', 'status_usaha', 'jenis_usaha',
            'kategori_usaha', 'skala_usaha', 'modal_usaha'
        ],
        'KEGIATAN USAHA/PERUSAHAAN': [
            'kode_kbli', 'nama_kbli', 'kegiatan_utama', 'kegiatan_tambahan'
        ],
        'LAIN LAIN': []
    }

    ordered_columns = []
    category_ranges = []

    def get_category_columns(category_name, max_cols):
        cat_cols = []
        for col in categories[category_name]:
            if col in df.columns and col not in ordered_columns and len(cat_cols) < max_cols:
                cat_cols.append(col)
        if len(cat_cols) < max_cols:
            for col in df.columns:
                if col in ordered_columns: continue
                col_lower = col.lower()
                for pattern in categories[category_name]:
                    if (pattern.lower() in col_lower or col_lower in pattern.lower()) and len(cat_cols) < max_cols:
                        cat_cols.append(col)
                        break
        return cat_cols

    # Logic pengurutan (sama seperti sebelumnya)
    segments = [
        ('IDENTITAS USAHA/PERUSAHAAN', 12),
        ('KEBERADAAN USAHA/PERUSAHAAN', 4),
        ('WILAYAH USAHA/PERUSAHAAN', 4),
        ('KARAKTERISTIK USAHA/PERUSAHAAN', 6),
        ('KEGIATAN USAHA/PERUSAHAAN', 4),
        ('LAIN LAIN', 2)
    ]

    for cat_name, max_cols in segments:
        cols = get_category_columns(cat_name, max_cols)
        if cols:
            start_idx = len(ordered_columns)
            ordered_columns.extend(cols)
            category_ranges.append((cat_name, start_idx, len(ordered_columns) - 1))

    # Sisa kolom
    remaining = [col for col in df.columns if col not in ordered_columns]
    ordered_columns.extend(remaining)

    return df[ordered_columns], ordered_columns, category_ranges


def restore_original_columns(df: pd.DataFrame, original_columns_mapping: dict) -> pd.DataFrame:
    df = df.copy()
    rename_map = {col: original_columns_mapping.get(col, col) for col in df.columns}
    return df.rename(columns=rename_map)


def to_excel_bytes(df: pd.DataFrame, original_columns_mapping: Optional[Dict[str, str]] = None) -> bytes:
    output = BytesIO()
    if original_columns_mapping:
        df = restore_original_columns(df, original_columns_mapping)

    df_ordered = df.copy()
    ordered_columns = list(df_ordered.columns)
    total_cols = len(ordered_columns)

    segments = [
        ('IDENTITAS USAHA/PERUSAHAAN', 12),
        ('KEBERADAAN USAHA/PERUSAHAAN', 4),
        ('WILAYAH USAHA/PERUSAHAAN', 4),
        ('KARAKTERISTIK USAHA/PERUSAHAAN', 6),
        ('KEGIATAN USAHA/PERUSAHAAN', 4),
        ('LAIN LAIN', 2),
    ]
    category_ranges = []
    current_idx = 0
    for cat_name, width in segments:
        if current_idx >= total_cols: break
        end_idx = min(current_idx + width - 1, total_cols - 1)
        category_ranges.append((cat_name, current_idx, end_idx))
        current_idx = end_idx + 1

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_ordered.to_excel(writer, index=False, sheet_name='Sheet1', startrow=1)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        border_style = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'),
                              bottom=Side(style='thin'))

        for cat_name, start_idx, end_idx in category_ranges:
            start_letter = get_column_letter(start_idx + 1)
            end_letter = get_column_letter(end_idx + 1)
            if start_idx < end_idx:
                worksheet.merge_cells(f'{start_letter}1:{end_letter}1')
            cell = worksheet[f'{start_letter}1']
            cell.value = cat_name
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align
            cell.border = border_style
            if start_idx == end_idx: cell.border = border_style

        # Style header kolom (row 2)
        col_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
        col_font = Font(bold=True, size=10)
        for idx, _ in enumerate(ordered_columns, 1):
            cell = worksheet[f'{get_column_letter(idx)}2']
            cell.fill = col_fill
            cell.font = col_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border_style

        worksheet.freeze_panes = 'A3'

    output.seek(0)
    return output.getvalue()


def to_csv_bytes(df: pd.DataFrame, original_columns_mapping: Optional[Dict[str, str]] = None) -> bytes:
    if original_columns_mapping:
        df = restore_original_columns(df, original_columns_mapping)
    return df.to_csv(index=False).encode('utf-8')


def save_to_template_excel(original_file, df_result, header_row_index=1, data_start_row=3):
    """
    Menyimpan data hasil processing kembali ke template Excel asli
    tanpa merusak format/style header.

    Args:
        original_file: File object dari st.file_uploader
        df_result: DataFrame hasil processing
        header_row_index: Index baris header (1-based), default 2 (Excel Row 2)
        data_start_row: Baris mulai data (1-based), default 3 (Excel Row 3)
    """
    # 1. Reset pointer file dan load workbook
    original_file.seek(0)
    wb = load_workbook(original_file)
    ws = wb.active

    # 2. Mapping Kolom DataFrame -> Kolom Excel
    # Kita perlu tahu kolom 'nama_usaha' di DF itu ada di kolom ke berapa di Excel (misal col C)

    # Ambil header dari Excel asli untuk mapping
    excel_headers = {}
    for col_idx, cell in enumerate(ws[header_row_index], 1):
        if cell.value:
            # Bersihkan newline agar cocok dengan logic cleaning kita sebelumnya
            clean_header = str(cell.value).split('\n')[0].strip()
            excel_headers[clean_header] = col_idx

    # 3. Tulis Data
    # Kita iterasi per baris di DataFrame dan tulis ke Excel
    # Menggunakan enumerate untuk tracking baris Excel

    # Konversi DF ke dictionary records agar iterasi lebih cepat
    data_records = df_result.to_dict('records')

    for i, row_data in enumerate(data_records):
        current_row = data_start_row + i

        for col_name, val in row_data.items():
            # Cek apakah kolom ini ada di Excel asli?
            if col_name in excel_headers:
                col_idx = excel_headers[col_name]

                # Handle NaN/None agar sel Excel jadi kosong
                if pd.isna(val):
                    val = None

                # Tulis nilai ke sel
                ws.cell(row=current_row, column=col_idx).value = val

    # 4. Simpan ke BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output