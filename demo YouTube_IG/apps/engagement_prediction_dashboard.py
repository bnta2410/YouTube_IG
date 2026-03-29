"""
Dashboard Dự báo Tương tác Nội dung - Phân tích Quốc tế & Thị trường Việt Nam
Content Engagement Prediction Dashboard - International & Vietnam Market Analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import subprocess
import sys
import joblib
from datetime import datetime, timedelta

# ===== CẤU HÌNH TRANG =====
st.set_page_config(
    page_title="Dự báo Tương tác Nội dung - Quốc tế & Việt Nam",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Chuyển đến thư mục gốc dự án
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ===== KIỂU VĂN BẢN =====
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .insight-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-left: 4px solid #2196F3;
        border-radius: 5px;
        margin: 10px 0;
    }
    .market-selector {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    h1 { color: #1f77b4; }
    h2 { color: #ff7f0e; border-bottom: 2px solid #ff7f0e; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ===== CHẠY PIPELINES TỰ ĐỘNG =====
st.sidebar.header("🔄 Kiểm soát Pipeline")

if st.sidebar.button("🚀 Chạy tất cả Pipelines", type="primary"):
    with st.spinner("Đang chạy YouTube pipeline..."):
        try:
            result = subprocess.run([sys.executable, "pipelines/full_pipeline.py"],
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0:
                st.sidebar.success("✅ YouTube pipeline hoàn thành!")
            else:
                st.sidebar.error("❌ YouTube pipeline thất bại")
        except Exception as e:
            st.sidebar.error(f"❌ Lỗi: {e}")

    with st.spinner("Đang chạy Instagram pipeline..."):
        try:
            result = subprocess.run([sys.executable, "pipelines/instagram_pipeline.py"],
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0:
                st.sidebar.success("✅ Instagram pipeline hoàn thành!")
            else:
                st.sidebar.error("❌ Instagram pipeline thất bại")
        except Exception as e:
            st.sidebar.error(f"❌ Lỗi: {e}")

    st.rerun()

# ===== TẢI DỮ LIỆU =====
@st.cache_data
def load_youtube_data():
    try:
        df = pd.read_csv("data/processed/vn_prediction.csv")
        return df if len(df) > 0 else None
    except:
        return None

@st.cache_data
def load_instagram_data():
    try:
        df = pd.read_csv("data/processed/instagram_prediction.csv")
        return df if len(df) > 0 else None
    except:
        return None

@st.cache_data
def load_model():
    try:
        model = joblib.load("models/model.pkl")
        return model
    except:
        return None

youtube_df = load_youtube_data()
instagram_df = load_instagram_data()
model = load_model()

# ===== NẾU KHÔNG CÓ DỮ LIỆU =====
if youtube_df is None and instagram_df is None:
    st.error("⚠️ Không có dữ liệu. Vui lòng chạy pipelines trước.")
    st.stop()

# ===== THANH BÊN: CHỌN THỊ TRƯỜNG =====
st.sidebar.markdown("---")
st.sidebar.subheader("🌍 Chọn Thị trường Phân tích")
market = st.sidebar.radio(
    "Thị trường:",
    ("🌐 Quốc tế", "🇻🇳 Việt Nam"),
    help="Chọn phân tích cho thị trường quốc tế hoặc riêng Việt Nam"
)

# ===== TIÊU ĐỀ CHÍNH =====
st.title("📊 Dự báo Tương tác Nội dung")
st.markdown(f"""
### {'🌐 Phân tích Quốc tế' if market == '🌐 Quốc tế' else '🇻🇳 Thị trường Việt Nam'}

