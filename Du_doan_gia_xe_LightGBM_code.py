import joblib
import pandas as pd
import numpy as np

from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from lightgbm import LGBMRegressor
from sklearn.preprocessing import LabelEncoder


# ============================================================
# 1. Load data
# ============================================================
df = pd.read_csv("BMW sales data (2010-2024).csv")

# ============================================================
# 2. Load Prophet model đã train
# ============================================================
model = joblib.load("du_doan_gia_xe_theo_nam_prophet.pkl")


# ============================================================
# 3. Hàm dự đoán giá theo năm
# ============================================================
def predict_price_year(year):
    df_pred = pd.DataFrame({
        "ds": [pd.to_datetime(str(year))]
    })

    forecast = model.predict(df_pred)
    return float(forecast["yhat"].values[0])


# DEMO
year = 2030
price = predict_price_year(year)
print(f"Predicted BMW average price in {year}: {price:,.2f} USD")


# ============================================================
# 4. PROPHET BACKTEST (2010–2020 train, 2021–2024 test)
# ============================================================
print("\n====================== PROPHET BACKTEST ======================")

# Tạo yearly price
df_yearly = df.groupby("Year")["Price_USD"].mean().reset_index()
df_yearly["ds"] = pd.to_datetime(df_yearly["Year"], format="%Y")
df_yearly["y"] = df_yearly["Price_USD"]

# Train: 2010–2020
df_train = df_yearly[df_yearly["ds"].dt.year <= 2020]
df_test  = df_yearly[df_yearly["ds"].dt.year > 2020]

model_bt = Prophet()
model_bt.fit(df_train[["ds", "y"]])

# Dự đoán số năm test
future_bt = model_bt.make_future_dataframe(periods=len(df_test), freq="Y")
forecast_bt = model_bt.predict(future_bt)

# Lấy dự đoán tương ứng test years
pred_bt = forecast_bt.tail(len(df_test))["yhat"].values
true_bt = df_test["y"].values

mae_bt = mean_absolute_error(true_bt, pred_bt)
rmse_bt = np.sqrt(mean_squared_error(true_bt, pred_bt))

print(f"Backtest MAE  = {mae_bt:,.2f}")
print(f"Backtest RMSE = {rmse_bt:,.2f}")


# ============================================================
# 5. LIGHTGBM LEAKAGE TESTS
# ============================================================
print("\n====================== LIGHTGBM LEAKAGE TESTS ======================")

# Encode categorical
df2 = df.copy()
cat_cols = df2.select_dtypes(include=["object"]).columns

encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    df2[col] = le.fit_transform(df2[col])
    encoders[col] = le

# Feature & target
X = df2.drop("Price_USD", axis=1)
y = df2["Price_USD"]


# ------------------------------------------------------------
# TEST 1 – REMOVE LEAK FEATURES
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# TEST 2 – SHUFFLE PRICE TEST
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# TEST 3 – REGION MEAN PRICE CLEANED
# ------------------------------------------------------------
df_no_region_leak = df2.copy()
df_no_region_leak["Region_MeanPrice"] = (
    df2.groupby("Region")["Price_USD"].transform("mean")
    - df2["Price_USD"] * 0.000001
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

# ============================================================
# 6. TRAIN LIGHTGBM FINAL MODEL (NO LEAK)
# ============================================================

X_final = X_clean      # dùng X không leak
y_final = y

X_train_f, X_test_f, y_train_f, y_test_f = train_test_split(
    X_final, y_final, test_size=0.2, random_state=42
)

lgbm_model = LGBMRegressor(
    objective="regression",
    boosting_type="gbdt",
    n_estimators=1200,
    learning_rate=0.03,
    max_depth=-1,
    subsample=0.9,
    colsample_bytree=0.9,
    reg_lambda=1.0
)

lgbm_model.fit(X_train_f, y_train_f)

pred_f = lgbm_model.predict(X_test_f)

print("\n===== FINAL LIGHTGBM MODEL =====")
print(f"MAE  = {mean_absolute_error(y_test_f, pred_f):,.2f}")
print(f"RMSE = {np.sqrt(mean_squared_error(y_test_f, pred_f)):,.2f}")

# ============================================================
# 7. SAVE LIGHTGBM MODEL
# ============================================================
joblib.dump(lgbm_model, "du_doan_gia_xe_LightGBM.pkl")
print("\nĐã tải file mô hình")

joblib.dump(encoders, "encoders.pkl")


