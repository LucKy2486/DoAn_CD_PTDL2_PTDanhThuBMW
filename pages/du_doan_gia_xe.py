import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

from dotenv import load_dotenv
import google.generativeai as genai

# ============================================================
# 0. Load API KEY từ file key.env
# ============================================================
load_dotenv("key.env")
api_key = os.getenv("AI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    print("⚠️ Không tìm thấy AI_API_KEY trong file key.env")

# ============================================================
# 1. LOAD MODEL & DỮ LIỆU
# ============================================================
df = pd.read_csv("BMW sales data (2010-2024).csv")
model = joblib.load("du_doan_gia_xe_LightGBM.pkl")
encoders = joblib.load("encoders.pkl")


# ============================================================
# HÀM MÃ HÓA AN TOÀN
# ============================================================
def safe_transform(encoder, value):
    value = str(value)
    if value not in encoder.classes_:
        encoder.classes_ = np.append(encoder.classes_, value)
    return encoder.transform([value])[0]


# ============================================================
# 2. GIAO DIỆN
# ============================================================
st.set_page_config(page_title="Dự đoán giá xe BMW", layout="wide")

st.markdown(
    "<h2 style='text-align:center;'>DỰ ĐOÁN GIÁ XE BMW</h2>",
    unsafe_allow_html=True
)

list_model = sorted(df["Model"].dropna().unique())
list_region = sorted(df["Region"].dropna().unique())
list_color = sorted(df["Color"].dropna().unique())
list_fuel = sorted(df["Fuel_Type"].dropna().unique())
list_trans = sorted(df["Transmission"].dropna().unique())
list_engine = sorted(df["Engine_Size_L"].dropna().unique())

st.write("### Nhập thông tin để bắt đầu dự đoán:")

col1, col2 = st.columns(2)

with col1:
    chon_model = st.selectbox("Dòng xe", list_model)
    chon_color = st.selectbox("Màu xe", list_color)
    chon_fuel = st.selectbox("Nhiên liệu", list_fuel)

with col2:
    chon_region = st.selectbox("Thị trường", list_region)
    chon_trans = st.selectbox("Hộp số", list_trans)
    chon_engine = st.selectbox("Dung tích động cơ (L)", list_engine)

nam_du_doan = st.selectbox("Năm dự đoán", list(range(2025, 2036)))

btn = st.button("Dự đoán giá xe", use_container_width=True)


# ============================================================
# 3. DỰ ĐOÁN
# ============================================================
if btn:

    sample = pd.DataFrame([{
        "Model": chon_model,
        "Year": nam_du_doan,
        "Region": chon_region,
        "Color": chon_color,
        "Fuel_Type": chon_fuel,
        "Transmission": chon_trans,
        "Engine_Size_L": chon_engine,
        "Mileage_KM": 0,
        "Sales_Volume": 0,
        "Sales_Classification": "Unknown"
    }])

    for col in encoders:
        if col in sample.columns:
            sample[col] = sample[col].apply(lambda x: safe_transform(encoders[col], x))

    predicted_price = model.predict(sample)[0]
    vnd = predicted_price * 24000


    # ============================================================
    # 4. LOAD ẢNH THEO QUY TẮC
    # ============================================================
    model_raw = chon_model.lower().strip()
    color_clean = chon_color.lower().replace(" ", "")

    if "series" in model_raw:
        num = model_raw.replace("series", "").strip()
        model_clean = f"{num}_series"
    else:
        model_clean = model_raw.replace(" ", "")

    candidates = [
        f"image/{model_clean}_{color_clean}.jpg",
        f"image/{model_clean}_{color_clean}.png",
        f"image/{model_clean}.jpg",
        f"image/{model_clean}.png",
    ]

    img_show = next((p for p in candidates if os.path.exists(p)), "image/default_car.png")


    # ============================================================
    # 5. UI HIỂN THỊ KẾT QUẢ
    # ============================================================
    st.markdown("## KẾT QUẢ DỰ ĐOÁN")

    img_col, info_col = st.columns([1, 2])

    with img_col:
        st.image(img_show, use_container_width=True)

    with info_col:
        st.markdown(
            f"""
            <h3 style="margin-top:0;">BMW {chon_model} – Năm {nam_du_doan}</h3>
            <p style="font-size:18px;">
                <b>Giá dự đoán (USD):</b><br>  
                <span style="color:#007bff; font-size:26px;"><b>{predicted_price:,.0f} USD</b></span>
                <br><br>
                <b>Giá dự đoán (VND):</b><br>
                <span style="color:#d9534f; font-size:26px;"><b>{vnd:,.0f} VND</b></span>
            </p>
            """,
            unsafe_allow_html=True
        )

    # ============================================================
    # 6. GIẢI THÍCH GIÁ (AI)
    # ============================================================
    if not api_key:
        explanation = (
            "⚠️ Không tìm thấy API Key trong file key.env — không thể sử dụng AI.\n\n"
            "Giá xe phụ thuộc vào thị trường, động cơ, nhiên liệu và chi phí sản xuất."
        )
    else:
        prompt = f"""
        Bạn là chuyên gia phân tích thị trường xe BMW.
        Hãy giải thích vì sao mô hình dự đoán giá:

        - Model: {chon_model}
        - Năm dự đoán: {nam_du_doan}
        - Thị trường: {chon_region}
        - Màu: {chon_color}
        - Nhiên liệu: {chon_fuel}
        - Hộp số: {chon_trans}
        - Động cơ: {chon_engine}L
        - Giá dự đoán: {predicted_price:,.0f} USD

        Viết ngắn gọn, tự nhiên, có góc nhìn chuyên gia BMW.
        """

        try:
            ai_model = genai.GenerativeModel("gemini-1.5-flash")
            result = ai_model.generate_content(prompt)
            explanation = result.text
        except Exception:
            explanation = (
                "⚠️ Không kết nối được AI. Dùng giải thích mặc định:\n"
                f"Giá xe BMW {chon_model} chịu ảnh hưởng bởi thị trường, "
                f"động cơ, màu sắc, nhiên liệu và chi phí sản xuất."
            )

    st.info(explanation)
