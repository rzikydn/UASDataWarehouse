import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
from supabase import create_client
import time
import math

# ⚠️ Ganti dengan secret key yang BARU setelah kamu reset di Supabase
SUPABASE_URL = "https://qzcyykzcqtwplswhjcsd.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_SECRET_KEY_HERE"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---- Load & Prepare Data ----
print("📂 Loading CSV...")
df = pd.read_csv('olist_master_order_items_clean.csv')

# Pastikan kolom timestamp sebagai string
timestamp_cols = ['shipping_limit_date', 'order_purchase_timestamp',
                  'order_approved_at', 'order_delivered_carrier_date',
                  'order_delivered_customer_date', 'order_estimated_delivery_date',
                  'purchase_date']
for col in timestamp_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).replace('nan', None).replace('None', None)

# ---- Kolom yang seharusnya INTEGER di Supabase (bigint/int) ----
# Pandas membacanya sebagai float64 karena ada NaN
int_columns = [
    'order_item_id', 'price_outlier_iqr', 'freight_value_outlier_iqr',
    'purchase_year', 'purchase_month', 'purchase_quarter', 'purchase_hour',
    'is_delivered', 'missing_approved_at', 'missing_carrier_date',
    'missing_customer_delivery_date', 'has_product_category',
    'seller_zip_code_prefix', 'customer_zip_code_prefix',
    'product_name_length', 'product_description_length',
    'product_photos_qty', 'product_weight_g', 'product_length_cm',
    'product_height_cm', 'product_width_cm', 'product_volume_cm3',
    'payment_count', 'max_payment_installments', 'unique_payment_types',
    'review_count', 'avg_review_score', 'min_review_score',
    'max_review_score', 'has_review_comment', 'is_late_delivery'
]

# Konversi kolom integer: NaN -> None, float -> int
for col in int_columns:
    if col in df.columns:
        df[col] = df[col].apply(lambda x: None if pd.isna(x) else int(x))

# Konversi semua NaN/inf ke None (JSON compliant)
df = df.replace([np.nan, np.inf, -np.inf], None)

print(f"✅ Data loaded: {len(df)} rows, {len(df.columns)} columns")


# ---- Clean record untuk JSON ----
def clean_record(record):
    """Pastikan setiap value JSON-compatible"""
    cleaned = {}
    for k, v in record.items():
        if v is None:
            cleaned[k] = None
        elif isinstance(v, float):
            if math.isnan(v) or math.isinf(v):
                cleaned[k] = None
            else:
                # Cek apakah float sebenarnya integer (misal 2.0 -> 2)
                if v == int(v) and k in int_columns:
                    cleaned[k] = int(v)
                else:
                    cleaned[k] = v
        elif isinstance(v, (np.integer,)):
            cleaned[k] = int(v)
        elif isinstance(v, (np.floating,)):
            if np.isnan(v) or np.isinf(v):
                cleaned[k] = None
            else:
                cleaned[k] = float(v)
        elif isinstance(v, str) and v in ('nan', 'None', 'NaT', 'nat'):
            cleaned[k] = None
        else:
            cleaned[k] = v
    return cleaned


# ---- Upload per Batch ----
records = df.to_dict(orient='records')
BATCH_SIZE = 500
total = len(records)
success = 0

print(f"\n🚀 Mulai upload ke Supabase...")
print(f"Total: {total} rows | Batch size: {BATCH_SIZE}\n")

for i in range(0, total, BATCH_SIZE):
    batch = records[i:i+BATCH_SIZE]
    try:
        batch = [clean_record(r) for r in batch]
        supabase.table("UasDataWarehous").upsert(batch).execute()
        success += len(batch)
        pct = round((success / total) * 100, 1)
        print(f"✅ {success}/{total} rows ({pct}%)")
    except Exception as e:
        print(f"❌ Error di batch {i}-{i+BATCH_SIZE}: {e}")
        print("⏸️  Upload dihentikan. Cek error di atas.")
        break
    time.sleep(0.3)

print(f"\n{'🎉 Upload selesai!' if success == total else '⚠️ Upload tidak lengkap'}")
print(f"Total uploaded: {success}/{total} rows")