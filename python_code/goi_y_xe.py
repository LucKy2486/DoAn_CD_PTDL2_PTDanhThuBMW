import streamlit as st
import pandas as pd
import numpy as np
import os
import textwrap
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import NearestNeighbors

df = pd.read_csv("BMW sales data (2010-2024).csv")

df_clean = df.copy()

cat_cols = ["Fuel_Type", "Region"]
encoders = {}

for col in cat_cols:
    le = LabelEncoder()
    df_clean[col] = le.fit_transform(df_clean[col])
    encoders[col] = le

feature_cols = ["Price_USD", "Fuel_Type", "Engine_Size_L", "Region"]
X = df_clean[feature_cols]

knn = NearestNeighbors(n_neighbors=5, metric="euclidean")
knn.fit(X)

st.set_page_config(page_title="Gợi ý xe BMW", layout="wide")

st.markdown("<h2 style='text-align:center;'>GỢI Ý XE BMW</h2>", unsafe_allow_html=True)
st.write("Chọn nhu cầu để đưa ra gợi ý:")

col1, col2 = st.columns(2)

with col1:
    budget = st.number_input("Ngân sách tối đa (USD)", min_value=20000, max_value=300000, step=5000)
    fuel = st.selectbox("Loại nhiên liệu", df["Fuel_Type"].unique())

with col2:
    engine_size_option = st.selectbox(
        "Dung tích động cơ mong muốn (L)",
        ["Không biết / Không quan trọng"] + sorted(df["Engine_Size_L"].unique())
    )
    region = st.selectbox("Khu vực thị trường", df["Region"].unique())

if engine_size_option == "Không biết / Không quan trọng":
    engine_size = float(df["Engine_Size_L"].mean())  
else:
    engine_size = float(engine_size_option)

btn = st.button("Gợi ý xe phù hợp", use_container_width=True)

if btn:

    user_input = pd.DataFrame([{
        "Price_USD": budget,
        "Fuel_Type": encoders["Fuel_Type"].transform([fuel])[0],
        "Engine_Size_L": engine_size,
        "Region": encoders["Region"].transform([region])[0]
    }])

    distances, indices = knn.kneighbors(user_input)

    max_dist = distances[0].max() if distances[0].max() != 0 else 1

    st.markdown("Các mẫu xe phù hợp nhất:")

    for dist, idx in zip(distances[0], indices[0]):

        car = df.iloc[idx]

        score = 100 * (1 - dist / max_dist)
        score = max(0, min(100, score))

        model_name = str(car['Model']).lower().replace(" ", "")
        color = str(car['Color']).lower().replace(" ", "")

        img_candidates = [
            f"image/{model_name}_{color}.jpg",
            f"image/{model_name}_{color}.png",
            f"image/{model_name}.jpg",
            f"image/{model_name}.png"
        ]

        img_path = next((img for img in img_candidates if os.path.exists(img)), "image/default_car.png")

        card_cols = st.columns([1, 2])
        with card_cols[0]:
            try:
                st.image(img_path, use_container_width=True)
            except Exception:
                st.image("image/default_car.png", use_container_width=True)

        with card_cols[1]:
            html_info = (
                f"<div style='padding:12px;'>"
                f"<h3 style='margin:0 0 6px 0;'>BMW {car['Model']}</h3>"
                f"<p style='margin:4px 0;'><b>Recommendation Score:</b> "
                f"<span style='color:#007bff; font-size:20px;'><b>{score:.1f}%</b></span></p>"
                f"<p style='margin:4px 0;'><b>Giá:</b> {car['Price_USD']:,.0f} USD</p>"
                f"<p style='margin:4px 0;'><b>Nhiên liệu:</b> {car['Fuel_Type']}</p>"
                f"<p style='margin:4px 0;'><b>Động cơ:</b> {car['Engine_Size_L']}L</p>"
                f"<p style='margin:0;'><b>Thị trường:</b> {car['Region']}</p>"
                f"</div>"
            )

            st.markdown(html_info, unsafe_allow_html=True)
        st.markdown("---")
