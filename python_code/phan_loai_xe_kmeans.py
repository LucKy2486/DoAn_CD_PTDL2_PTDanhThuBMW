import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
import plotly.express as px
import joblib

st.set_page_config(page_title="Phân loại xe BMW – K-Means", layout="wide")

st.divider()

df = pd.read_csv("BMW sales data (2010-2024).csv")
df_cluster = df.copy()

cat_cols = ["Fuel_Type", "Region"]
encoders = {}

for col in cat_cols:
    le = LabelEncoder()
    df_cluster[col] = le.fit_transform(df_cluster[col])
    encoders[col] = le

features = ["Price_USD", "Engine_Size_L", "Fuel_Type", "Region"]
X = df_cluster[features]

st.sidebar.header("Tùy chỉnh")
k = st.sidebar.slider("Số lượng cụm (K)", min_value=2, max_value=6, value=3)

model = KMeans(n_clusters=k, random_state=42)
df_cluster["Cluster"] = model.fit_predict(X)

def describe_cluster(data):
    price_range = f"{data['Price_USD'].min():,.0f} – {data['Price_USD'].max():,.0f}"
    engine_range = f"{data['Engine_Size_L'].min()} – {data['Engine_Size_L'].max()} L"

    fuel_pop = data["Fuel_Type"].mode()[0]
    region_pop = data["Region"].mode()[0]

    return f"""
- Tầm giá: {price_range} USD  
- Động cơ: {engine_range}  
- Nhiên liệu phổ biến: {encoders['Fuel_Type'].inverse_transform([fuel_pop])[0]}  
- Thị trường: {encoders['Region'].inverse_transform([region_pop])[0]}
"""

st.subheader("Biểu đồ phân cụm (Giá – Động cơ)")

fig = px.scatter(
    df_cluster,
    x="Engine_Size_L",
    y="Price_USD",
    color="Cluster",
    hover_data=["Model", "Fuel_Type", "Region"],
    color_discrete_sequence=px.colors.qualitative.Bold,
    title="Phân nhóm xe theo Giá và Dung tích động cơ"
)

st.plotly_chart(fig, use_container_width=True)
st.divider()

st.subheader("Chi tiết từng cụm")

for c in range(k):
    st.markdown(f"## Nhóm {c}")

    sub = df_cluster[df_cluster["Cluster"] == c]

    st.info(describe_cluster(sub))

    st.markdown("Một số mẫu xe tiêu biểu")
    st.table(sub[["Model", "Year", "Price_USD", "Engine_Size_L"]].head(10))

    st.markdown("---")

st.subheader("Biểu đồ số lượng xe trong từng cụm")

cluster_count = df_cluster["Cluster"].value_counts().reset_index()
cluster_count.columns = ["Cluster", "Count"]

fig_bar = px.bar(
    cluster_count,
    x="Cluster",
    y="Count",
    text="Count",
    title="Số lượng xe trong mỗi cụm",
    color="Cluster",
    color_continuous_scale="Blues"
)

fig_bar.update_traces(textposition="outside")

st.plotly_chart(fig_bar, use_container_width=True)

#joblib.dump(model, "kmeans_model.pkl")
#print("Đã lưu model")
