from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from flask_session import Session
import pandas as pd
import os
import json
from io import BytesIO
import processing

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
Session(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'usaha_file' not in request.files:
        return redirect(url_for('index'))
    
    usaha_file = request.files['usaha_file']
    wilayah_file = request.files.get('wilayah_file')
    
    if usaha_file.filename == '':
        return redirect(url_for('index'))
    
    # Get configuration
    skip_rows = int(request.form.get('skip_rows', 0))
    kota_codes_input = request.form.get('kota_codes', '71')
    kota_codes = [k.strip() for k in kota_codes_input.split(',') if k.strip()]
    
    # Processing options
    do_clean_columns = 'do_clean_columns' in request.form
    do_format_kode = 'do_format_kode' in request.form
    do_clean_nama_usaha = 'do_clean_nama_usaha' in request.form
    do_fill_whatsapp = 'do_fill_whatsapp' in request.form
    do_merge_wilayah = 'do_merge_wilayah' in request.form
    do_classify = 'do_classify' in request.form
    do_detect_jaringan = 'do_detect_jaringan' in request.form
    
    try:
        # Load data
        df = processing.load_data(usaha_file, skiprows=skip_rows)
        
        # Store original columns mapping if cleaning is enabled
        original_columns_mapping = None
        
        # Process data
        if do_clean_columns:
            df, original_columns_mapping = processing.clean_columns(df)
            
        if do_format_kode:
            df = processing.format_kode_wilayah(df)
            
        if do_clean_nama_usaha:
            nama_col = 'nama_usaha' if 'nama_usaha' in df.columns else None
            if nama_col:
                df = processing.clean_nama_usaha(df, nama_col)
        
        if do_merge_wilayah and wilayah_file and wilayah_file.filename != '':
            df_wilayah = pd.read_excel(wilayah_file)
            alamat_cols = [col for col in df.columns if 'alamat' in col.lower()]
            alamat_col = alamat_cols[0] if alamat_cols else 'alamat'
            df = processing.merge_with_wilayah(df, df_wilayah, kota_codes, alamat_col)
            
        if do_classify:
            nama_col = 'nama_usaha' if 'nama_usaha' in df.columns else df.columns[1]
            df = processing.classify_bentuk_badan_hukum(df, nama_col)
            
        if do_detect_jaringan:
            nama_col = 'nama_usaha' if 'nama_usaha' in df.columns else df.columns[1]
            df = processing.detect_and_fill_jaringan_usaha(df, nama_col)
            
        if do_fill_whatsapp:
            nomor_telepon_cols = [col for col in df.columns if 'nomor_telepon' in col.lower() or 'telepon' in col.lower()]
            nomor_whatsapp_cols = [col for col in df.columns if 'nomor_whatsapp' in col.lower() or 'whatsapp' in col.lower()]
            
            nomor_telepon_col = nomor_telepon_cols[0] if nomor_telepon_cols else 'nomor_telepon'
            nomor_whatsapp_col = nomor_whatsapp_cols[0] if nomor_whatsapp_cols else 'nomor_whatsapp'
            
            df = processing.fill_nomor_whatsapp(df, nomor_telepon_col, nomor_whatsapp_col)
        
        # Store in session
        # Convert to dict for session storage (or pickle if using filesystem session)
        # Since we use filesystem session, we can store the dataframe directly (it uses pickle)
        session['df_processed'] = df
        session['original_columns_mapping'] = original_columns_mapping
        session['filename'] = os.path.splitext(usaha_file.filename)[0]
        
        return redirect(url_for('result'))
        
    except Exception as e:
        return f"Error processing file: {str(e)}"

@app.route('/result')
def result():
    if 'df_processed' not in session:
        return redirect(url_for('index'))
    
    df = session['df_processed']
    
    # Prepare preview data (first 50 rows)
    preview_html = df.head(50).to_html(classes='table table-striped table-hover', index=False)
    
    # Statistics
    stats = {
        'rows': len(df),
        'columns': len(df.columns),
        'memory': f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
    }
    
    # Classification Summary
    summary_data = []
    pie_data = {'labels': [], 'values': []}
    
    if 'bentuk_badan_hukum_usaha' in df.columns:
        kode_names = processing.get_kode_names()
        value_counts = df['bentuk_badan_hukum_usaha'].value_counts()
        
        for kode in sorted(kode_names.keys()):
            count = value_counts.get(kode, 0)
            if count > 0:
                name = kode_names[kode]
                summary_data.append({
                    'kode': kode,
                    'nama': name,
                    'jumlah': int(count),
                    'persentase': f"{count/len(df)*100:.2f}%"
                })
                pie_data['labels'].append(name)
                pie_data['values'].append(int(count))
        
        unclassified = df['bentuk_badan_hukum_usaha'].isna().sum()
        if unclassified > 0:
            summary_data.append({
                'kode': '-',
                'nama': 'Tidak Terklasifikasi',
                'jumlah': int(unclassified),
                'persentase': f"{unclassified/len(df)*100:.2f}%"
            })
            pie_data['labels'].append('Tidak Terklasifikasi')
            pie_data['values'].append(int(unclassified))
            
    # Unclassified samples
    unclassified_samples = []
    if 'bentuk_badan_hukum_usaha' in df.columns:
        nama_col = 'nama_usaha' if 'nama_usaha' in df.columns else df.columns[1]
        unclassified_samples = df[df['bentuk_badan_hukum_usaha'].isna()][nama_col].drop_duplicates().head(20).tolist()
        
    return render_template('result.html', 
                           preview_html=preview_html, 
                           stats=stats, 
                           summary_data=summary_data,
                           pie_data=pie_data,
                           unclassified_samples=unclassified_samples,
                           kode_names=processing.get_kode_names())

@app.route('/apply_pattern', methods=['POST'])
def apply_pattern():
    if 'df_processed' not in session:
        return jsonify({'success': False, 'message': 'No data in session'})
    
    import re
    
    data = request.json
    custom_kode = int(data.get('kode'))
    custom_pattern = data.get('pattern')
    
    df = session['df_processed']
    nama_col = 'nama_usaha' if 'nama_usaha' in df.columns else df.columns[1]
    
    try:
        mask_empty = df['bentuk_badan_hukum_usaha'].isna()
        
        def apply_regex(nama):
            if pd.isna(nama):
                return None
            if re.search(custom_pattern, str(nama).upper()):
                return custom_kode
            return None
        
        new_classified = df.loc[mask_empty, nama_col].apply(apply_regex)
        count_new = new_classified.notna().sum()
        
        df.loc[mask_empty, 'bentuk_badan_hukum_usaha'] = df.loc[mask_empty, 'bentuk_badan_hukum_usaha'].fillna(new_classified)
        session['df_processed'] = df
        
        return jsonify({'success': True, 'count': int(count_new)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/download/<format_type>')
def download(format_type):
    if 'df_processed' not in session:
        return redirect(url_for('index'))
    
    df = session['df_processed']
    original_columns_mapping = session.get('original_columns_mapping')
    filename = session.get('filename', 'result')
    
    # Check if restore columns is requested (passed as query param)
    restore = request.args.get('restore', 'true') == 'true'
    mapping = original_columns_mapping if restore else None
    
    if format_type == 'excel':
        output = processing.to_excel_bytes(df, mapping)
        return send_file(
            BytesIO(output),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{filename}_processed.xlsx'
        )
    elif format_type == 'csv':
        output = processing.to_csv_bytes(df, mapping)
        return send_file(
            BytesIO(output),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{filename}_processed.csv'
        )
    
    return redirect(url_for('result'))

if __name__ == '__main__':
    app.run(debug=True)