**Báo cáo:** Dự báo mức độ tương tác nội dung từ dữ liệu Instagram/YouTube engagement  
**Cập nhật:** {datetime.now().strftime("%d-%m-%Y %H:%M")}
""")

if market == "🌐 Quốc tế":
    # ===== PHÂN TÍCH QUỐC TẾ =====
    st.markdown("<div class='market-selector'><b>📊 PHÂN TÍCH QUỐC TẾ - INTERNATIONAL MARKET ANALYSIS</b></div>", unsafe_allow_html=True)
    
    tab_int1, tab_int2, tab_int3, tab_int4, tab_int5 = st.tabs([
        "📊 Tóm tắt",
        "📺 YouTube",
        "📸 Instagram",
        "🎯 Hiệu suất Model",
        "🔄 So sánh"
    ])

    # ===== TAB 1: TÓM TẮT =====
    with tab_int1:
        st.header("📊 Tóm tắt Quốc tế")
        
        col1, col2, col3, col4 = st.columns(4)
        
        if youtube_df is not None:
            col1.metric("🎬 Video YouTube", len(youtube_df), "sample toàn cầu")
            col2.metric("📊 Tương tác TB YouTube", f"{youtube_df['predicted_engagement'].mean():.4f}")
        
        if instagram_df is not None:
            col3.metric("📸 Bài viết Instagram", len(instagram_df), "toàn cầu")
            col4.metric("📊 Tương tác TB Instagram", f"{instagram_df['predicted_engagement'].mean():.4f}")
        
        st.divider()
        
        # Insights
        st.subheader("💡 Thông tin chính")
        
        if youtube_df is not None and instagram_df is not None:
            yt_avg = youtube_df['predicted_engagement'].mean()
            ig_avg = instagram_df['predicted_engagement'].mean()
            diff = ((ig_avg - yt_avg) / yt_avg * 100) if yt_avg > 0 else 0
            
            st.markdown(f"""
            - 📈 **Tương tác YouTube:** {yt_avg:.4f} (trung bình)
            - 📈 **Tương tác Instagram:** {ig_avg:.4f} (trung bình)
            - 📊 **Sự chênh lệch:** Instagram {'cao hơn' if diff > 0 else 'thấp hơn'} {abs(diff):.1f}%
            - 🎯 **Tổng dữ liệu:** {len(youtube_df) + len(instagram_df):,} bài viết phân tích
            """)

    # ===== TAB 2: YOUTUBE =====
    with tab_int2:
        if youtube_df is None:
            st.error("❌ Không có dữ liệu YouTube")
        else:
            st.header("📺 Phân tích YouTube Quốc tế")
            
            # Bộ lọc
            st.subheader("🔍 Bộ lọc YouTube")
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            youtube_df_filtered = youtube_df.copy()
            
            with filter_col1:
                min_views, max_views = int(youtube_df['views'].min()), int(youtube_df['views'].max())
                views_range = st.slider("Lượng xem", min_views, max_views, (min_views, max_views), key="yt_views_int")
                youtube_df_filtered = youtube_df_filtered[(youtube_df_filtered['views'] >= views_range[0]) & (youtube_df_filtered['views'] <= views_range[1])]
            
            with filter_col2:
                min_eng, max_eng = float(youtube_df['predicted_engagement'].min()), float(youtube_df['predicted_engagement'].max())
                eng_range = st.slider("Tương tác dự đoán", min_eng, max_eng, (min_eng, max_eng), key="yt_eng_int")
                youtube_df_filtered = youtube_df_filtered[(youtube_df_filtered['predicted_engagement'] >= eng_range[0]) & (youtube_df_filtered['predicted_engagement'] <= eng_range[1])]
            
            with filter_col3:
                sort_by = st.selectbox("Sắp xếp theo", ["Tương tác ↓", "Lượt xem ↓", "Thích ↓"], key="yt_sort_int")
                
            st.write(f"**Dữ liệu sau lọc:** {len(youtube_df_filtered)} video")
            st.divider()
            
            # Thống kê
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📊 Lượt xem TB", f"{youtube_df_filtered['views'].mean():,.0f}")
            col2.metric("❤️ Thích TB", f"{youtube_df_filtered['likes'].mean():,.0f}")
            col3.metric("💬 Bình luận TB", f"{youtube_df_filtered['comments'].mean():,.0f}")
            col4.metric("🎯 Tương tác TB", f"{youtube_df_filtered['predicted_engagement'].mean():.4f}")
            
            st.divider()
            
            # Biểu đồ
            st.subheader("📊 Biểu đồ Phân tích")
            
            chart_col1, chart_col2, chart_col3 = st.columns(3)
            
            with chart_col1:
                fig, ax = plt.subplots(figsize=(9, 5))
                ax.hist(youtube_df_filtered['predicted_engagement'], bins=30, color='#FF0000', alpha=0.7, edgecolor='black')
                ax.set_xlabel('Điểm tương tác dự đoán', fontsize=10)
                ax.set_ylabel('Số lượng video', fontsize=10)
                ax.set_title('Phân phối Tương tác', fontsize=11, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
            
            with chart_col2:
                fig, ax = plt.subplots(figsize=(9, 5))
                ax.scatter(youtube_df_filtered['views'], youtube_df_filtered['predicted_engagement'], 
                          alpha=0.6, c='#FF0000', s=50, edgecolors='darkred', linewidth=0.5)
                ax.set_xlabel('Lượt xem', fontsize=10)
                ax.set_ylabel('Tương tác dự đoán', fontsize=10)
                ax.set_title('Lượt xem vs Tương tác', fontsize=11, fontweight='bold')
                ax.grid(alpha=0.3)
                st.pyplot(fig)
            
            with chart_col3:
                if 'category_id' in youtube_df_filtered.columns:
                    category_eng = youtube_df_filtered.groupby('category_id')['predicted_engagement'].mean().sort_values(ascending=False).head(8)
                    fig, ax = plt.subplots(figsize=(9, 5))
                    ax.barh(range(len(category_eng)), category_eng.values, color='#FF6B6B', alpha=0.7, edgecolor='black')
                    ax.set_yticks(range(len(category_eng)))
                    ax.set_yticklabels([f"Cat {c}" for c in category_eng.index], fontsize=9)
                    ax.set_xlabel('Tương tác trung bình', fontsize=10)
                    ax.set_title('Top 8 Danh mục', fontsize=11, fontweight='bold')
                    ax.invert_yaxis()
                    st.pyplot(fig)

    # ===== TAB 3: INSTAGRAM =====
    with tab_int3:
        if instagram_df is None:
            st.error("❌ Không có dữ liệu Instagram")
        else:
            st.header("📸 Phân tích Instagram Quốc tế")
            
            # Bộ lọc
            st.subheader("🔍 Bộ lọc Instagram")
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            instagram_df_filtered = instagram_df.copy()
            
            with filter_col1:
                if 'account_type' in instagram_df_filtered.columns:
                    account_types = instagram_df_filtered['account_type'].astype(str).unique().tolist()
                    selected_accounts = st.multiselect("Loại tài khoản", account_types, default=account_types, key="ig_acc_int")
                    instagram_df_filtered = instagram_df_filtered[instagram_df_filtered['account_type'].astype(str).isin(selected_accounts)]
            
            with filter_col2:
                if 'impressions' in instagram_df_filtered.columns:
                    min_imp, max_imp = int(instagram_df_filtered['impressions'].min()), int(instagram_df_filtered['impressions'].max())
                    imp_range = st.slider("Lượt xem", min_imp, max_imp, (min_imp, max_imp), key="ig_imp_int")
                    instagram_df_filtered = instagram_df_filtered[(instagram_df_filtered['impressions'] >= imp_range[0]) & (instagram_df_filtered['impressions'] <= imp_range[1])]
            
            with filter_col3:
                if 'media_type' in instagram_df_filtered.columns:
                    media_types = instagram_df_filtered['media_type'].astype(str).unique().tolist()
                    selected_media = st.multiselect("Loại nội dung", media_types, default=media_types, key="ig_media_int")
                    instagram_df_filtered = instagram_df_filtered[instagram_df_filtered['media_type'].astype(str).isin(selected_media)]
            
            st.write(f"**Dữ liệu sau lọc:** {len(instagram_df_filtered)} bài viết")
            st.divider()
            
            # Thống kê
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("👁️ Lượt xem TB", f"{instagram_df_filtered['impressions'].mean():,.0f}" if 'impressions' in instagram_df_filtered.columns else "N/A")
            col2.metric("❤️ Thích TB", f"{instagram_df_filtered['likes'].mean():,.0f}")
            col3.metric("💬 Bình luận TB", f"{instagram_df_filtered['comments'].mean():,.0f}")
            col4.metric("🎯 Tương tác TB", f"{instagram_df_filtered['predicted_engagement'].mean():.4f}")
            
            st.divider()
            
            # Biểu đồ
            st.subheader("📊 Biểu đồ Phân tích")
            
            chart_col1, chart_col2, chart_col3 = st.columns(3)
            
            with chart_col1:
                fig, ax = plt.subplots(figsize=(9, 5))
                ax.hist(instagram_df_filtered['predicted_engagement'], bins=30, color='#E1306C', alpha=0.7, edgecolor='black')
                ax.set_xlabel('Điểm tương tác dự đoán', fontsize=10)
                ax.set_ylabel('Số lượng bài viết', fontsize=10)
                ax.set_title('Phân phối Tương tác', fontsize=11, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
            
            with chart_col2:
                if 'impressions' in instagram_df_filtered.columns:
                    fig, ax = plt.subplots(figsize=(9, 5))
                    ax.scatter(instagram_df_filtered['impressions'], instagram_df_filtered['predicted_engagement'], 
                              alpha=0.6, c='#E1306C', s=50, edgecolors='darkred', linewidth=0.5)
                    ax.set_xlabel('Lượt xem', fontsize=10)
                    ax.set_ylabel('Tương tác dự đoán', fontsize=10)
                    ax.set_title('Lượt xem vs Tương tác', fontsize=11, fontweight='bold')
                    ax.grid(alpha=0.3)
                    st.pyplot(fig)
            
            with chart_col3:
                if 'content_category' in instagram_df_filtered.columns:
                    cat_eng = instagram_df_filtered.groupby('content_category')['predicted_engagement'].mean().sort_values(ascending=False).head(8)
                    fig, ax = plt.subplots(figsize=(9, 5))
                    ax.barh(range(len(cat_eng)), cat_eng.values, color='#F37B63', alpha=0.7, edgecolor='black')
                    ax.set_yticks(range(len(cat_eng)))
                    ax.set_yticklabels(cat_eng.index, fontsize=9)
                    ax.set_xlabel('Tương tác trung bình', fontsize=10)
                    ax.set_title('Top 8 Danh mục Nội dung', fontsize=11, fontweight='bold')
                    ax.invert_yaxis()
                    st.pyplot(fig)

    # ===== TAB 4: HIỆU SUẤT MODEL =====
    with tab_int4:
        st.header("🎯 Hiệu suất Model")
        
        if model is None:
            st.warning("⚠️ Không tìm thấy file model")
        else:
            st.markdown("""
            **Chi tiết Model:**
            - Thuật toán: Random Forest Regressor
            - Số cây: 100
            - Mục tiêu: Dự báo điểm tương tác từ các đặc điểm nội dung
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Các đặc điểm Model")
                features = ["like_ratio", "comment_ratio", "publish_hour", "title_length"]
                for i, feat in enumerate(features, 1):
                    st.write(f"{i}. **{feat}**")
            
            with col2:
                st.subheader("🔍 Tầm quan trọng Đặc điểm")
                if hasattr(model, 'feature_importances_'):
                    feature_importance = pd.DataFrame({
                        'Đặc điểm': features,
                        'Tầm quan trọng': model.feature_importances_
                    }).sort_values('Tầm quan trọng', ascending=False)
                    
                    fig, ax = plt.subplots(figsize=(8, 5))
                    bars = ax.barh(feature_importance['Đặc điểm'], feature_importance['Tầm quan trọng'], color='#1f77b4')
                    ax.set_xlabel('Điểm tầm quan trọng', fontsize=10)
                    ax.set_title('Tầm quan trọng Đặc điểm', fontsize=11, fontweight='bold')
                    
                    for i, bar in enumerate(bars):
                        width = bar.get_width()
                        ax.text(width, bar.get_y() + bar.get_height()/2, f'{width:.4f}', 
                               ha='left', va='center', fontsize=9)
                    
                    st.pyplot(fig)

    # ===== TAB 5: SO SÁNH =====
    with tab_int5:
        st.header("🔄 So sánh YouTube vs Instagram")
        
        if youtube_df is not None and instagram_df is not None:
            comparison_data = {
                'Chỉ số': [
                    'Tổng bài viết',
                    'Tương tác TB',
                    'Tương tác max',
                    'Tương tác min',
                    'Độ lệch chuẩn'
                ],
                'YouTube': [
                    len(youtube_df),
                    f"{youtube_df['predicted_engagement'].mean():.4f}",
                    f"{youtube_df['predicted_engagement'].max():.4f}",
                    f"{youtube_df['predicted_engagement'].min():.4f}",
                    f"{youtube_df['predicted_engagement'].std():.4f}"
                ],
                'Instagram': [
                    len(instagram_df),
                    f"{instagram_df['predicted_engagement'].mean():.4f}",
                    f"{instagram_df['predicted_engagement'].max():.4f}",
                    f"{instagram_df['predicted_engagement'].min():.4f}",
                    f"{instagram_df['predicted_engagement'].std():.4f}"
                ]
            }
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)
            
            st.divider()
            
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                fig, ax = plt.subplots(figsize=(9, 5))
                data_to_plot = [youtube_df['predicted_engagement'], instagram_df['predicted_engagement']]
                bp = ax.boxplot(data_to_plot, labels=['YouTube', 'Instagram'], patch_artist=True)
                
                colors = ['#FF0000', '#E1306C']
                for patch, color in zip(bp['boxes'], colors):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.7)
                
                ax.set_ylabel('Điểm tương tác dự đoán', fontsize=10)
                ax.set_title('So sánh Phân phối Tương tác', fontsize=11, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
            
            with col_comp2:
                fig, ax = plt.subplots(figsize=(9, 5))
                ax.hist(youtube_df['predicted_engagement'], bins=30, alpha=0.6, label='YouTube', color='#FF0000', edgecolor='black')
                ax.hist(instagram_df['predicted_engagement'], bins=30, alpha=0.6, label='Instagram', color='#E1306C', edgecolor='black')
                ax.set_xlabel('Điểm tương tác dự đoán', fontsize=10)
                ax.set_ylabel('Tần suất', fontsize=10)
                ax.set_title('So sánh Phân phối Chồng lắp', fontsize=11, fontweight='bold')
                ax.legend()
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)

