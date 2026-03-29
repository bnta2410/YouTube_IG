import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Instagram Engagement Analysis", layout="wide", page_icon="📸")

data_file = "instagram_prediction.csv"
if not os.path.exists(data_file):
    st.error(f"Dữ liệu không tìm thấy: {data_file}. Chạy instagram_pipeline.py trước để tạo file.")
    st.stop()

try:
    df = pd.read_csv(data_file)
except Exception as e:
    st.error(f"Lỗi khi đọc {data_file}: {e}")
    st.stop()

required_cols = ["predicted_engagement", "likes", "comments", "impressions"]
for col in required_cols:
    if col not in df.columns:
        st.error(f"Cột cần thiết bị thiếu: {col}")
        st.stop()

st.title("Instagram Engagement Prediction")
st.markdown("#### Dashboard phân tích nhanh và trực quan cho Instagram")

# Info bar
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng posts", len(df))
if "predicted_engagement" in df.columns:
    col2.metric("Tương tác trung bình", round(df["predicted_engagement"].mean(), 4))
if "impressions" in df.columns:
    col3.metric("Impressions trung bình", int(df["impressions"].mean()))
if "account_type" in df.columns:
    col4.metric("Số account types", df["account_type"].nunique())

# ===== Sidebar filter =====
st.sidebar.header("Bộ lọc dữ liệu")
search_caption = st.sidebar.text_input("Tìm theo caption (nếu có)")

selected_account_types = None
if "account_type" in df.columns:
    account_types = df["account_type"].astype(str).sort_values().unique().tolist()
    selected_account_types = st.sidebar.multiselect("Chọn loại account", account_types, default=account_types)
    df = df[df["account_type"].astype(str).isin(selected_account_types)]

selected_media_types = None
if "media_type" in df.columns:
    media_types = df["media_type"].astype(str).sort_values().unique().tolist()
    selected_media_types = st.sidebar.multiselect("Chọn loại media", media_types, default=media_types)
    df = df[df["media_type"].astype(str).isin(selected_media_types)]

selected_content_categories = None
if "content_category" in df.columns:
    content_categories = df["content_category"].astype(str).sort_values().unique().tolist()
    selected_content_categories = st.sidebar.multiselect("Chọn danh mục nội dung", content_categories, default=content_categories)
    df = df[df["content_category"].astype(str).isin(selected_content_categories)]

if search_caption and "caption_length" in df.columns:
    # Giả sử có cột caption hoặc tìm theo caption_length
    df = df[df["caption_length"] > 0]  # Placeholder filter

# Phần filter nâng cao
if "impressions" in df.columns:
    min_imp, max_imp = int(df["impressions"].min()), int(df["impressions"].max())
    impression_range = st.sidebar.slider("Impressions", min_imp, max_imp, (min_imp, max_imp))
    df = df[(df["impressions"] >= impression_range[0]) & (df["impressions"] <= impression_range[1])]

if "likes" in df.columns:
    min_likes, max_likes = int(df["likes"].min()), int(df["likes"].max())
    likes_range = st.sidebar.slider("Likes", min_likes, max_likes, (min_likes, max_likes))
    df = df[(df["likes"] >= likes_range[0]) & (df["likes"] <= likes_range[1])]

if "predicted_engagement" in df.columns:
    min_eng, max_eng = float(df["predicted_engagement"].min()), float(df["predicted_engagement"].max())
    engagement_range = st.sidebar.slider("Tương tác dự đoán", min_eng, max_eng, (min_eng, max_eng))
    df = df[(df["predicted_engagement"] >= engagement_range[0]) & (df["predicted_engagement"] <= engagement_range[1])]

st.sidebar.markdown("---")
st.sidebar.write(f"Posts hiển thị: {len(df)}")

# ===== KPI =====
st.subheader("Tổng quan")
st.write("Số lượng posts:", len(df))
if len(df) > 0:
    st.write("Tương tác trung bình:", round(df["predicted_engagement"].mean(), 4))
else:
    st.write("Không có dữ liệu sau khi lọc.")

# ===== Biểu đồ chính =====
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Phân phối Tương tác")
    fig, ax = plt.subplots()
    if "predicted_engagement" in df.columns:
        df["predicted_engagement"].hist(bins=30, ax=ax, color="#E1306C")
        ax.set_xlabel("Tương tác dự đoán")
        ax.set_ylabel("Số lượng posts")
        st.pyplot(fig)
    else:
        st.info("Không có dữ liệu Tương tác dự đoán để hiển thị histogram")

