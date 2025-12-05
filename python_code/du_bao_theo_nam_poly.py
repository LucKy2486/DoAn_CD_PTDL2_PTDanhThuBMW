import streamlit as st
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import plotly.express as px

st.set_page_config(page_title="Dự báo giá theo năm – Polynomial Regression", layout="wide")

df = pd.read_csv("BMW sales data (2010-2024).csv")

st.markdown("<h2 style='text-align:center;'>DỰ BÁO GIÁ XE THEO NĂM</h2>", unsafe_allow_html=True)

model_selected = st.selectbox("Chọn dòng xe", df["Model"].unique())
df_model = df[df["Model"] == model_selected].sort_values("Year")

X = df_model[["Year"]]
y = df_model["Price_USD"]

poly = PolynomialFeatures(degree=3)
X_poly = poly.fit_transform(X)

model = LinearRegression()
model.fit(X_poly, y)

future_years = np.arange(2025, 2036)
future_poly = poly.transform(future_years.reshape(-1, 1))
preds = model.predict(future_poly)

pred_df = pd.DataFrame({"Year": future_years, "Predicted_Price": preds})

fig = px.line(pred_df, x="Year", y="Predicted_Price",
              title=f"Dự báo giá xe {model_selected} (2025–2035)",
              markers=True)

st.plotly_chart(fig, use_container_width=True)

joblib.dump(model, "poly_model.pkl")
print("Đã lưu model")