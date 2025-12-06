"""
Streamlit App - All in One Tool
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import warnings
from streamlit_option_menu import option_menu

# Import modul lokal
from src import utils, processing, classification, duplication, merger

warnings.filterwarnings('ignore')

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Data Tools",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    # --- SIDEBAR NAVIGATION (MODIFIED) ---
    with st.sidebar:
        # Opsional: Tambahkan Logo jika punya
        # st.image("assets/logo.png", use_column_width=True)

        st.title("🗂️ Data Tools")

        selected_menu = option_menu(
            menu_title="Menu Utama",  # Judul menu (bisa dikosongkan None)
            options=["EDA Usaha", "Cek Duplikasi Excel", "Gabung Excel"],
            icons=["bar-chart-fill", "search", "layers-fill"],  # Icon Bootstrap
            menu_icon="cast",  # Icon judul menu
            default_index=0,  # Menu yang aktif saat pertama buka
            styles={
                "container": {"padding": "5!important", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "18px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#02ab21"},  # Warna hijau biar fresh
            }
        )

        st.divider()

        if selected_menu == "EDA Usaha":
            st.info("Mode: Exploratory Data Analysis & Cleaning Standar.")
        elif selected_menu == "Cek Duplikasi Excel":
            st.info("Mode: Deteksi duplikasi Fuzzy Logic untuk data UMKM.")
        elif selected_menu == "Gabung Excel":
            st.info("Mode: Menggabungkan banyak file Excel menjadi satu master.")

    # =========================================================================
    # FITUR 1: EDA USAHA (Code lama kita taruh di sini)
    # =========================================================================
    if selected_menu == "EDA Usaha":
        st.title("📊 EDA Usaha")
        st.markdown("Aplikasi untuk melakukan Exploratory Data Analysis dan Cleaning")

        # --- SIDEBAR KHUSUS EDA ---
        with st.sidebar:
            st.divider()
            st.header("⚙️ Pengaturan EDA")
            usaha_file = st.file_uploader("Data Usaha (CSV/Excel)", type=['csv', 'xlsx', 'xls'])
            wilayah_file = st.file_uploader("Data Wilayah (Excel) - Opsional", type=['xlsx', 'xls'])

            skip_rows = st.number_input("Skip Rows", min_value=0, value=1, step=1)

            st.write("Kode Kabupaten = Kota:")
            kota_codes_input = st.text_input("Kode Kota (pisahkan koma)", value="71")
            kota_codes = [k.strip() for k in kota_codes_input.split(',') if k.strip()]

            output_filename = st.text_input("Nama Output EDA", value="hasil_eda")

        # --- LOGIC EDA ---
        if usaha_file is not None:
            # (... Logic EDA yang sama seperti sebelumnya ...)
            # Saya ringkas agar tidak terlalu panjang, tapi ini isinya logic 'tab' kemarin
            with st.spinner("Loading data usaha..."):
                df = utils.load_data(usaha_file, skiprows=skip_rows)

            cols_to_string = ['nomor_telepon', 'nomor_whatsapp', 'idsbr', 'kodepos']

            for col in cols_to_string:
                if col in df.columns:
                    df[col] = df[col].astype(str).replace('nan', '')

            st.success(f"✅ Data loaded: {df.shape[0]:,} rows")

            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 Data Preview", "🔧 Processing", "📊 Klasifikasi", "📈 Statistik", "💾 Download"
            ])

            with tab1:
                st.dataframe(df.head(100), use_container_width=True)

            with tab2:
                st.subheader("🔧 Proses Data")
                c1, c2 = st.columns(2)
                with c1:
                    do_clean_cols = st.checkbox("Clean Columns", True)
                    do_fmt_kode = st.checkbox("Format Wilayah", True)
                    do_clean_nama = st.checkbox("Clean Nama Usaha", True)
                with c2:
                    do_merge = st.checkbox("Merge Wilayah", value=wilayah_file is not None, disabled=wilayah_file is None)
                    do_classify = st.checkbox("Klasifikasi Badan Hukum", True)
                    do_jaringan = st.checkbox("Deteksi Jaringan", True)
                    do_wa = st.checkbox("Format WhatsApp", True)

                if st.button("🚀 Proses Data EDA"):
                    # .. Panggil fungsi processing dari src ..
                    df_proc = df.copy()
                    if do_clean_cols: df_proc, _ = processing.clean_columns(df_proc)
                    if do_fmt_kode: df_proc = processing.format_kode_wilayah(df_proc)
                    if do_clean_nama: df_proc = processing.clean_nama_usaha(df_proc)
                    if do_merge and wilayah_file:
                        df_wil = pd.read_excel(wilayah_file)
                        df_proc = processing.merge_with_wilayah(df_proc, df_wil, kota_codes)
                    if do_classify: df_proc = classification.classify_bentuk_badan_hukum(df_proc)
                    if do_jaringan: df_proc = classification.detect_and_fill_jaringan_usaha(df_proc)
                    if do_wa: df_proc = processing.fill_nomor_whatsapp(df_proc)

                    st.session_state['df_eda_result'] = df_proc
                    st.success("Selesai!")
                    st.dataframe(df_proc.head())

            # (Tab 3, 4 logic sama...)
            with tab3:
                st.subheader("📊 Hasil Klasifikasi Badan Hukum")

                # Ambil data dari session state (hasil proses) atau data mentah
                current_df = st.session_state.get('df_eda_result', df)

                if 'bentuk_badan_hukum_usaha' in current_df.columns:
                    # Hitung statistik
                    counts = current_df['bentuk_badan_hukum_usaha'].value_counts(dropna=False).reset_index()
                    counts.columns = ['Kode', 'Jumlah']

                    # Mapping Kode ke Nama (Import fungsi mapping dari classification.py)
                    kode_map = classification.get_kode_names()
                    counts['Keterangan'] = counts['Kode'].map(kode_map).fillna('Tidak Terklasifikasi')

                    # Tampilkan metrik
                    col_k1, col_k2 = st.columns([1, 2])

                    with col_k1:
                        st.write("#### Ringkasan Jumlah")
                        st.dataframe(counts[['Keterangan', 'Kode', 'Jumlah']], hide_index=True)

                    with col_k2:
                        st.write("#### Grafik Distribusi")
                        # Bar Chart Sederhana
                        st.bar_chart(counts.set_index('Keterangan')['Jumlah'])

                    st.divider()

                    # Filter Interaktif
                    st.write("#### 🔍 Lihat Detail Data")
                    selected_type = st.selectbox(
                        "Pilih Jenis Badan Hukum untuk ditampilkan:",
                        options=counts['Keterangan'].unique()
                    )

                    # Filter dataframe berdasarkan pilihan
                    selected_kode_rows = counts[counts['Keterangan'] == selected_type]['Kode'].values
                    if len(selected_kode_rows) > 0:
                        val = selected_kode_rows[0]
                        # Handle NaN (Tidak Terklasifikasi)
                        if pd.isna(val):
                            filtered_df = current_df[current_df['bentuk_badan_hukum_usaha'].isna()]
                        else:
                            filtered_df = current_df[current_df['bentuk_badan_hukum_usaha'] == val]

                        st.write(f"Menampilkan {len(filtered_df)} data untuk: **{selected_type}**")
                        st.dataframe(filtered_df[['nama_usaha', 'alamat', 'bentuk_badan_hukum_usaha']].head(50),
                                     use_container_width=True)
                else:
                    st.warning(
                        "⚠️ Kolom 'bentuk_badan_hukum_usaha' belum ditemukan. Silakan jalankan 'Proses Data' dengan mencentang opsi Klasifikasi.")

            # --- TAB 4: STATISTIK ---
            with tab4:
                st.subheader("📈 Statistik Data")
                current_df = st.session_state.get('df_eda_result', df)

                # 1. Overview Metrics
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Baris", f"{current_df.shape[0]:,}")
                m2.metric("Total Kolom", f"{current_df.shape[1]}")

                # Cek duplikasi ID
                if 'idsbr' in current_df.columns:
                    n_dupl = current_df['idsbr'].duplicated().sum()
                    m3.metric("Duplikasi ID (idsbr)", f"{n_dupl}", delta_color="inverse")
                else:
                    m3.metric("Duplikasi ID", "N/A")

                # Cek Usaha Tidak Aktif (jika ada kolom keberadaan)
                if 'keberadaan_usaha' in current_df.columns:
                    # Asumsi kode != 1 adalah tidak aktif/tutup/dll (sesuai screenshot Anda)
                    # Jika kolom object/string, sesuaikan logikanya
                    non_active = current_df[current_df['keberadaan_usaha'].astype(str) != '1'].shape[0]
                    m4.metric("Usaha Non-Aktif/Tutup", f"{non_active}")

                st.divider()

                # 2. Analisis Missing Values (Kekengkapan Data)
                st.write("#### 📉 Kelengkapan Data (Missing Values)")
                st.caption("Grafik ini menunjukkan jumlah data yang KOSONG di setiap kolom.")

                null_counts = current_df.isnull().sum().sort_values(ascending=False)
                null_counts = null_counts[null_counts > 0]  # Hanya ambil yang ada null-nya

                if not null_counts.empty:
                    st.bar_chart(null_counts)
                else:
                    st.success("Mantap! Tidak ada data kosong (Missing Values) di dataset ini.")

                # 3. Distribusi Wilayah (Top 10)
                st.divider()
                c_w1, c_w2 = st.columns(2)

                with c_w1:
                    if 'nmkab' in current_df.columns:
                        st.write("#### Top 10 Kabupaten/Kota")
                        top_kab = current_df['nmkab'].value_counts().head(10)
                        st.bar_chart(top_kab)
                    elif 'kdkab' in current_df.columns:
                        st.write("#### Top 10 Kode Kabupaten")
                        top_kab = current_df['kdkab'].value_counts().head(10)
                        st.bar_chart(top_kab)

                with c_w2:
                    if 'nmkec' in current_df.columns:
                        st.write("#### Top 10 Kecamatan")
                        top_kec = current_df['nmkec'].value_counts().head(10)
                        st.bar_chart(top_kec)
                    elif 'kdkec' in current_df.columns:
                        st.write("#### Top 10 Kode Kecamatan")
                        top_kec = current_df['kdkec'].value_counts().head(10)
                        st.bar_chart(top_kec)

            with tab5:
                if 'df_eda_result' in st.session_state:
                    df_res = st.session_state['df_eda_result']

                    st.subheader("💾 Download Hasil")
                    st.info("Download menggunakan template asli (Format terjaga).")

                    # PANGGIL FUNGSI BARU DI SINI
                    # Pastikan 'usaha_file' masih bisa diakses (variabel file uploader di atas)
                    if usaha_file:
                        try:
                            excel_bytes = utils.save_to_template_excel(
                                usaha_file,
                                df_res,
                                header_row_index=2,  # Sesuaikan dengan template Anda (Row 2)
                                data_start_row=3  # Data mulai di Row 3
                            )

                            st.download_button(
                                label="Download Excel (Template Asli)",
                                data=excel_bytes,
                                file_name=f"{output_filename}_processed.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        except Exception as e:
                            st.error(f"Gagal menulis ke template: {e}")
                            st.warning("Pastikan nama kolom di Excel tidak berubah drastis.")

                            # Fallback ke metode lama jika gagal
                            st.download_button(
                                "Download Excel (Format Standar)",
                                utils.to_excel_bytes(df_res),
                                f"{output_filename}_standard.xlsx"
                            )
        else:
            st.info("👆 Silakan upload file data usaha di sidebar sebelah kiri.")

    # =========================================================================
    # FITUR 2: CEK DUPLIKASI (Porting dari Flask)
    # =========================================================================
    elif selected_menu == "Cek Duplikasi Excel":
        st.title("👯 Cek Duplikasi UMKM")
        st.markdown("""
        Upload file Excel, sistem akan mendeteksi duplikasi berdasarkan **Nama** dan **Alamat** (Fuzzy Logic 98%).
        File output akan tetap menjaga format/warna asli file input.
        """)

        with st.sidebar:
            st.divider()
            st.header("⚙️ Input Duplikasi")
            dupl_file = st.file_uploader("Upload File (.xlsx)", type=['xlsx'])

        if dupl_file is not None:
            st.write(f"Filename: **{dupl_file.name}**")

            if st.button("🚀 Mulai Cek Duplikasi", type="primary"):
                try:
                    with st.spinner("Sedang memproses... (Ini mungkin memakan waktu untuk data besar)"):
                        # Panggil fungsi dari src/duplication.py
                        result_bytes = duplication.process_duplication(dupl_file)

                    st.success("✅ Proses Selesai!")

                    # Tombol Download
                    st.download_button(
                        label="📥 Download Hasil (.xlsx)",
                        data=result_bytes,
                        file_name=f"processed_{dupl_file.name}",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                except Exception as e:
                    st.error(f"Terjadi Kesalahan: {e}")
                    st.error("Pastikan file Excel memiliki kolom 'nama_usaha', 'alamat', dan 'idsbr' serta format template sesuai.")

        else:
            # Tampilkan instruksi jika belum upload
            st.info("Silakan upload file Excel melalui sidebar untuk memulai pengecekan duplikasi.")
            with st.expander("ℹ️ Struktur File yang Dibutuhkan"):
                st.markdown("""
                - **Format:** .xlsx
                - **Header Pandas:** Baris ke-2 (Index 1)
                - **Data Mulai:** Baris ke-3 di Excel
                - **Kolom Wajib:** `idsbr`, `nama_usaha`, `alamat`
                - **Output:** Kolom ke-13 (Status) dan ke-14 (Master ID) akan diisi otomatis.
                """)

            # =========================================================================
            # FITUR 3: GABUNG EXCEL (LOGIKA BARU)
            # =========================================================================
    elif selected_menu == "Gabung Excel":
            st.title("🔗 Gabung Multiple Excel")
            st.markdown("""
                Fitur ini menggabungkan banyak file Excel menjadi satu file.
                Sistem akan **otomatis menyambung data** ke bawah tanpa menduplikasi Header.
                Pastikan struktur kolom (nama header) antar file **sama**.
                """)

            with st.sidebar:
                st.divider()
                st.header("⚙️ Input Files")

                # accept_multiple_files=True adalah kuncinya
                uploaded_files = st.file_uploader(
                    "Upload File-file Excel (.xlsx)",
                    type=['xlsx', 'xls'],
                    accept_multiple_files=True
                )

                st.write("---")
                header_row_input = st.number_input(
                    "Posisi Header (Baris ke-)",
                    min_value=1,
                    value=2,
                    help="Jika header ada di baris pertama Excel, isi 1. Jika baris ke-5, isi 5."
                )
                # Konversi ke 0-based index untuk pandas
                header_idx = header_row_input - 1

                output_name = st.text_input("Nama File Output", "hasil_gabungan")

            if uploaded_files:
                st.info(f"📂 {len(uploaded_files)} file dipilih.")

                if st.button("🚀 Gabungkan File", type="primary"):
                    try:
                        with st.spinner("Sedang menggabungkan file..."):
                            # Panggil fungsi dari src/merger.py
                            result_bytes, total_rows = merger.process_merge_files(
                                uploaded_files,
                                header_row=header_idx
                            )

                        st.success(f"✅ Berhasil menggabungkan data! Total baris data: {total_rows:,}")

                        st.download_button(
                            label="📥 Download Hasil Gabungan",
                            data=result_bytes,
                            file_name=f"{output_name}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    except ValueError as ve:
                        st.error(f"Kesalahan Data: {ve}")
                    except Exception as e:
                        st.error(f"Terjadi kesalahan teknis: {e}")
                        st.error("Pastikan semua file memiliki ekstensi Excel yang valid dan tidak corrupt.")
            else:
                st.info("👈 Silakan upload beberapa file Excel di sidebar untuk memulai.")

if __name__ == "__main__":
    main()