with col_b:
    st.subheader("Boxplot Tương tác")
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    if "predicted_engagement" in df.columns:
        ax2.boxplot(df["predicted_engagement"].dropna(), vert=False, patch_artist=True, boxprops=dict(facecolor="#FCAF45"))
        ax2.set_xlabel("Tương tác dự đoán")
        st.pyplot(fig2)
    else:
        st.info("Không có dữ liệu Tương tác dự đoán")

st.subheader("Trend Tương tác - Sắp xếp")
if len(df) > 0 and "predicted_engagement" in df.columns:
    df_line = df.sort_values(by="predicted_engagement")["predicted_engagement"]
    st.line_chart(df_line.reset_index(drop=True))
else:
    st.info("Không có đủ dữ liệu để biểu diễn trend")

# ===== Scatter =====
if len(df) > 0 and "impressions" in df.columns and "predicted_engagement" in df.columns:
    st.subheader("Impressions vs Tương tác")
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    ax3.scatter(df["impressions"], df["predicted_engagement"], alpha=0.6, c="#833AB4", edgecolors="w", s=40)
    ax3.set_xlabel("Impressions")
    ax3.set_ylabel("Tương tác dự đoán")
    ax3.set_title("Quan hệ Impressions và Tương tác dự đoán")
    st.pyplot(fig3)
else:
    st.info("Thiếu cột Impressions hoặc Tương tác dự đoán cho scatter plot")

# ===== Phân tích theo account type =====
if "account_type" in df.columns and "predicted_engagement" in df.columns:
    st.subheader("Phân tích theo Loại Account")
    df_acc = df.groupby("account_type").agg(
        Số_posts=("predicted_engagement", "count"),
        Trung_bình_tương_tác=("predicted_engagement", "mean"),
        Trung_bình_impressions=("impressions", "mean") if "impressions" in df.columns else ("predicted_engagement", "mean")
    ).reset_index()

    df_acc = df_acc.sort_values(by="Trung_bình_tương_tác", ascending=False)
    st.dataframe(df_acc)

    # Bar chart top account types
    top_acc = df_acc.head(10)
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    ax4.barh(top_acc["account_type"], top_acc["Trung_bình_tương_tác"], color="#405DE6")
    ax4.invert_yaxis()
    ax4.set_xlabel("Tương tác trung bình")
    ax4.set_title("Top Account Types theo tương tác dự đoán")
    st.pyplot(fig4)
else:
    st.info("Không có cột account_type hoặc Tương tác dự đoán để phân tích theo loại account")

# ===== Phân tích theo content category =====
if "content_category" in df.columns and "predicted_engagement" in df.columns:
    st.subheader("Phân tích theo Danh mục Nội dung")
    df_cat = df.groupby("content_category").agg(
        Số_posts=("predicted_engagement", "count"),
        Trung_bình_tương_tác=("predicted_engagement", "mean"),
        Trung_bình_impressions=("impressions", "mean") if "impressions" in df.columns else ("predicted_engagement", "mean")
    ).reset_index()

    df_cat = df_cat.sort_values(by="Trung_bình_tương_tác", ascending=False)
    st.dataframe(df_cat)

    # Bar chart top content categories
    top_cat = df_cat.head(10)
    fig5, ax5 = plt.subplots(figsize=(10, 5))
    ax5.barh(top_cat["content_category"], top_cat["Trung_bình_tương_tác"], color="#C13584")
    ax5.invert_yaxis()
    ax5.set_xlabel("Tương tác trung bình")
    ax5.set_title("Top Content Categories theo tương tác dự đoán")
    st.pyplot(fig5)
else:
    st.info("Không có cột content_category hoặc Tương tác dự đoán để phân tích theo danh mục nội dung")

# ===== Ranking top N =====
st.subheader("Posts top theo Tương tác dự đoán")
if len(df) > 0 and "predicted_engagement" in df.columns:
    max_n = min(100, len(df))
    n = st.slider("Số lượng top", min_value=5, max_value=max_n, value=min(20, max_n), step=5)
    df_top = df.sort_values(by="predicted_engagement", ascending=False).head(n)
    st.table(df_top[[col for col in ["post_id", "account_type", "media_type", "content_category", "likes", "comments", "impressions", "predicted_engagement"] if col in df_top.columns]].reset_index(drop=True))
else:
    st.info("Không có dữ liệu Top ranking")

# ===== Raw data expander =====
with st.expander("📊 Raw Data - Dữ liệu chi tiết", expanded=False):
    st.subheader(f"Toàn bộ dữ liệu đang lọc ({len(df)} posts)")
    st.dataframe(df, use_container_width=True, height=400)

    # Download filtered data
    csv_filtered = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Tải toàn bộ dữ liệu đang lọc (CSV)",
        data=csv_filtered,
        file_name="instagram_filtered_data.csv",
        mime="text/csv"
    )