import pandas as pd

#Đọc dữ liệu
df = pd.read_csv("D:/Hoc_Ki_Cuoi/CDPTDL2/Do_An/Doanh_thu_BMV_2010-2024(BMW Worldwide Sales Records (2010–2024))/BMW sales data (2010-2024).csv")

#Làm sạch và kiểm tra data 
#print(df.head()) 
#print(df.info())
#print(df.describe()) 
#print(df.isnull().sum())

#Target dự đoán
target = "Sales_Volume"

# Tạo X và y
X = df.drop(columns=[target])
y = df[target]

category_cols = ["Model", "Region", "Color", "Fuel_Type", "Transmission", "Sales_Classification"]

#Chuyển dạng category
for col in category_cols:
    X[col] = X[col].astype("category")

from sklearn.model_selection import train_test_split
#Train/Test 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from lightgbm import LGBMRegressor
#Model LightGBM(Dự đoán doanh số theo category_cols)
model = LGBMRegressor(n_estimators=600,learning_rate=0.05, random_state=42)

#Train
model.fit(X_train, y_train, categorical_feature=category_cols)

from sklearn.metrics import mean_absolute_error, r2_score
#Dự đoán
y_pred = model.predict(X_test)

#Đánh giá
print("MAE:", mean_absolute_error(y_test, y_pred))
print("R2 :", r2_score(y_test, y_pred))#càng gần 1 càng tốt
#-------------------------------------------------
#Save Model
import pickle
with open ("model_lgb.txt", "wb") as f:
    pickle.dump(model, f)
print("*"*50)
#--------------------------------------------------
from prophet import Prophet
#Tổng hợp
ts = df.groupby("Year")["Sales_Volume"].sum().reset_index()

#Đặt tên cột Prophet
ts.columns = ["ds", "y"]

#Chuyển Year thành dạng datetime 
ts["ds"] = pd.to_datetime(ts["ds"], format="%Y")

#Model Prophet(#Dự đoán theo thời gian)
model = Prophet()

#Train model
model.fit(ts)

#Dự đoán 12 năm tiếp theo
future = model.make_future_dataframe(periods=12, freq="Y")
forecast = model.predict(future)

#Kết quả dự đoán
result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(12)
result.columns = ["Ngay", "Du_bao", "Bien_duoi", "Bien_tren"]
print(result)
#-------------------------------------------------
#Save model
import joblib
joblib.dump(model, "model_prophet.pkl")

