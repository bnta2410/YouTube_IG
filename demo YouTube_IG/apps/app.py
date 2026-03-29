import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import subprocess
import sys

# Change to project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Social Media Engagement Analysis", layout="wide", page_icon="📊")

# ===== AUTO RUN PIPELINES =====
st.sidebar.header("🔄 Pipeline Control")

if st.sidebar.button("🚀 Run All Pipelines", type="primary"):
    with st.spinner("Running YouTube pipeline..."):
        try:
            result = subprocess.run([sys.executable, "pipelines/full_pipeline.py"],
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0:
                st.sidebar.success("✅ YouTube pipeline completed!")
            else:
                st.sidebar.error(f"❌ YouTube pipeline failed: {result.stderr}")
        except Exception as e:
            st.sidebar.error(f"❌ Error running YouTube pipeline: {e}")

    with st.spinner("Running Instagram pipeline..."):
        try:
            result = subprocess.run([sys.executable, "pipelines/instagram_pipeline.py"],
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0:
                st.sidebar.success("✅ Instagram pipeline completed!")
            else:
                st.sidebar.error(f"❌ Instagram pipeline failed: {result.stderr}")
        except Exception as e:
            st.sidebar.error(f"❌ Error running Instagram pipeline: {e}")

    st.rerun()

# ===== LOAD DATA =====
def load_platform_data(platform_name, data_file, required_cols):
    if not os.path.exists(data_file):
        st.error(f"⚠️ Dữ liệu {platform_name} không tìm thấy: {data_file}. Chạy pipeline trước.")
        return None

    try:
        df = pd.read_csv(data_file)
        for col in required_cols:
            if col not in df.columns:
                st.error(f"⚠️ Cột cần thiết bị thiếu trong {platform_name}: {col}")
                return None
        return df
    except Exception as e:
        st.error(f"⚠️ Lỗi khi đọc {platform_name}: {e}")
        return None

# Load YouTube data
youtube_df = load_platform_data("YouTube", "data/processed/vn_prediction.csv",
                               ["predicted_engagement", "views", "title"])

# Load Instagram data
instagram_df = load_platform_data("Instagram", "data/processed/instagram_prediction.csv",
                                 ["predicted_engagement", "likes", "comments", "impressions"])

st.title("📊 Social Media Engagement Analysis Dashboard")
st.markdown("#### Phân tích tương tác YouTube & Instagram")

# ===== MAIN DASHBOARD =====
if youtube_df is not None or instagram_df is not None:
    tab1, tab2 = st.tabs(["📺 YouTube Analysis", "📸 Instagram Analysis"])

    # ===== YOUTUBE TAB =====
    with tab1:
        if youtube_df is None:
            st.error("Không có dữ liệu YouTube. Chạy pipeline trước.")
        else:
            # Category ID mapping (YouTube)
            CATEGORY_MAP = {
                "1": "Phim & Hoạt hình",
                "2": "Xe & Phương tiện",
                "10": "Âm nhạc",
                "15": "Thú cưng & Động vật",
                "17": "Thể thao",
                "18": "Phim ngắn",
                "19": "Du lịch & Sự kiện",
                "20": "Trò chơi",
                "21": "Vlog cá nhân",
                "22": "Con người & Blog",
                "23": "Hài kịch",
                "24": "Giải trí",
                "25": "Tin tức & Chính trị",
                "26": "Hướng dẫn & Phong cách",
                "27": "Giáo dục",
                "28": "Khoa học & Công nghệ",
                "29": "Tổ chức phi lợi nhuận",
                "30": "Phim ảnh",
                "32": "Hành động & Phiêu lưu",
                "33": "Kinh điển",
                "34": "Hài",
                "35": "Tài liệu",
                "36": "Chính kịch",
                "37": "Gia đình",
                "39": "Kinh dị",
                "40": "Kinh tế - Viễn tưởng",
                "41": "Tâm lý",
                "43": "Chương trình",
                "44": "Trailer"
            }

            # Dịch tên cột sang tiếng Việt (nếu tồn tại)
            column_map = {
                "video_id": "ID video",
                "title": "Tiêu đề",
                "channel": "Kênh",
                "channel_title": "Kênh",
                "category_id": "Thể loại",
                "views": "Lượt xem",
                "likes": "Thích",
                "comment_count": "Bình luận",
                "comments": "Bình luận",
                "publish_time": "Thời gian xuất bản",
                "predicted_engagement": "Tương tác dự đoán",
                "engagement_rate": "Tỷ lệ tương tác",
            }

            existing_map = {k: v for k, v in column_map.items() if k in youtube_df.columns}
            if existing_map:
                youtube_df = youtube_df.rename(columns=existing_map)

            # Map category ID to category name if Thể loại exists
            if "Thể loại" in youtube_df.columns:
                youtube_df["Thể loại"] = youtube_df["Thể loại"].astype(str).map(lambda x: CATEGORY_MAP.get(x, f"Thể loại {x}"))

            st.header("📺 YouTube Engagement Analysis")

            # Info bar
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Tổng video", len(youtube_df))
            col2.metric("Tương tác trung bình", round(youtube_df["Tương tác dự đoán"].mean(), 4))
            col3.metric("Lượt xem trung bình", int(youtube_df["Lượt xem"].mean()))
            col4.metric("Số thể loại", youtube_df["Thể loại"].nunique() if "Thể loại" in youtube_df.columns else 0)

            # Filters
            st.subheader("🔍 Bộ lọc YouTube")
            col_f1, col_f2 = st.columns(2)

            with col_f1:
                if "Thể loại" in youtube_df.columns:
                    category_values = youtube_df["Thể loại"].astype(str).sort_values().unique().tolist()
                    selected_categories = st.multiselect("Chọn thể loại", category_values, default=category_values, key="yt_cat")
                    youtube_df = youtube_df[youtube_df["Thể loại"].astype(str).isin(selected_categories)]

            with col_f2:
                search_title = st.text_input("Tìm theo tiêu đề", key="yt_search")
                if search_title:
                    youtube_df = youtube_df[youtube_df["Tiêu đề"].astype(str).str.contains(search_title, case=False, na=False)]

            # Charts
            st.subheader("📈 Phân tích YouTube")
            col_a, col_b = st.columns(2)

            with col_a:
                fig, ax = plt.subplots()
                youtube_df["Tương tác dự đoán"].hist(bins=30, ax=ax, color="#FF0000")
                ax.set_xlabel("Tương tác dự đoán")
                ax.set_ylabel("Số lượng video")
                ax.set_title("Phân phối Tương tác YouTube")
                st.pyplot(fig)

            with col_b:
                if len(youtube_df) > 0 and "Lượt xem" in youtube_df.columns and "Tương tác dự đoán" in youtube_df.columns:
                    fig, ax = plt.subplots()
                    ax.scatter(youtube_df["Lượt xem"], youtube_df["Tương tác dự đoán"], alpha=0.6, c="#FF0000", s=40)
                    ax.set_xlabel("Lượt xem")
                    ax.set_ylabel("Tương tác dự đoán")
                    ax.set_title("Views vs Engagement")
                    st.pyplot(fig)

            # Category Analysis
            if "Thể loại" in youtube_df.columns and "Tương tác dự đoán" in youtube_df.columns:
                st.subheader("🎯 Phân tích theo Thể loại YouTube")
                df_cat = youtube_df.groupby("Thể loại").agg(
                    Số_video=("Tương tác dự đoán", "count"),
                    Trung_bình_tương_tác=("Tương tác dự đoán", "mean"),
                    Trung_bình_lượt_xem=("Lượt xem", "mean")
                ).reset_index().sort_values(by="Trung_bình_tương_tác", ascending=False)

                st.dataframe(df_cat)

                # Bar chart
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.barh(df_cat["Thể loại"].head(10), df_cat["Trung_bình_tương_tác"].head(10), color="#FF0000")
                ax.invert_yaxis()
                ax.set_xlabel("Tương tác trung bình")
                ax.set_title("Top 10 Thể loại YouTube")
                st.pyplot(fig)

            # Top videos
            st.subheader("🏆 Top Videos YouTube")
            if len(youtube_df) > 0:
                n = st.slider("Số lượng top", 5, min(50, len(youtube_df)), 20, key="yt_top")
                df_top = youtube_df.sort_values(by="Tương tác dự đoán", ascending=False).head(n)
                st.table(df_top[["Tiêu đề", "Kênh", "Thể loại", "Lượt xem", "Tương tác dự đoán"]].reset_index(drop=True))

    # ===== INSTAGRAM TAB =====
    with tab2:
        if instagram_df is None:
            st.error("Không có dữ liệu Instagram. Chạy pipeline trước.")
        else:
            st.header("📸 Instagram Engagement Analysis")

            # Info bar
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Tổng posts", len(instagram_df))
            col2.metric("Tương tác trung bình", round(instagram_df["predicted_engagement"].mean(), 4))
            col3.metric("Impressions trung bình", int(instagram_df["impressions"].mean()))
            col4.metric("Số account types", instagram_df["account_type"].nunique() if "account_type" in instagram_df.columns else 0)

            # Filters
            st.subheader("🔍 Bộ lọc Instagram")
            col_f1, col_f2, col_f3 = st.columns(3)

            with col_f1:
                if "account_type" in instagram_df.columns:
                    account_types = instagram_df["account_type"].astype(str).sort_values().unique().tolist()
                    selected_accounts = st.multiselect("Chọn loại account", account_types, default=account_types, key="ig_acc")
                    instagram_df = instagram_df[instagram_df["account_type"].astype(str).isin(selected_accounts)]

            with col_f2:
                if "media_type" in instagram_df.columns:
                    media_types = instagram_df["media_type"].astype(str).sort_values().unique().tolist()
                    selected_media = st.multiselect("Chọn loại media", media_types, default=media_types, key="ig_media")
                    instagram_df = instagram_df[instagram_df["media_type"].astype(str).isin(selected_media)]

            with col_f3:
                if "content_category" in instagram_df.columns:
                    content_cats = instagram_df["content_category"].astype(str).sort_values().unique().tolist()
                    selected_cats = st.multiselect("Chọn danh mục", content_cats, default=content_cats, key="ig_cat")
                    instagram_df = instagram_df[instagram_df["content_category"].astype(str).isin(selected_cats)]

            # Charts
            st.subheader("📈 Phân tích Instagram")
            col_a, col_b = st.columns(2)

            with col_a:
                fig, ax = plt.subplots()
                instagram_df["predicted_engagement"].hist(bins=30, ax=ax, color="#E1306C")
                ax.set_xlabel("Tương tác dự đoán")
                ax.set_ylabel("Số lượng posts")
                ax.set_title("Phân phối Tương tác Instagram")
                st.pyplot(fig)

            with col_b:
                if len(instagram_df) > 0 and "impressions" in instagram_df.columns and "predicted_engagement" in instagram_df.columns:
                    fig, ax = plt.subplots()
                    ax.scatter(instagram_df["impressions"], instagram_df["predicted_engagement"], alpha=0.6, c="#E1306C", s=40)
                    ax.set_xlabel("Impressions")
                    ax.set_ylabel("Tương tác dự đoán")
                    ax.set_title("Impressions vs Engagement")
                    st.pyplot(fig)

            # Account Type Analysis
            if "account_type" in instagram_df.columns and "predicted_engagement" in instagram_df.columns:
                st.subheader("🎯 Phân tích theo Loại Account Instagram")
                df_acc = instagram_df.groupby("account_type").agg(
                    Số_posts=("predicted_engagement", "count"),
                    Trung_bình_tương_tác=("predicted_engagement", "mean"),
                    Trung_bình_impressions=("impressions", "mean")
                ).reset_index().sort_values(by="Trung_bình_tương_tác", ascending=False)

                st.dataframe(df_acc)

                # Bar chart
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.barh(df_acc["account_type"], df_acc["Trung_bình_tương_tác"], color="#E1306C")
                ax.invert_yaxis()
                ax.set_xlabel("Tương tác trung bình")
                ax.set_title("Account Types Instagram")
                st.pyplot(fig)

            # Content Category Analysis
            if "content_category" in instagram_df.columns and "predicted_engagement" in instagram_df.columns:
                st.subheader("🎨 Phân tích theo Danh mục Nội dung Instagram")
                df_cat = instagram_df.groupby("content_category").agg(
                    Số_posts=("predicted_engagement", "count"),
                    Trung_bình_tương_tác=("predicted_engagement", "mean"),
                    Trung_bình_impressions=("impressions", "mean")
                ).reset_index().sort_values(by="Trung_bình_tương_tác", ascending=False)

                st.dataframe(df_cat.head(10))

                # Bar chart
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.barh(df_cat["content_category"].head(10), df_cat["Trung_bình_tương_tác"].head(10), color="#C13584")
                ax.invert_yaxis()
                ax.set_xlabel("Tương tác trung bình")
                ax.set_title("Top 10 Content Categories Instagram")
                st.pyplot(fig)

            # Top posts
            st.subheader("🏆 Top Posts Instagram")
            if len(instagram_df) > 0:
                n = st.slider("Số lượng top", 5, min(50, len(instagram_df)), 20, key="ig_top")
                df_top = instagram_df.sort_values(by="predicted_engagement", ascending=False).head(n)
                st.table(df_top[["post_id", "account_type", "media_type", "content_category", "likes", "comments", "impressions", "predicted_engagement"]].reset_index(drop=True))

else:
    st.warning("⚠️ Không có dữ liệu từ cả YouTube và Instagram. Vui lòng chạy pipelines trước.")

# ===== FOOTER =====
st.markdown("---")
st.markdown("**📊 Social Media Engagement Analysis Dashboard** | Built with Streamlit")
st.markdown("Data sources: YouTube API + Kaggle datasets")