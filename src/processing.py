import pandas as pd
import re
from typing import List


def clean_columns(df: pd.DataFrame) -> tuple:
    """Bersihkan nama kolom."""
    df = df.copy()
    original_columns = df.columns.tolist()
    cleaned_columns = df.columns.str.split('\n').str[0].tolist()
    original_columns_mapping = dict(zip(cleaned_columns, original_columns))
    df.columns = cleaned_columns
    return df, original_columns_mapping


def format_kode_wilayah(df: pd.DataFrame) -> pd.DataFrame:
    """Format kode wilayah dengan zero-padding."""
    df = df.copy()
    for col, width in [('kdprov', 2), ('kdkab', 2), ('kdkec', 3), ('kddesa', 3)]:
        if col in df.columns:
            df[col] = df[col].astype("Int64").astype(str).str.zfill(width)
    return df


def create_alamat_new(df_wilayah: pd.DataFrame, kota_codes: List[str]) -> pd.DataFrame:
    """Buat kolom alamat_new dari data wilayah (untuk lookup table)."""
    df = df_wilayah.copy()
    for col in ["nmdesa", "nmkec", "nmkab", "nmprov"]:
        if col in df.columns:
            df[col] = df[col].fillna('').astype(str).str.strip()

    def build_alamat(row):
        parts = []
        if row.get('nmdesa', '') and row['nmdesa'] not in ['', 'nan', 'None', '<NA>']:
            parts.append(f"Desa {row['nmdesa']}")
        if row.get('nmkec', '') and row['nmkec'] not in ['', 'nan', 'None', '<NA>']:
            parts.append(f"Kecamatan {row['nmkec']}")
        if row.get('nmkab', '') and row['nmkab'] not in ['', 'nan', 'None', '<NA>']:
            kdkab = str(row.get('kdkab', ''))
            prefix = "Kota" if kdkab in kota_codes else "Kabupaten"
            parts.append(f"{prefix} {row['nmkab']}")
        if row.get('nmprov', '') and row['nmprov'] not in ['', 'nan', 'None', '<NA>']:
            parts.append(f"Provinsi {row['nmprov']}")
        return ', '.join(parts) if parts else None

    df['alamat_new'] = df.apply(build_alamat, axis=1)
    return df


def create_fallback_alamat(df: pd.DataFrame, df_wilayah: pd.DataFrame, kota_codes: List[str],
                           alamat_col: str = 'alamat') -> pd.DataFrame:
    """Buat alamat fallback untuk rows yang tidak match."""
    df = df.copy()
    if alamat_col not in df.columns: df[alamat_col] = None

    mask_empty = df[alamat_col].isna()
    if mask_empty.any():
        mask_str_empty = ~df[alamat_col].isna() & (
            df[alamat_col].astype(str).str.strip().isin(['', 'nan', 'None', '<NA>']))
        mask_empty = mask_empty | mask_str_empty

    if not mask_empty.any(): return df

    # Lookup tables optimization
    lookup_kec = df_wilayah[['kdprov', 'kdkab', 'kdkec', 'nmkec', 'nmkab', 'nmprov']].drop_duplicates(
        subset=['kdprov', 'kdkab', 'kdkec'])
    lookup_kab = df_wilayah[['kdprov', 'kdkab', 'nmkab', 'nmprov']].drop_duplicates(subset=['kdprov', 'kdkab'])
    lookup_prov = df_wilayah[['kdprov', 'nmprov']].drop_duplicates(subset=['kdprov'])

    def build_fallback(row):
        parts = []
        kdprov, kdkab, kdkec = str(row.get('kdprov', '')), str(row.get('kdkab', '')), str(row.get('kdkec', ''))

        # Match Level Kecamatan
        match_kec = lookup_kec[
            (lookup_kec['kdprov'] == kdprov) & (lookup_kec['kdkab'] == kdkab) & (lookup_kec['kdkec'] == kdkec)]
        if not match_kec.empty:
            r = match_kec.iloc[0]
            if r.get('nmkec', '') not in ['', 'nan']: parts.append(f"Kecamatan {r['nmkec']}")
            if r.get('nmkab', '') not in ['', 'nan']:
                prefix = "Kota" if kdkab in kota_codes else "Kabupaten"
                parts.append(f"{prefix} {r['nmkab']}")
            if r.get('nmprov', '') not in ['', 'nan']: parts.append(f"Provinsi {r['nmprov']}")
            if parts: return ', '.join(parts)

        # Match Level Kabupaten
        match_kab = lookup_kab[(lookup_kab['kdprov'] == kdprov) & (lookup_kab['kdkab'] == kdkab)]
        if not match_kab.empty:
            r = match_kab.iloc[0]
            if r.get('nmkab', '') not in ['', 'nan']:
                prefix = "Kota" if kdkab in kota_codes else "Kabupaten"
                parts.append(f"{prefix} {r['nmkab']}")
            if r.get('nmprov', '') not in ['', 'nan']: parts.append(f"Provinsi {r['nmprov']}")
            if parts: return ', '.join(parts)

        # Fallback Kode
        codes = []
        if kdprov: codes.append(f"Prov:{kdprov}")
        if kdkab: codes.append(f"Kab:{kdkab}")
        if kdkec: codes.append(f"Kec:{kdkec}")
        if str(row.get('kddesa', '')): codes.append(f"Desa:{row['kddesa']}")
        return f"[Kode: {', '.join(codes)}]" if codes else None

    df.loc[mask_empty, alamat_col] = df.loc[mask_empty].apply(build_fallback, axis=1)
    return df


