import streamlit as st
import pandas as pd
import os
# =========================
# TẢI DỮ LIỆU
# =========================
df = pd.read_csv("BMW sales data (2010-2024).csv")

usd_to_vnd = 24000

# Việt hóa Region
region_map = {
    "Asia": "Châu Á",
    "Europe": "Châu Âu",
    "North America": "Bắc Mỹ",
    "South America": "Nam Mỹ",
    "Africa": "Châu Phi",
}

df["Region_VI"] = df["Region"].map(region_map)

# =========================
# PHÂN NHÓM DÒNG BMW
# =========================
def categorize_brand(model):
    m = str(model).lower().strip()
    if m.startswith("m"):
        return "BMW M"
    if m.startswith("i"):
        return "BMW i"
    return "BMW"


# =========================
# LẤY SERIES (3/4/5/7/X/Z, i3/i4..., M3/M4…)
# =========================
def extract_series(model):
    m = str(model).lower().strip()

    # BMW i
    if m.startswith("i"):
        return m[1:].upper()  # i4 → 4, i8 → 8

    # BMW M
    if m.startswith("m"):
        return m[1:].upper()  # M3 → 3, M5 → 5

    # BMW thường (3 Series, 5 Series…)
    if "series" in m:
        num = m.split("series")[0].strip()
        return num

    # X3, X5, Z4
    if m[0] in ["x", "z"]:
        return m[0].upper()

    return None


df["Brand_Type"] = df["Model"].apply(categorize_brand)
df["Series"] = df["Model"].apply(extract_series)


# =========================
# GIAO DIỆN TRANG WEB
# =========================
st.set_page_config(page_title="BMW Catalog", layout="wide")

st.markdown(
    """
    <h1 style="text-align:center; font-size:42px; font-family:Georgia;">
        CHỌN DÒNG XE
    </h1>
    """,
    unsafe_allow_html=True
)


# =========================
# BỘ LỌC (Region - Year)
# =========================
col1, col2 = st.columns([1, 1])

with col1:
    region = st.selectbox(
        "Region",
        df["Region_VI"].unique(),
        index=list(df["Region"].unique()).index("Asia")  # mặc định Châu Á
    )

with col2:
    year = st.selectbox(
        "Year",
        sorted(df["Year"].unique()),
        index=sorted(df["Year"].unique()).index(2016)  # mặc định 2016
    )


# =========================
# CHỌN BRAND: BMW / BMW M / BMW i
# =========================
st.write("")
colA, colB, colC = st.columns([1, 1, 1])

btn_bmw = colA.button("BMW")
btn_m = colB.button("BMW M")
btn_i = colC.button("BMW i")

# Mặc định trang Home → BMW
if btn_m:
    selected_brand = "BMW M"
elif btn_i:
    selected_brand = "BMW i"
else:
    selected_brand = "BMW"


# =========================
# CHỌN SERIES
# =========================
series_bmw = ["3", "4", "5", "7", "X", "Z"]
series_selected = "3"  # mặc định Series 3

if selected_brand == "BMW":
    col_s = st.columns(len(series_bmw))

    for idx, s in enumerate(series_bmw):
        if col_s[idx].button(s):
            series_selected = s
else:
    # BMW M hoặc BMW i → không chọn series, chỉ lọc theo brand
    series_selected = None


# =========================
# LỌC DỮ LIỆU HIỂN THỊ
# =========================
filtered = df[
    (df["Region_VI"] == region) &
    (df["Year"] == year) &
    (df["Brand_Type"] == selected_brand)
]

if selected_brand == "BMW":
    filtered = filtered[filtered["Series"] == series_selected]


# =========================
# HIỂN THỊ CARD XE
# =========================
st.write("")
st.write("")

if filtered.empty:
    st.warning("⚠ Không tìm thấy xe phù hợp với bộ lọc.")
