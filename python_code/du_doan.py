import sys
import base64
import json
import joblib
import pandas as pd
import numpy as np
from catboost import CatBoostRegressor

input_b64 = sys.argv[1]
json_str = base64.b64decode(input_b64).decode("utf-8")
data = json.loads(json_str)

def safe_transform(encoder, value):
    value = str(value)
    if value in encoder.classes_:
        return encoder.transform([value])[0]
    else:
        return encoder.transform([encoder.classes_[0]])[0]

model = CatBoostRegressor()
model.load_model("model/catboost_model.cbm")
encoders = joblib.load("model/encoders.joblib")
prophet = joblib.load("model/prophet_model.pkl")

df = pd.DataFrame([data])

#Xu hướng Market_Trend
if "Year" in df.columns:
    year = int(df["Year"].iloc[0])
    trend = float(prophet.predict(pd.DataFrame({"ds":[year]}))["yhat"].iloc[0])
    df["Market_Trend"] = trend
else:
    df["Market_Trend"] = 0  

#Chuẩn hóa cột phân loại
for col in encoders:
    if col in df.columns:
        df[col] = df[col].apply(lambda x: safe_transform(encoders[col], x))

#Dự đoán
pred = float(model.predict(df)[0])

print(pred)