else:
    # ===== PHÂN TÍCH VIỆT NAM =====
    st.markdown("<div class='market-selector'><b>🇻🇳 PHÂN TÍCH THỊ TRƯỜNG VIỆT NAM - VIETNAM MARKET ANALYSIS</b></div>", unsafe_allow_html=True)
    
    st.info("🇻🇳 Phân tích chuyên sâu cho thị trường Việt Nam sử dụng dữ liệu từ YouTube API VN region")
    
    tab_vn1, tab_vn2, tab_vn3 = st.tabs([
        "📊 Tóm tắt VN",
        "📺 YouTube VN",
        "📸 Instagram VN"
    ])

    # ===== TAB 1: TÓM TẮT VIỆT NAM =====
    with tab_vn1:
        st.header("📊 Tóm tắt Thị trường Việt Nam")
        
        st.markdown("""
        ### 🇻🇳 Phân tích Riêng Việt Nam
        
        Phân tích này tập trung vào xu hướng tương tác nội dung **dành riêng cho thị trường Việt Nam**
        bao gồm:
        - Video YouTube từ khu vực Việt Nam (VN region)
        - Bài viết Instagram của người dùng/nội dung Việt Nam
        - Các danh mục nội dung phổ biến ở VN
        - Thời gian đăng tối ưu cho thị trường VN
        """)
        
        if youtube_df is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📺 YouTube Việt Nam")
                st.metric("📊 Số video", len(youtube_df))
                st.metric("📈 Tương tác TB", f"{youtube_df['predicted_engagement'].mean():.4f}")
                st.metric("👁️ Lượt xem TB", f"{youtube_df['views'].mean():,.0f}")
            
            with col2:
                st.subheader("💡 Thông tin Chính")
                
                # Top channel
                if 'channel_title' in youtube_df.columns:
                    top_channel = youtube_df['channel_title'].value_counts().head(1)
                    if len(top_channel) > 0:
                        st.write(f"**Kênh hàng đầu:** {top_channel.index[0]}")
                        st.write(f"**Số video:** {top_channel.values[0]}")
                
                # Peak engagement
                peak_row = youtube_df.loc[youtube_df['predicted_engagement'].idxmax()]
                st.write(f"**Tương tác cao nhất:** {peak_row['predicted_engagement']:.4f}")
                st.write(f"**Video:** {peak_row.get('title', 'N/A')[:50]}...")

    # ===== TAB 2: YOUTUBE VIỆT NAM =====
    with tab_vn2:
        if youtube_df is None:
            st.error("❌ Không có dữ liệu YouTube VN")
        else:
            st.header("📺 YouTube Thị trường Việt Nam")
            
            # Bộ lọc nâng cao
            st.subheader("🔍 Bộ lọc Nâng cao")
            
            filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
            
            youtube_df_vn = youtube_df.copy()
            
            with filter_col1:
                min_views, max_views = int(youtube_df_vn['views'].min()), int(youtube_df_vn['views'].max())
                views_range = st.slider("Lượt xem", min_views, max_views, (min_views, max_views), key="yt_views_vn")
                youtube_df_vn = youtube_df_vn[(youtube_df_vn['views'] >= views_range[0]) & (youtube_df_vn['views'] <= views_range[1])]
            
            with filter_col2:
                min_likes, max_likes = int(youtube_df_vn['likes'].min()), int(youtube_df_vn['likes'].max())
                likes_range = st.slider("❤️ Thích", min_likes, max_likes, (min_likes, max_likes), key="yt_likes_vn")
                youtube_df_vn = youtube_df_vn[(youtube_df_vn['likes'] >= likes_range[0]) & (youtube_df_vn['likes'] <= likes_range[1])]
            
            with filter_col3:
                min_comments = int(youtube_df_vn['comments'].min())
                max_comments = int(youtube_df_vn['comments'].max())
                comments_range = st.slider("💬 Bình luận", min_comments, max_comments, (min_comments, max_comments), key="yt_comments_vn")
                youtube_df_vn = youtube_df_vn[(youtube_df_vn['comments'] >= comments_range[0]) & (youtube_df_vn['comments'] <= comments_range[1])]
            
            with filter_col4:
                min_eng, max_eng = float(youtube_df_vn['predicted_engagement'].min()), float(youtube_df_vn['predicted_engagement'].max())
                eng_range = st.slider("🎯 Tương tác", min_eng, max_eng, (min_eng, max_eng), key="yt_eng_vn")
                youtube_df_vn = youtube_df_vn[(youtube_df_vn['predicted_engagement'] >= eng_range[0]) & (youtube_df_vn['predicted_engagement'] <= eng_range[1])]
            
            st.write(f"**Kết quả:** {len(youtube_df_vn)}/{len(youtube_df)} video VN")
            st.divider()
            
            # Thống kê
            stat_col1, stat_col2, stat_col3, stat_col4, stat_col5 = st.columns(5)
            stat_col1.metric("📊 Lượt xem TB", f"{youtube_df_vn['views'].mean():,.0f}")
            stat_col2.metric("❤️ Thích TB", f"{youtube_df_vn['likes'].mean():,.0f}")
            stat_col3.metric("💬 Bình luận TB", f"{youtube_df_vn['comments'].mean():,.0f}")
            stat_col4.metric("🎯 Tương tác TB", f"{youtube_df_vn['predicted_engagement'].mean():.4f}")
            stat_col5.metric("📈 Tỷ lệ Like", f"{(youtube_df_vn['likes'].sum() / youtube_df_vn['views'].sum() * 100):.4f}%")
            
            st.divider()
            
            # Biểu đồ chuyên sâu
            st.subheader("📊 Biểu đồ Phân tích Chi tiết VN")
            
            vn_chart_col1, vn_chart_col2, vn_chart_col3 = st.columns(3)
            
            with vn_chart_col1:
                fig, ax = plt.subplots(figsize=(9, 5))
                ax.hist(youtube_df_vn['predicted_engagement'], bins=25, color='#FFA500', alpha=0.7, edgecolor='black')
                ax.set_xlabel('Điểm tương tác', fontsize=10)
                ax.set_ylabel('Số video', fontsize=10)
                ax.set_title('Phân phối Tương tác - Thị trường VN', fontsize=11, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
            
            with vn_chart_col2:
                if 'publish_hour' in youtube_df_vn.columns:
                    hourly_data = youtube_df_vn.groupby('publish_hour')['predicted_engagement'].mean()
                    fig, ax = plt.subplots(figsize=(9, 5))
                    ax.plot(hourly_data.index, hourly_data.values, marker='o', linewidth=2.5, markersize=8, color='#FF6B6B')
                    ax.fill_between(hourly_data.index, hourly_data.values, alpha=0.3, color='#FF6B6B')
                    ax.set_xlabel('Giờ đăng (0-23)', fontsize=10)
                    ax.set_ylabel('Tương tác trung bình', fontsize=10)
                    ax.set_title('Thời gian Đăng Tối ưu - VN', fontsize=11, fontweight='bold')
                    ax.set_xticks(range(0, 24, 3))
                    ax.grid(alpha=0.3)
                    st.pyplot(fig)
            
            with vn_chart_col3:
                if 'category_id' in youtube_df_vn.columns:
                    CATEGORY_MAP = {
                        "1": "Giải trí", "2": "Xe cộ", "10": "Âm nhạc", "15": "Thú cưng",
                        "17": "Thể thao", "20": "Chơi game", "22": "Con người", "23": "Hài kịch",
                        "24": "Giải trí", "25": "Tin tức", "26": "Phong cách", "27": "Giáo dục",
                        "28": "Khoa học & Công nghệ"
                    }
                    youtube_df_vn['category_name'] = youtube_df_vn['category_id'].astype(str).map(
                        lambda x: CATEGORY_MAP.get(x, f"Danh mục {x}")
                    )
                    cat_eng = youtube_df_vn.groupby('category_name')['predicted_engagement'].mean().sort_values(ascending=False).head(8)
                    
                    fig, ax = plt.subplots(figsize=(9, 5))
                    ax.barh(range(len(cat_eng)), cat_eng.values, color='#FFB6C1', alpha=0.8, edgecolor='black')
                    ax.set_yticks(range(len(cat_eng)))
                    ax.set_yticklabels(cat_eng.index, fontsize=9)
                    ax.set_xlabel('Tương tác TB', fontsize=10)
                    ax.set_title('Top Danh mục Nội dung - VN', fontsize=11, fontweight='bold')
                    ax.invert_yaxis()
                    st.pyplot(fig)
            
            st.divider()
            
            # Bảng dữ liệu chi tiết
            st.subheader("📋 Dữ liệu Chi tiết YouTube VN")
            
            rows_per_page = st.select_slider("Hàng mỗi trang", options=[10, 25, 50], value=25, key="yt_vn_rows")
            total_pages = (len(youtube_df_vn) + rows_per_page - 1) // rows_per_page
            page = st.slider("Trang", 1, max(1, total_pages), 1, key="yt_vn_page")
            
            start_idx = (page - 1) * rows_per_page
            end_idx = start_idx + rows_per_page
            
            display_cols = ['title', 'channel_title', 'views', 'likes', 'comments', 'predicted_engagement']
            display_cols = [col for col in display_cols if col in youtube_df_vn.columns]
            
            st.dataframe(
                youtube_df_vn[display_cols].iloc[start_idx:end_idx].reset_index(drop=True),
                use_container_width=True,
                height=400
            )

    # ===== TAB 3: INSTAGRAM VIỆT NAM =====
    with tab_vn3:
        if instagram_df is None:
            st.error("❌ Không có dữ liệu Instagram VN")
        else:
            st.header("📸 Instagram Thị trường Việt Nam")
            
            # Bộ lọc nâng cao
            st.subheader("🔍 Bộ lọc Nâng cao")
            
            instagram_df_vn = instagram_df.copy()
            
            filter_row1_col1, filter_row1_col2, filter_row1_col3 = st.columns(3)
            
            with filter_row1_col1:
                if 'content_category' in instagram_df_vn.columns:
                    categories = instagram_df_vn['content_category'].astype(str).unique().tolist()
                    selected_cats = st.multiselect("Danh mục nội dung", categories, default=categories, key="ig_vn_cat")
                    instagram_df_vn = instagram_df_vn[instagram_df_vn['content_category'].astype(str).isin(selected_cats)]
            
            with filter_row1_col2:
                if 'account_type' in instagram_df_vn.columns:
                    acc_types = instagram_df_vn['account_type'].astype(str).unique().tolist()
                    selected_accs = st.multiselect("Loại tài khoản", acc_types, default=acc_types, key="ig_vn_acc")
                    instagram_df_vn = instagram_df_vn[instagram_df_vn['account_type'].astype(str).isin(selected_accs)]
            
            with filter_row1_col3:
                if 'media_type' in instagram_df_vn.columns:
                    media_types = instagram_df_vn['media_type'].astype(str).unique().tolist()
                    selected_media = st.multiselect("Loại nội dung", media_types, default=media_types, key="ig_vn_media")
                    instagram_df_vn = instagram_df_vn[instagram_df_vn['media_type'].astype(str).isin(selected_media)]
            
            filter_row2_col1, filter_row2_col2, filter_row2_col3 = st.columns(3)
            
            with filter_row2_col1:
                if 'likes' in instagram_df_vn.columns:
                    min_likes = int(instagram_df_vn['likes'].min())
                    max_likes = int(instagram_df_vn['likes'].max())
                    likes_range = st.slider("❤️ Thích", min_likes, max_likes, (min_likes, max_likes), key="ig_vn_likes")
                    instagram_df_vn = instagram_df_vn[(instagram_df_vn['likes'] >= likes_range[0]) & (instagram_df_vn['likes'] <= likes_range[1])]
            
            with filter_row2_col2:
                if 'impressions' in instagram_df_vn.columns:
                    min_imp = int(instagram_df_vn['impressions'].min())
                    max_imp = int(instagram_df_vn['impressions'].max())
                    imp_range = st.slider("👁️ Lượt xem", min_imp, max_imp, (min_imp, max_imp), key="ig_vn_imp")
                    instagram_df_vn = instagram_df_vn[(instagram_df_vn['impressions'] >= imp_range[0]) & (instagram_df_vn['impressions'] <= imp_range[1])]
            
            with filter_row2_col3:
                if 'predicted_engagement' in instagram_df_vn.columns:
                    min_eng = float(instagram_df_vn['predicted_engagement'].min())
                    max_eng = float(instagram_df_vn['predicted_engagement'].max())
                    eng_range = st.slider("🎯 Tương tác", min_eng, max_eng, (min_eng, max_eng), key="ig_vn_eng")
                    instagram_df_vn = instagram_df_vn[(instagram_df_vn['predicted_engagement'] >= eng_range[0]) & (instagram_df_vn['predicted_engagement'] <= eng_range[1])]
            
            st.write(f"**Kết quả:** {len(instagram_df_vn)}/{len(instagram_df)} bài viết Instagram")
            st.divider()
            
            # Thống kê
            stat_col1, stat_col2, stat_col3, stat_col4, stat_col5 = st.columns(5)
            stat_col1.metric("👁️ Lượt xem TB", f"{instagram_df_vn['impressions'].mean():,.0f}" if 'impressions' in instagram_df_vn.columns else "N/A")
            stat_col2.metric("❤️ Thích TB", f"{instagram_df_vn['likes'].mean():,.0f}")
            stat_col3.metric("💬 Bình luận TB", f"{instagram_df_vn['comments'].mean():,.0f}")
            stat_col4.metric("🎯 Tương tác TB", f"{instagram_df_vn['predicted_engagement'].mean():.4f}")
            stat_col5.metric("📈 Tỷ lệ Like", f"{(instagram_df_vn['likes'].sum() / instagram_df_vn['impressions'].sum() * 100):.4f}%" if 'impressions' in instagram_df_vn.columns else "N/A")
            
            st.divider()
            
            # Biểu đồ chuyên sâu
            st.subheader("📊 Biểu đồ Phân tích Chi tiết VN")
            
            vn_ig_col1, vn_ig_col2, vn_ig_col3 = st.columns(3)
            
            with vn_ig_col1:
                fig, ax = plt.subplots(figsize=(9, 5))
                ax.hist(instagram_df_vn['predicted_engagement'], bins=25, color='#FFA500', alpha=0.7, edgecolor='black')
                ax.set_xlabel('Điểm tương tác', fontsize=10)
                ax.set_ylabel('Số bài viết', fontsize=10)
                ax.set_title('Phân phối Tương tác - Instagram VN', fontsize=11, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
            
            with vn_ig_col2:
                if 'content_category' in instagram_df_vn.columns:
                    cat_eng = instagram_df_vn.groupby('content_category')['predicted_engagement'].mean().sort_values(ascending=False).head(8)
                    fig, ax = plt.subplots(figsize=(9, 5))
                    ax.barh(range(len(cat_eng)), cat_eng.values, color='#FFB6C1', alpha=0.8, edgecolor='black')
                    ax.set_yticks(range(len(cat_eng)))
                    ax.set_yticklabels(cat_eng.index, fontsize=9)
                    ax.set_xlabel('Tương tác TB', fontsize=10)
                    ax.set_title('Top Danh mục Nội dung - VN', fontsize=11, fontweight='bold')
                    ax.invert_yaxis()
                    st.pyplot(fig)
            
            with vn_ig_col3:
                if 'account_type' in instagram_df_vn.columns:
                    acc_eng = instagram_df_vn.groupby('account_type')['predicted_engagement'].mean().sort_values(ascending=False)
                    fig, ax = plt.subplots(figsize=(9, 5))
                    ax.bar(range(len(acc_eng)), acc_eng.values, color='#FFD700', alpha=0.8, edgecolor='black')
                    ax.set_xticks(range(len(acc_eng)))
                    ax.set_xticklabels(acc_eng.index, rotation=45, ha='right', fontsize=9)
                    ax.set_ylabel('Tương tác TB', fontsize=10)
                    ax.set_title('Loại Tài khoản - VN', fontsize=11, fontweight='bold')
                    st.pyplot(fig)
            
            st.divider()
            
            # Bảng dữ liệu chi tiết
            st.subheader("📋 Dữ liệu Chi tiết Instagram VN")
            
            rows_per_page = st.select_slider("Hàng mỗi trang", options=[10, 25, 50], value=25, key="ig_vn_rows")
            total_pages = (len(instagram_df_vn) + rows_per_page - 1) // rows_per_page
            page = st.slider("Trang", 1, max(1, total_pages), 1, key="ig_vn_page")
            
            start_idx = (page - 1) * rows_per_page
            end_idx = start_idx + rows_per_page
            
            display_cols = ['post_id', 'account_type', 'content_category', 'likes', 'comments', 'impressions', 'predicted_engagement']
            display_cols = [col for col in display_cols if col in instagram_df_vn.columns]
            
            st.dataframe(
                instagram_df_vn[display_cols].iloc[start_idx:end_idx].reset_index(drop=True),
                use_container_width=True,
                height=400
            )

# ===== CHÂN TRANG =====
st.divider()
st.markdown(f"""
---
**📊 Dashboard Dự báo Tương tác Nội dung**  
*Phân tích Quốc tế & Thị trường Việt Nam*

**Cập nhật:** {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}  
**Nguồn dữ liệu:** YouTube API VN Region + Kaggle Instagram Analytics + Kaggle YouTube Dataset  
**Công nghệ:** Python, Streamlit, Pandas, Scikit-learn
""")
