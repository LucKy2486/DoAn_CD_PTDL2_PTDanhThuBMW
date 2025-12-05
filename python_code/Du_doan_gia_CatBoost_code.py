import pandas as pd
import joblib
from catboost import CatBoostRegressor
from sklearn.preprocessing import LabelEncoder #Chuẩn hóa
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

df = pd.read_csv("BMW sales data (2010-2024).csv")

#Load Prophet model 
prophet = joblib.load("prophet_model.pkl")

#Kiểm tra null
#print(df.isnull().sum())
#print(df.describe())#Thống kê

years = df['Year'].unique()
market_trend_map = {
    y: float(prophet.predict(pd.DataFrame({"ds":[y]}))["yhat"].iloc[0])
    for y in years
}

df['Market_Trend'] = df['Year'].map(market_trend_map)
cat_cols = ["Model", "Region", "Color", "Fuel_Type", "Transmission", "Sales_Classification"]
encoders = {}

for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le

#Lưu encoders
joblib.dump(encoders, "encoders.joblib")
print("Encoders đã lưu")
    
X = df.drop(columns=["Price_USD"])
y = df["Price_USD"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True, random_state=42)

#Mô hình CatBoost
model = CatBoostRegressor(iterations=300, depth=8, learning_rate=0.05, loss_function='RMSE', verbose=100, thread_count=-1)
model.fit(X_train, y_train,cat_features=[X.columns.get_loc(c) for c in cat_cols])

#Dự đoán
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("*"*50)
print(f"MAE: {mae:.2f}")#Trung bình mức sai số thực tế
print(f"RMSE: {rmse:.2f}")#Trung bình sai số
print("*"*50)

model.save_model("catboost_model.cbm")
print("Model CatBoost đã lưu")







