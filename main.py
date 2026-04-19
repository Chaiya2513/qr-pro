import streamlit as st
from streamlit_gsheets import GSheetsConnection
import qrcode
from PIL import Image
from io import BytesIO
from datetime import datetime
import pandas as pd

# ... (การตั้งค่า Connection เหมือนเดิม) ...

# --- ตรวจสอบตอนสแกน (Query Parameter) ---
if "id" in query_params:
    qr_id = query_params["id"]
    match = df[df['id'].astype(str) == str(qr_id)]
    
    if not match.empty:
        target_url = match.iloc[0]['target_url']
        exp_val = match.iloc[0]['expiry_date']
        
        # ตรวจสอบเงื่อนไขวันหมดอายุ
        # ถ้าค่าใน Sheet เป็นค่าว่าง หรือ None (pd.isna) ให้ผ่านได้เลย
        if pd.isna(exp_val) or exp_val == "" or exp_val == "None":
            st.success("กำลังนำทาง (QR แบบถาวร)...")
            st.markdown(f'<meta http-equiv="refresh" content="0;url={target_url}">', unsafe_allow_html=True)
            st.stop()
        else:
            expiry_date = pd.to_datetime(exp_val).date()
            if datetime.now().date() <= expiry_date:
                st.success(f"กำลังนำทาง (หมดอายุ {expiry_date})...")
                st.markdown(f'<meta http-equiv="refresh" content="0;url={target_url}">', unsafe_allow_html=True)
                st.stop()
            else:
                st.error("❌ ขออภัย QR Code นี้หมดอายุแล้ว")
                st.stop()

# --- หน้าจอหลักสำหรับสร้าง QR ---
st.title("🎨 Smart QR Code Generator")

with st.form("main_form"):
    qr_id = st.text_input("รหัส QR ID:", placeholder="เช่น PROMO-01")
    target_url = st.text_input("ลิงก์ปลายทาง (Target URL):")
    
    # เพิ่ม Checkbox สำหรับกำหนดว่าจะให้มีวันหมดอายุไหม
    use_expiry = st.checkbox("กำหนดวันหมดอายุ", value=True)
    expiry_date = st.date_input("ระบุวันหมดอายุ:", value=datetime(2026, 4, 30), disabled=not use_expiry)
    
    logo_file = st.file_uploader("โลโก้ตรงกลาง:", type=['png', 'jpg'])
    submit_button = st.form_submit_button("สร้างและบันทึก")

if submit_button:
    if qr_id and target_url:
        # เตรียมค่าที่จะบันทึก (ถ้าไม่ใช้ expiry ให้ใส่ None)
        save_expiry = expiry_date.strftime('%Y-%m-%d') if use_expiry else None
        
        # บันทึกลง Google Sheets
        new_row = pd.DataFrame([{
            "id": qr_id,
            "target_url": target_url,
            "expiry_date": save_expiry
        }])
        
        # (ส่วนของการต่อ DataFrame และ conn.update เหมือนเดิม)
        # ... 

        st.success(f"สร้าง QR Code เรียบร้อย! ประเภท: {'มีวันหมดอายุ' if use_expiry else 'ถาวร'}")
        # ... (โค้ดสร้างภาพ QR Code และปุ่ม Download เหมือนเดิม)