else:
    cols = st.columns(3)

    for i, (_, row) in enumerate(filtered.iterrows()):
        with cols[i % 3]:

            # ---- Xác định tên file ảnh ----
            model = row["Model"].lower().replace(" ", "")
            color = row["Color"].lower()

            # BMW Series (3,4,5,7)
            if model.endswith("series"):
                prefix = row["Series"]  # vd: 3, 5, 7
                img_name = f"{prefix}_series_{color}"

            # BMW X (X3, X5...)
            elif model.startswith("x"):
                img_name = f"{model}_{color}"

            # BMW i (i3, i4...)
            elif model.startswith("i"):
                img_name = f"{model}_{color}"

            # BMW M (M3, M4...)
            elif model.startswith("m"):
                img_name = f"{model}_{color}"

            # fallback (nếu dữ liệu lạ)
            else:
                img_name = f"{model}_{color}"

            img_jpg = f"image/{img_name}.jpg"
            img_png = f"image/{img_name}.png"

            if os.path.exists(img_jpg):
                img_path = img_jpg
            elif os.path.exists(img_png):
                img_path = img_png
            else:
                img_path = "image/default_car.png"

            # ---- HIỂN THỊ ẢNH ----
            st.image(img_path, use_container_width=True)

            # ---- INFO XE ----
            st.markdown(
                f"""
                <h4 style="margin-top:10px;">BMW {row['Model']}</h4>
                <p style="margin-top:-10px;">Nhiên liệu: {row['Fuel_Type']}</p>
                <p>
                    <b>Giá:</b> {row['Price_USD']:,.0f} USD  
                    <br>≈ {row['Price_USD'] * usd_to_vnd:,.0f} VND
                </p>
                """,
                unsafe_allow_html=True
            )


st.markdown("""
<style>
.navbar {
    position: fixed;
    top: 0;
    width: 100%;
    background-color: white !important;
    padding: 10px 20px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    z-index: 9999;
    display: flex;
    gap: 25px;
    border-bottom: 2px solid #eaeaea;
}

.nav-item {
    font-size: 18px;
    font-weight: 600;
    text-decoration: none;
    color: black !important;
    cursor: pointer;
}

.nav-item:hover {
    color: #007bff !important;
}

/* đẩy nội dung xuống */
.stApp > header {
    margin-top: 80px !important;
}

.block-container {
    padding-top: 100px !important;
}
</style>
""", unsafe_allow_html=True)


# ===== HTML NAVBAR =====
query_params = st.query_params

if "pages" in query_params:
    page = query_params["pages"]

    if page == "du_doan_gia_xe":
        st.switch_page("pages/du_doan_gia_xe.py")

st.markdown("""
<style>
.navbar {
    position: fixed;
    top: 0;
    width: 100%;
    background-color: white !important;
    padding: 12px 24px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    z-index: 9999;
    display: flex;
    gap: 30px;
}
.nav-item {
    font-size: 18px;
    font-weight: 600;
    text-decoration: none;
    color: black !important;
}
.nav-item:hover { color: #007bff !important; }
.stApp > header { margin-top: 80px !important; }
.block-container { padding-top: 100px !important; }
</style>
""", unsafe_allow_html=True)

# ===== READ QUERY PARAM =====
params = st.query_params
page = params.get("pages", "home")

# ===== ROUTING =====
if page == "du_doan_gia_xe":
    st.switch_page("pages/du_doan_gia_xe.py")
elif page == "bieu_do":
    st.switch_page("pages/bieu_do.py")  # nếu có
elif page == "goi_y_xe":
    st.switch_page("pages/goi_y_xe.py")  # nếu có

# ===== NAVBAR HTML =====
st.markdown("""
<div class="navbar">
    <a class="nav-item" href="?pages=home">Home</a>
    <a class="nav-item" href="?pages=du_doan_gia_xe">Dự đoán giá xe</a>
</div>
""", unsafe_allow_html=True)





