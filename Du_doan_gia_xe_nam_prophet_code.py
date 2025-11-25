import pandas as pd
import numpy as np
from prophet import Prophet
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from lightgbm import LGBMRegressor
from sklearn.preprocessing import LabelEncoder

# ============================================================
# 1. LOAD DATA
# ============================================================
df = pd.read_csv("BMW sales data (2010-2024).csv")

# --------------------------
# Chuẩn bị dữ liệu Prophet
# --------------------------
df_yearly = df.groupby("Year")["Price_USD"].mean().reset_index()

# Prophet yêu cầu 2 cột: ds, y
df_yearly = df_yearly.rename(columns={
    "Year": "ds",
    "Price_USD": "y"
})

df_yearly["ds"] = pd.to_datetime(df_yearly["ds"], format="%Y")


# ============================================================
# 2. TRAIN PROPHET
# ============================================================
prophet_model = Prophet(
    yearly_seasonality=True,
    seasonality_mode="additive",
    changepoint_prior_scale=0.05
)

prophet_model.fit(df_yearly)

# ============================================================
# 3. PROPHET – DỰ ĐOÁN 12 NĂM TỚI
# ============================================================
future = prophet_model.make_future_dataframe(
    periods=12,  # dự đoán 2025–2036
    freq="Y"
)

forecast = prophet_model.predict(future)

# ============================================================
# 4. LIGHTGBM – DATA PREPROCESSING
# ============================================================

# Copy để xử lý
df2 = df.copy()

# Encode categorical
cat_cols = df2.select_dtypes(include=["object"]).columns
encoders = {}

for col in cat_cols:
    le = LabelEncoder()
    df2[col] = le.fit_transform(df2[col])
    encoders[col] = le

# Tạo X, y cho LightGBM
X = df2.drop("Price_USD", axis=1)
y = df2["Price_USD"]


# ============================================================
# 5. LEAKAGE TESTS
# ============================================================

print("\n====================== LIGHTGBM LEAKAGE TESTS ======================")

# ============================================================
# TEST 1 – REMOVE LEAK FEATURES
# ============================================================
leak_cols = ["Region_MeanPrice", "Price_Per_Liter"]

X_clean = X.drop(columns=leak_cols, errors="ignore")

X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
    X_clean, y, test_size=0.2, random_state=42
)

model_test1 = LGBMRegressor(
    boosting_type="gbdt",
    objective="regression",
    n_estimators=1000,
    learning_rate=0.05
)

model_test1.fit(X_train_c, y_train_c)
pred1 = model_test1.predict(X_test_c)

print("\n===== TEST 1 — REMOVE LEAK FEATURES =====")
print(f"Test1 MAE  = {mean_absolute_error(y_test_c, pred1):,.2f}")
print(f"Test1 RMSE = {np.sqrt(mean_squared_error(y_test_c, pred1)):,.2f}")


# ============================================================
# TEST 2 – SHUFFLE PRICE (SANITY CHECK)
# ============================================================
y_shuffled = y.sample(frac=1.0, random_state=42).reset_index(drop=True)

X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
    X, y_shuffled, test_size=0.2, random_state=42
)

model_test2 = LGBMRegressor(
    objective="regression",
    n_estimators=1000,
    learning_rate=0.05
)

model_test2.fit(X_train_s, y_train_s)
pred2 = model_test2.predict(X_test_s)

print("\n===== TEST 2 — SHUFFLE PRICE TEST =====")
print(f"Test2 MAE  = {mean_absolute_error(y_test_s, pred2):,.2f}")
print(f"Test2 RMSE = {np.sqrt(mean_squared_error(y_test_s, pred2)):,.2f}")


# ============================================================
# TEST 3 – REGION MEAN PRICE CLEANED
# ============================================================
df_no_region_leak = df2.copy()
df_no_region_leak["Region_MeanPrice"] = (
    df2.groupby("Region")["Price_USD"].transform("mean")
    - df2["Price_USD"] * 0.000001  # tránh leak trực tiếp
)

X2 = df_no_region_leak.drop("Price_USD", axis=1)

X_train2, X_test2, y_train2, y_test2 = train_test_split(
    X2, y, test_size=0.2, random_state=42
)

model_test3 = LGBMRegressor(
    objective="regression",
    n_estimators=1000,
    learning_rate=0.05
)

model_test3.fit(X_train2, y_train2)
pred3 = model_test3.predict(X_test2)

print("\n===== TEST 3 — REGION MEAN CLEANED =====")
print(f"Test3 MAE  = {mean_absolute_error(y_test2, pred3):,.2f}")
print(f"Test3 RMSE = {np.sqrt(mean_squared_error(y_test2, pred3)):,.2f}")

joblib.dump(prophet_model, "du_doan_gia_xe_theo__nam_prophet.pkl")
print("\nĐã tải mô hình")