def merge_with_wilayah(df: pd.DataFrame, df_wilayah: pd.DataFrame, kota_codes: List[str],
                       alamat_col: str = 'alamat') -> pd.DataFrame:
    """Merge data usaha dengan data wilayah."""
    df = df.copy()
    if alamat_col not in df.columns: df[alamat_col] = None

    df_wilayah = format_kode_wilayah(df_wilayah)
    df_wilayah = create_alamat_new(df_wilayah, kota_codes)

    on_columns = ["kdprov", "kdkab", "kdkec", "kddesa"]
    lookup = df_wilayah[on_columns + ["alamat_new"]].drop_duplicates(subset=on_columns)

    df = df.merge(lookup, on=on_columns, how='left')

    mask_empty = df[alamat_col].isna() | (df[alamat_col].astype(str).str.strip().isin(['', 'nan', 'None', '<NA>']))
    df.loc[mask_empty & df['alamat_new'].notna(), alamat_col] = df.loc[
        mask_empty & df['alamat_new'].notna(), 'alamat_new']

    if 'alamat_new' in df.columns: df = df.drop(columns=['alamat_new'])
    df = create_fallback_alamat(df, df_wilayah, kota_codes, alamat_col)
    return df


def fill_nomor_whatsapp(df: pd.DataFrame, nomor_telepon_col: str = 'nomor_telepon',
                        nomor_whatsapp_col: str = 'nomor_whatsapp') -> pd.DataFrame:
    df = df.copy()
    if nomor_whatsapp_col not in df.columns: df[nomor_whatsapp_col] = None
    if nomor_telepon_col not in df.columns: return df

    def convert_to_whatsapp(nomor):
        if pd.isna(nomor): return None
        s = re.sub(r'\D', '', str(nomor).strip())
        if s.startswith('08'): return '+62' + s[1:]
        return None

    mask_empty = df[nomor_whatsapp_col].isna() | (
        df[nomor_whatsapp_col].astype(str).str.strip().isin(['', 'nan', 'None']))
    mask_has_tel = df[nomor_telepon_col].notna()

    mask_process = mask_empty & mask_has_tel
    if mask_process.any():
        converted = df.loc[mask_process, nomor_telepon_col].apply(convert_to_whatsapp)
        mask_valid = converted.notna()
        df.loc[mask_process & mask_valid, nomor_whatsapp_col] = converted[mask_valid]
    return df


def clean_nama_usaha(df: pd.DataFrame, nama_col: str = 'nama_usaha') -> pd.DataFrame:
    """Clean penamaan usaha, ubah kurung jadi <>, pindah PT/CV ke belakang."""
    df = df.copy()
    if nama_col not in df.columns: return df

    def clean_single(nama):
        if pd.isna(nama) or str(nama).strip() in ['', 'nan', 'None', '<NA>']: return nama
        s = str(nama).strip()

        # Cek jika sudah benar
        if re.search(r',\s*(PT|CV|UD|PD|FA|P\.T\.?|C\.V\.?|U\.D\.?|P\.D\.?|F\.A\.?)\s*$', s, re.IGNORECASE):
            s = re.sub(r'\(([^)]*)\)', r'<\1>', s)
            s = re.sub(r'\[([^\]]*)\]', r'<\1>', s)
            # Cleanup minor
            s = re.sub(r'\s+', ' ', s).strip()
            return s

        # Ubah kurung
        s = re.sub(r'\(([^)]*)\)', r'<\1>', s)
        s = re.sub(r'\[([^\]]*)\]', r'<\1>', s)
        s = re.sub(r'\{([^}]*)\}', r'<\1>', s)
        s = re.sub(r'["""]([^"""]*)["""]', r'<\1>', s)
        s = re.sub(r"['']([^'']*)['']", r'<\1>', s)

        # Pindah Badan Hukum Depan -> Belakang
        patterns = [
            (r'^PT\.?\s+', 'PT'), (r'^P\.T\.?\s+', 'PT'),
            (r'^CV\.?\s+', 'CV'), (r'^C\.V\.?\s+', 'CV'),
            (r'^UD\.?\s+', 'UD'), (r'^FA\.?\s+', 'FA'),
            (r'(?<!S\.)\bPD\.?\s+', 'PD')
        ]

        moved = False
        for pat, suff in patterns:
            if re.match(pat, s, re.IGNORECASE):
                s = re.sub(pat, '', s, flags=re.IGNORECASE).strip()
                if not re.search(r',\s*' + suff + r'\s*$', s, re.IGNORECASE):
                    s = f"{s}, {suff}"
                moved = True
                break

        # Handle suffix yg nempel titik (e.g. "Nama Usaha. PT")
        if not moved:
            suffixes = ['PT', 'CV', 'UD', 'PD', 'FA']
            for suf in suffixes:
                s = re.sub(r'\.\s*' + suf + r'\.?\s*$', f', {suf}', s, flags=re.IGNORECASE)
                s = re.sub(r'\s+' + suf + r'\.?\s*$', f', {suf}', s, flags=re.IGNORECASE)

        # Cleanup akhir
        s = re.sub(r'\s+', ' ', s).strip()
        s = re.sub(r',{2,}', ',', s)
        s = re.sub(r',\s*,', ', ', s)
        return s

    df[nama_col] = df[nama_col].apply(clean_single)
    return df