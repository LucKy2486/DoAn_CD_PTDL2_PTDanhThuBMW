import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
import numpy as np
import joblib

df = pd.read_csv("BMW sales data (2010-2024).csv")

#ktr null
#print(df.isnull().sum())
#print(df.describe())#Thống kê

#Gom giá trung bình theo năm
df_year = df.groupby("Year")["Price_USD"].mean().reset_index()
df_year.columns = ["ds", "y"]

#Prophet chỉ yêu cầu 1 DataFrame duy nhất nên ko thể dùng X_train,X_test,.....
#shuffle=False: Không trộn dữ liệu-->Giữ nguyên data
train_df, test_df = train_test_split(df_year, test_size=0.2, shuffle=False)  

#Huấn luyện Prophet 
model = Prophet(yearly_seasonality=True)
model.fit(train_df)

#Dự đoán
future_test = test_df[["ds"]].copy()
forecast = model.predict(future_test)

#Tính MAE/RMSE
y_true = test_df["y"].values
y_pred = forecast["yhat"].values

mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
print("*"*50)
print(f"MAE: {mae:.2f}")#Trung bình mức sai số thực tế
print(f"RMSE: {rmse:.2f}")#Trung bình sai số
print("*"*50)
#Lưu model Prophet
joblib.dump(model, "prophet_model.pkl")
print("Đã lưu model")

#VD: Dự đoán tương lai
future_years = pd.DataFrame({"ds": [2025, 2026]})
future_forecast = model.predict(future_years)
print(future_forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]])
