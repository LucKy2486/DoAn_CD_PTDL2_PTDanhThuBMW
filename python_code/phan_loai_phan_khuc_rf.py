import streamlit as st
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Phân khúc xe BMW – Random Forest", layout="wide")

df = pd.read_csv("BMW sales data (2010-2024).csv")

st.markdown("<h2 style='text-align:center;'>PHÂN KHÚC XE BMW</h2>", unsafe_allow_html=True)
st.write("Phân khúc được tạo tự động bằng K-Means (Rẻ – Trung – Cao cấp).")

kmeans = KMeans(n_clusters=3, random_state=42)
df["cluster"] = kmeans.fit_predict(df[["Price_USD"]])

cluster_order = df.groupby("cluster")["Price_USD"].mean().sort_values().index.tolist()

mapping = {
    cluster_order[0]: "Rẻ",
    cluster_order[1]: "Trung cấp",
    cluster_order[2]: "Cao cấp"
}

df["Segment"] = df["cluster"].map(mapping)

df_clean = df.copy()
cat_cols = ["Fuel_Type", "Region", "Color", "Transmission", "Model", "Segment"]
encoders = {}

for col in cat_cols:
    le = LabelEncoder()
    df_clean[col] = le.fit_transform(df_clean[col].astype(str))
    encoders[col] = le

X = df_clean[["Engine_Size_L", "Year", "Fuel_Type", "Region", "Transmission", "Model"]]
y = df_clean["Segment"]

model = RandomForestClassifier(n_estimators=500, random_state=42)
model.fit(X, y)

importance = pd.DataFrame({
    "Feature": X.columns,
    "Importance": model.feature_importances_
}).sort_values(by="Importance", ascending=False)

st.subheader("Độ quan trọng của các yếu tố khi phân khúc xe")
fig = px.bar(
    importance,
    x="Importance",
    y="Feature",
    orientation="h",
    color="Importance",
    color_continuous_scale="Blues"
)
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Dự đoán phân khúc cho 1 chiếc xe")

engine = st.slider("Động cơ (L)", 1.0, 5.0, 2.0)
year = st.slider("Năm", 2010, 2024, 2020)
fuel = st.selectbox("Nhiên liệu", df["Fuel_Type"].unique())
region = st.selectbox("Thị trường", df["Region"].unique())
trans = st.selectbox("Hộp số", df["Transmission"].unique())
model_name = st.selectbox("Model", df["Model"].unique())

sample = pd.DataFrame([{
    "Engine_Size_L": engine,
    "Year": year,
    "Fuel_Type": encoders["Fuel_Type"].transform([fuel])[0],
    "Region": encoders["Region"].transform([region])[0],
    "Transmission": encoders["Transmission"].transform([trans])[0],
    "Model": encoders["Model"].transform([model_name])[0],
}])

pred = model.predict(sample)[0]
pred_label = encoders["Segment"].inverse_transform([pred])[0]

st.success(f"Phân khúc dự đoán: **{pred_label}**")
