import pandas as pd
import re


def get_bentuk_badan_hukum_patterns() -> dict:
    return {
        1: r'(?i)\b(PT\.?|P\.T\.?|PERSEROAN|PERSERO)\b',
        2: r'(?i)\b(YAYASAN|YYS\.?)\b',
        3: r'(?i)\b(KOPERASI|KOP\.?|KOPKAR|KSU|KSP|KOPWAN|KOPDIT|KOSPIN|KUD)\b',
        4: r'(?i)\b(DANA\s*PENSIUN|DAPEN|DP\.?)\b',
        5: r'(?i)\b(PERUM|PERUMDA|PERUMNAS)\b',
        6: r'(?i)\b(BUMDES|BUM\s*DESA|BUMN?\s*DES)\b',
        7: r'(?i)\b(CV\.?|C\.V\.?)\b',
        8: r'(?i)\b(FIRMA|FA\.?)\b',
        9: r'(?i)\b(PERSEKUTUAN|MAATSCHAP|SEKUTU)\b',
        10: r'(?i)\b(PERWAKILAN|REPRESENTATIVE\s*OFFICE|REP\.?\s*OFFICE)\b',
        11: r'(?i)\b(LLC|LTD\.?|LIMITED|INC\.?|INCORPORATED|CORP\.?|CORPORATION|PTE\.?\s*LTD\.?|SDN\.?\s*BHD\.?|GMBH|AG\b|S\.?A\.?\b|BV\.?|NV\.?)\b',
        12: r'(?i)\b(UD\.?|U\.D\.?|PD\.?|P\.D\.?|TOKO|WARUNG|KIOS|KEDAI|DEPOT|SALON|BENGKEL|LAUNDRY|FOTOCOPY|FOTO\s*COPY|PERCETAKAN|SABLON|KONTER|COUNTER|RENTAL|SEWA|JAHIT|TAILOR|CATERING|KATERING)\b',
    }


def get_kode_names() -> dict:
    return {
        1: 'Perseroan (PT)', 2: 'Yayasan', 3: 'Koperasi', 4: 'Dana Pensiun',
        5: 'Perum/Perumda', 6: 'BUM Desa', 7: 'CV', 8: 'Firma',
        9: 'Persekutuan Perdata', 10: 'Kantor Perwakilan LN', 11: 'Badan Usaha LN',
        12: 'Usaha Perseorangan', 99: 'Lainnya'
    }


def classify_bentuk_badan_hukum(df: pd.DataFrame, nama_col: str = 'nama_usaha') -> pd.DataFrame:
    df = df.copy()
    patterns = get_bentuk_badan_hukum_patterns()
    if 'bentuk_badan_hukum_usaha' not in df.columns: df['bentuk_badan_hukum_usaha'] = None

    def classify_single(nama):
        if pd.isna(nama) or str(nama).strip() == '': return None
        nama_str = str(nama).upper()
        for kode, pattern in patterns.items():
            if re.search(pattern, nama_str): return kode
        return None

    df['bentuk_badan_hukum_usaha'] = df[nama_col].apply(classify_single)
    return df


def detect_and_fill_jaringan_usaha(df: pd.DataFrame, nama_col: str = 'nama_usaha') -> pd.DataFrame:
    """Deteksi format <XXXX> dan isi bentuk_badan_hukum_usaha=12 dan jaringan_usaha=1."""
    df = df.copy()
    if 'bentuk_badan_hukum_usaha' not in df.columns: df['bentuk_badan_hukum_usaha'] = None
    if 'jaringan_usaha' not in df.columns: df['jaringan_usaha'] = None
    if nama_col not in df.columns: return df

    pattern = r'<[^>]+>'

    def has_jaringan_format(nama):
        if pd.isna(nama) or str(nama) in ['', 'nan']: return False
        return bool(re.search(pattern, str(nama).strip()))

    mask_jaringan = df[nama_col].apply(has_jaringan_format)
    df.loc[mask_jaringan, 'bentuk_badan_hukum_usaha'] = 12
    df.loc[mask_jaringan, 'jaringan_usaha'] = 1
    return df