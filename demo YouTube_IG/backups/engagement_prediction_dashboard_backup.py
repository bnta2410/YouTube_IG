"""
Comprehensive Content Engagement Prediction Dashboard
Báo cáo: Dự báo mức độ tương tác nội dung số từ bộ dữ liệu instagram/youtube engagement
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import subprocess
import sys
import joblib
from datetime import datetime

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Content Engagement Prediction Report",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Change to project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ===== STYLING =====
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
    h1 { color: #1f77b4; }
    h2 { color: #ff7f0e; border-bottom: 2px solid #ff7f0e; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

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
                st.sidebar.error(f"❌ YouTube pipeline failed")
        except Exception as e:
            st.sidebar.error(f"❌ Error: {e}")

    with st.spinner("Running Instagram pipeline..."):
        try:
            result = subprocess.run([sys.executable, "pipelines/instagram_pipeline.py"],
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0:
                st.sidebar.success("✅ Instagram pipeline completed!")
            else:
                st.sidebar.error(f"❌ Instagram pipeline failed")
        except Exception as e:
            st.sidebar.error(f"❌ Error: {e}")

    st.rerun()

# ===== DATA LOADING =====
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

# ===== HEADER =====
st.title("📊 Content Engagement Prediction Report")
st.markdown("""
### Dự báo mức độ tương tác nội dung số từ bộ dữ liệu Instagram/YouTube engagement

**Mục tiêu:** Phân tích và dự báo mức độ tương tác nội dung trên các nền tảng mạng xã hội (YouTube & Instagram)  
**Phương pháp:** Random Forest Regression + Feature Engineering  
**Cập nhật:** {}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")))

if youtube_df is None and instagram_df is None:
    st.error("⚠️ No data available. Please run the pipelines first.")
    st.stop()

# ===== NAVIGATION =====
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Summary",
    "📺 YouTube Analysis",
    "📸 Instagram Analysis",
    "🎯 Model Performance",
    "🔄 Cross-Platform Comparison"
])

# ===== TAB 1: EXECUTIVE SUMMARY =====
with tab1:
    st.header("Executive Summary - Tóm tắt báo cáo")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Key metrics
        st.subheader("📈 Key Metrics")
        
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        total_videos = len(youtube_df) if youtube_df is not None else 0
        total_posts = len(instagram_df) if instagram_df is not None else 0
        
        metrics_col1.metric("YouTube Videos", total_videos, "500 samples")
        metrics_col2.metric("Instagram Posts", total_posts, "30K+ samples")
        
        if youtube_df is not None:
            avg_yt_engagement = youtube_df["predicted_engagement"].mean()
            metrics_col3.metric("Avg YouTube Engagement", f"{avg_yt_engagement:.4f}", "prediction score")
        
        if instagram_df is not None:
            avg_ig_engagement = instagram_df["predicted_engagement"].mean()
            metrics_col4.metric("Avg Instagram Engagement", f"{avg_ig_engagement:.4f}", "prediction score")
    
    with col2:
        st.info("📌 **Report Status:** ✅ Ready")
    
    # Dataset overview
    st.subheader("📋 Dataset Overview")
    
    overview_col1, overview_col2 = st.columns(2)
    
    with overview_col1:
        st.markdown("**YouTube Dataset:**")
        st.write(f"- Total videos: {total_videos}")
        if youtube_df is not None:
            st.write(f"- Avg views: {youtube_df['views'].mean():,.0f}")
            st.write(f"- Date range: {youtube_df.get('publish_time', pd.Series()).min() if 'publish_time' in youtube_df.columns else 'N/A'}")
    
    with overview_col2:
        st.markdown("**Instagram Dataset:**")
        st.write(f"- Total posts: {total_posts}")
        if instagram_df is not None:
            st.write(f"- Avg impressions: {instagram_df.get('impressions', pd.Series()).mean():,.0f}")
            st.write(f"- Account types: {instagram_df.get('account_type', pd.Series()).nunique() if 'account_type' in instagram_df.columns else 'N/A'}")
    
    # Key insights
    st.subheader("💡 Key Insights")
    
    insights = []
    
    if youtube_df is not None:
        top_yt = youtube_df.nlargest(1, 'predicted_engagement')
        if len(top_yt) > 0:
            insights.append(f"🔥 Top YouTube video has highest engagement score: {top_yt['predicted_engagement'].values[0]:.4f}")
    
    if instagram_df is not None:
        top_ig = instagram_df.nlargest(1, 'predicted_engagement')
        if len(top_ig) > 0:
            insights.append(f"🔥 Top Instagram post has highest engagement score: {top_ig['predicted_engagement'].values[0]:.4f}")
    
    if youtube_df is not None and instagram_df is not None:
        yt_avg = youtube_df['predicted_engagement'].mean()
        ig_avg = instagram_df['predicted_engagement'].mean()
        diff_pct = ((ig_avg - yt_avg) / yt_avg * 100) if yt_avg > 0 else 0
        insights.append(f"📊 Instagram engagement is {abs(diff_pct):.1f}% {'higher' if diff_pct > 0 else 'lower'} than YouTube on average")
    
    for idx, insight in enumerate(insights, 1):
        st.markdown(f"<div class='insight-box'>{idx}. {insight}</div>", unsafe_allow_html=True)

# ===== TAB 2: YOUTUBE ANALYSIS =====
with tab2:
    if youtube_df is None:
        st.error("❌ No YouTube data available. Run the pipeline first.")
    else:
        st.header("📺 YouTube Engagement Analysis")
        
        # Display summary stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Videos", len(youtube_df), f"Δ {len(youtube_df)} from pipeline")
        col2.metric("Avg Predicted Engagement", f"{youtube_df['predicted_engagement'].mean():.4f}")
        col3.metric("Max Predicted Engagement", f"{youtube_df['predicted_engagement'].max():.4f}")
        col4.metric("Min Predicted Engagement", f"{youtube_df['predicted_engagement'].min():.4f}")
        
        st.divider()
        
        # ===== SECTION 1: ENGAGEMENT DISTRIBUTION =====
        st.subheader("📈 Engagement Distribution Analysis")
        
        col_chart1, col_chart2, col_chart3 = st.columns(3)
        
        with col_chart1:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.hist(youtube_df['predicted_engagement'], bins=40, color='#FF0000', alpha=0.7, edgecolor='black')
            ax.set_xlabel('Predicted Engagement Score', fontsize=10)
            ax.set_ylabel('Number of Videos', fontsize=10)
            ax.set_title('Distribution of Engagement', fontsize=11, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)
        
        with col_chart2:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(youtube_df['views'], youtube_df['predicted_engagement'], 
                      alpha=0.6, c='#FF0000', s=50, edgecolors='darkred', linewidth=0.5)
            ax.set_xlabel('Views', fontsize=10)
            ax.set_ylabel('Predicted Engagement', fontsize=10)
            ax.set_title('Views vs Engagement', fontsize=11, fontweight='bold')
            ax.grid(alpha=0.3)
            st.pyplot(fig)
        
        with col_chart3:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(youtube_df['likes'], youtube_df['predicted_engagement'], 
                      alpha=0.6, c='#00A4EF', s=50, edgecolors='darkblue', linewidth=0.5)
            ax.set_xlabel('Likes', fontsize=10)
            ax.set_ylabel('Predicted Engagement', fontsize=10)
            ax.set_title('Likes vs Engagement', fontsize=11, fontweight='bold')
            ax.grid(alpha=0.3)
            st.pyplot(fig)
        
        st.divider()
        
        # ===== SECTION 2: CATEGORY ANALYSIS =====
        st.subheader("🎯 Category/Topic Analysis - User Interaction Preferences")
        
        if 'category_id' in youtube_df.columns:
            # Category mapping
            CATEGORY_MAP = {
                "1": "Film & Animation", "2": "Autos & Vehicles", "10": "Music",
                "15": "Pets & Animals", "17": "Sports", "18": "Short Movies",
                "19": "Travel & Events", "20": "Gaming", "21": "Videoblogging",
                "22": "People & Blogs", "23": "Comedy", "24": "Entertainment",
                "25": "News & Politics", "26": "Howto & Style", "27": "Education",
                "28": "Science & Technology", "29": "Nonprofits & Activism"
            }
            
            youtube_df_cat = youtube_df.copy()
            youtube_df_cat['category'] = youtube_df_cat['category_id'].astype(str).map(
                lambda x: CATEGORY_MAP.get(x, f"Category {x}")
            )
            
            # Category statistics
            category_stats = youtube_df_cat.groupby('category').agg({
                'predicted_engagement': ['count', 'mean', 'max'],
                'views': 'mean',
                'likes': 'mean',
                'comments': 'mean'
            }).round(4)
            
            category_stats.columns = ['Video_Count', 'Avg_Engagement', 'Max_Engagement', 'Avg_Views', 'Avg_Likes', 'Avg_Comments']
            category_stats = category_stats.sort_values('Avg_Engagement', ascending=False)
            
            # Display category table
            st.write("**Category Performance Metrics:**")
            st.dataframe(category_stats, use_container_width=True)
            
            # Category charts
            col_cat1, col_cat2 = st.columns(2)
            
            with col_cat1:
                fig, ax = plt.subplots(figsize=(12, 6))
                top_categories = category_stats.head(10)
                bars = ax.barh(range(len(top_categories)), top_categories['Avg_Engagement'], color='#FF0000', alpha=0.7, edgecolor='black')
                ax.set_yticks(range(len(top_categories)))
                ax.set_yticklabels(top_categories.index)
                ax.set_xlabel('Average Engagement Score', fontsize=10)
                ax.set_title('Top 10 Categories by Engagement (Most Interactive Topics)', fontsize=11, fontweight='bold')
                ax.invert_yaxis()
                
                # Add value labels
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax.text(width, bar.get_y() + bar.get_height()/2, f'{width:.4f}', 
                           ha='left', va='center', fontsize=9)
                
                st.pyplot(fig)
            
            with col_cat2:
                fig, ax = plt.subplots(figsize=(12, 6))
                video_counts = category_stats['Video_Count'].sort_values(ascending=False).head(10)
                bars = ax.barh(range(len(video_counts)), video_counts, color='#00A4EF', alpha=0.7, edgecolor='black')
                ax.set_yticks(range(len(video_counts)))
                ax.set_yticklabels(video_counts.index)
                ax.set_xlabel('Number of Videos', fontsize=10)
                ax.set_title('Top 10 Categories by Video Count', fontsize=11, fontweight='bold')
                ax.invert_yaxis()
                
                # Add value labels
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax.text(width, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                           ha='left', va='center', fontsize=9)
                
                st.pyplot(fig)
        
        st.divider()
        
        # ===== SECTION 3: ENGAGEMENT TREND ANALYSIS =====
        st.subheader("📊 Engagement Trend Analysis")
        
        col_trend1, col_trend2 = st.columns(2)
        
        with col_trend1:
            # Engagement by like ratio
            youtube_df_sorted = youtube_df.sort_values('like_ratio')
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(youtube_df_sorted['like_ratio'], youtube_df_sorted['predicted_engagement'],
                      alpha=0.6, c='#FF0000', s=50, edgecolors='darkred', linewidth=0.5)
            ax.set_xlabel('Like Ratio (Likes/Views)', fontsize=10)
            ax.set_ylabel('Predicted Engagement', fontsize=10)
            ax.set_title('Engagement Trend by Like Ratio', fontsize=11, fontweight='bold')
            ax.grid(alpha=0.3)
            st.pyplot(fig)
        
        with col_trend2:
            # Engagement by comment ratio
            youtube_df_sorted = youtube_df.sort_values('comment_ratio')
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(youtube_df_sorted['comment_ratio'], youtube_df_sorted['predicted_engagement'],
                      alpha=0.6, c='#00A4EF', s=50, edgecolors='darkblue', linewidth=0.5)
            ax.set_xlabel('Comment Ratio (Comments/Views)', fontsize=10)
            ax.set_ylabel('Predicted Engagement', fontsize=10)
            ax.set_title('Engagement Trend by Comment Ratio', fontsize=11, fontweight='bold')
            ax.grid(alpha=0.3)
            st.pyplot(fig)
        
        col_trend3, col_trend4 = st.columns(2)
        
        with col_trend3:
            # Engagement by publish hour
            hourly_engagement = youtube_df.groupby('publish_hour')['predicted_engagement'].agg(['mean', 'count'])
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(hourly_engagement.index, hourly_engagement['mean'], marker='o', linewidth=2, markersize=8, color='#FF0000', label='Avg Engagement')
            ax.fill_between(hourly_engagement.index, hourly_engagement['mean'], alpha=0.3, color='#FF0000')
            ax.set_xlabel('Hour of Publication (0-23)', fontsize=10)
            ax.set_ylabel('Average Engagement', fontsize=10)
            ax.set_title('Engagement by Publication Hour', fontsize=11, fontweight='bold')
            ax.grid(alpha=0.3)
            ax.set_xticks(range(0, 24, 2))
            st.pyplot(fig)
        
        with col_trend4:
            # Title length vs engagement
            youtube_df_sorted = youtube_df.sort_values('title_length')
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(youtube_df_sorted['title_length'], youtube_df_sorted['predicted_engagement'],
                      alpha=0.6, c='#28A745', s=50, edgecolors='darkgreen', linewidth=0.5)
            ax.set_xlabel('Title Length (Characters)', fontsize=10)
            ax.set_ylabel('Predicted Engagement', fontsize=10)
            ax.set_title('Engagement Trend by Title Length', fontsize=11, fontweight='bold')
            ax.grid(alpha=0.3)
            st.pyplot(fig)
        
        st.divider()
        
        # ===== SECTION 4: DETAILED DATA TABLE =====
        st.subheader("📋 Detailed YouTube Data")
        
        # Pagination for large dataset
        rows_per_page = st.select_slider("Rows per page", options=[10, 25, 50, 100], value=50)
        total_pages = (len(youtube_df) + rows_per_page - 1) // rows_per_page
        current_page = st.slider("Page", 1, total_pages, 1)
        
        start_idx = (current_page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        
        display_cols = ['title', 'channel_title', 'views', 'likes', 'comments', 'predicted_engagement']
        display_cols = [col for col in display_cols if col in youtube_df.columns]
        
        st.dataframe(
            youtube_df[display_cols].iloc[start_idx:end_idx].reset_index(drop=True),
            use_container_width=True,
            height=400
        )
        
        st.caption(f"Showing rows {start_idx + 1}-{min(end_idx, len(youtube_df))} of {len(youtube_df)}")

# ===== TAB 3: INSTAGRAM ANALYSIS =====
with tab3:
    if instagram_df is None:
        st.error("❌ No Instagram data available. Run the pipeline first.")
    else:
        st.header("📸 Instagram Engagement Analysis")
        
        # Display summary stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Posts", len(instagram_df), f"Δ {len(instagram_df)} from pipeline")
        col2.metric("Avg Predicted Engagement", f"{instagram_df['predicted_engagement'].mean():.4f}")
        col3.metric("Max Predicted Engagement", f"{instagram_df['predicted_engagement'].max():.4f}")
        col4.metric("Min Predicted Engagement", f"{instagram_df['predicted_engagement'].min():.4f}")
        
        st.divider()
        
        # ===== SECTION 1: ENGAGEMENT DISTRIBUTION =====
        st.subheader("📈 Engagement Distribution Analysis")
        
        col_chart1, col_chart2, col_chart3 = st.columns(3)
        
        with col_chart1:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.hist(instagram_df['predicted_engagement'], bins=40, color='#E1306C', alpha=0.7, edgecolor='black')
            ax.set_xlabel('Predicted Engagement Score', fontsize=10)
            ax.set_ylabel('Number of Posts', fontsize=10)
            ax.set_title('Distribution of Engagement', fontsize=11, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)
        
        with col_chart2:
            if 'impressions' in instagram_df.columns:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.scatter(instagram_df['impressions'], instagram_df['predicted_engagement'], 
                          alpha=0.6, c='#E1306C', s=50, edgecolors='darkred', linewidth=0.5)
                ax.set_xlabel('Impressions', fontsize=10)
                ax.set_ylabel('Predicted Engagement', fontsize=10)
                ax.set_title('Impressions vs Engagement', fontsize=11, fontweight='bold')
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        with col_chart3:
            if 'likes' in instagram_df.columns:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.scatter(instagram_df['likes'], instagram_df['predicted_engagement'], 
                          alpha=0.6, c='#00A4EF', s=50, edgecolors='darkblue', linewidth=0.5)
                ax.set_xlabel('Likes', fontsize=10)
                ax.set_ylabel('Predicted Engagement', fontsize=10)
                ax.set_title('Likes vs Engagement', fontsize=11, fontweight='bold')
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        st.divider()
        
        # ===== SECTION 2: CONTENT CATEGORY ANALYSIS =====
        st.subheader("🎯 Content Category Analysis - User Interaction Preferences")
        
        if 'content_category' in instagram_df.columns:
            # Content category statistics
            category_stats = instagram_df.groupby('content_category').agg({
                'predicted_engagement': ['count', 'mean', 'max'],
                'impressions': 'mean',
                'likes': 'mean',
                'comments': 'mean'
            }).round(4)
            
            category_stats.columns = ['Post_Count', 'Avg_Engagement', 'Max_Engagement', 'Avg_Impressions', 'Avg_Likes', 'Avg_Comments']
            category_stats = category_stats.sort_values('Avg_Engagement', ascending=False)
            
            # Display category table
            st.write("**Content Category Performance Metrics:**")
            st.dataframe(category_stats.head(15), use_container_width=True)
            
            # Category charts
            col_cat1, col_cat2 = st.columns(2)
            
            with col_cat1:
                fig, ax = plt.subplots(figsize=(12, 6))
                top_categories = category_stats.head(10)
                bars = ax.barh(range(len(top_categories)), top_categories['Avg_Engagement'], color='#E1306C', alpha=0.7, edgecolor='black')
                ax.set_yticks(range(len(top_categories)))
                ax.set_yticklabels(top_categories.index, fontsize=9)
                ax.set_xlabel('Average Engagement Score', fontsize=10)
                ax.set_title('Top 10 Content Categories by Engagement (Most Interactive Topics)', fontsize=11, fontweight='bold')
                ax.invert_yaxis()
                
                # Add value labels
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax.text(width, bar.get_y() + bar.get_height()/2, f'{width:.4f}', 
                           ha='left', va='center', fontsize=8)
                
                st.pyplot(fig)
            
            with col_cat2:
                fig, ax = plt.subplots(figsize=(12, 6))
                post_counts = category_stats['Post_Count'].sort_values(ascending=False).head(10)
                bars = ax.barh(range(len(post_counts)), post_counts, color='#F77737', alpha=0.7, edgecolor='black')
                ax.set_yticks(range(len(post_counts)))
                ax.set_yticklabels(post_counts.index, fontsize=9)
                ax.set_xlabel('Number of Posts', fontsize=10)
                ax.set_title('Top 10 Content Categories by Post Count', fontsize=11, fontweight='bold')
                ax.invert_yaxis()
                
                # Add value labels
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax.text(width, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                           ha='left', va='center', fontsize=8)
                
                st.pyplot(fig)
        
        elif 'account_type' in instagram_df.columns:
            # Account type analysis as fallback
            account_stats = instagram_df.groupby('account_type').agg({
                'predicted_engagement': ['count', 'mean', 'max'],
                'impressions': 'mean',
                'likes': 'mean',
                'comments': 'mean'
            }).round(4)
            
            account_stats.columns = ['Post_Count', 'Avg_Engagement', 'Max_Engagement', 'Avg_Impressions', 'Avg_Likes', 'Avg_Comments']
            account_stats = account_stats.sort_values('Avg_Engagement', ascending=False)
            
            st.write("**Account Type Performance Metrics:**")
            st.dataframe(account_stats, use_container_width=True)
        
        st.divider()
        
        # ===== SECTION 3: ENGAGEMENT TREND ANALYSIS =====
        st.subheader("📊 Engagement Trend Analysis")
        
        col_trend1, col_trend2 = st.columns(2)
        
        with col_trend1:
            # Engagement by like ratio
            if 'like_ratio' in instagram_df.columns:
                instagram_df_sorted = instagram_df.sort_values('like_ratio')
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.scatter(instagram_df_sorted['like_ratio'], instagram_df_sorted['predicted_engagement'],
                          alpha=0.6, c='#E1306C', s=50, edgecolors='darkred', linewidth=0.5)
                ax.set_xlabel('Like Ratio (Likes/Impressions)', fontsize=10)
                ax.set_ylabel('Predicted Engagement', fontsize=10)
                ax.set_title('Engagement Trend by Like Ratio', fontsize=11, fontweight='bold')
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        with col_trend2:
            # Engagement by comment ratio
            if 'comment_ratio' in instagram_df.columns:
                instagram_df_sorted = instagram_df.sort_values('comment_ratio')
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.scatter(instagram_df_sorted['comment_ratio'], instagram_df_sorted['predicted_engagement'],
                          alpha=0.6, c='#00A4EF', s=50, edgecolors='darkblue', linewidth=0.5)
                ax.set_xlabel('Comment Ratio (Comments/Impressions)', fontsize=10)
                ax.set_ylabel('Predicted Engagement', fontsize=10)
                ax.set_title('Engagement Trend by Comment Ratio', fontsize=11, fontweight='bold')
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        col_trend3, col_trend4 = st.columns(2)
        
        with col_trend3:
            # Engagement by reach ratio
            if 'reach_ratio' in instagram_df.columns:
                instagram_df_sorted = instagram_df.sort_values('reach_ratio')
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.scatter(instagram_df_sorted['reach_ratio'], instagram_df_sorted['predicted_engagement'],
                          alpha=0.6, c='#28A745', s=50, edgecolors='darkgreen', linewidth=0.5)
                ax.set_xlabel('Reach Ratio', fontsize=10)
                ax.set_ylabel('Predicted Engagement', fontsize=10)
                ax.set_title('Engagement Trend by Reach Ratio', fontsize=11, fontweight='bold')
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        with col_trend4:
            # Engagement by follower count
            if 'follower_count' in instagram_df.columns:
                instagram_df_sorted = instagram_df.sort_values('follower_count')
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.scatter(instagram_df_sorted['follower_count'], instagram_df_sorted['predicted_engagement'],
                          alpha=0.6, c='#F77737', s=50, edgecolors='darkorange', linewidth=0.5)
                ax.set_xlabel('Follower Count', fontsize=10)
                ax.set_ylabel('Predicted Engagement', fontsize=10)
                ax.set_title('Engagement Trend by Follower Count', fontsize=11, fontweight='bold')
                ax.grid(alpha=0.3)
                st.pyplot(fig)
        
        st.divider()
        
        # ===== SECTION 4: ACCOUNT TYPE & MEDIA TYPE ANALYSIS =====
        st.subheader("📱 Account Type & Media Type Analysis")
        
        ana_col1, ana_col2 = st.columns(2)
        
        with ana_col1:
            if 'account_type' in instagram_df.columns:
                fig, ax = plt.subplots(figsize=(10, 5))
                account_engagement = instagram_df.groupby('account_type')['predicted_engagement'].mean().sort_values(ascending=False)
                bars = ax.bar(range(len(account_engagement)), account_engagement.values, color='#E1306C', alpha=0.7, edgecolor='black')
                ax.set_xticks(range(len(account_engagement)))
                ax.set_xticklabels(account_engagement.index, rotation=45, ha='right')
                ax.set_ylabel('Average Engagement', fontsize=10)
                ax.set_title('Average Engagement by Account Type', fontsize=11, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                
                # Add value labels
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, height, f'{height:.4f}', 
                           ha='center', va='bottom', fontsize=9)
                
                st.pyplot(fig)
        
        with ana_col2:
            if 'media_type' in instagram_df.columns:
                fig, ax = plt.subplots(figsize=(10, 5))
                media_engagement = instagram_df.groupby('media_type')['predicted_engagement'].mean().sort_values(ascending=False)
                bars = ax.bar(range(len(media_engagement)), media_engagement.values, color='#00A4EF', alpha=0.7, edgecolor='black')
                ax.set_xticks(range(len(media_engagement)))
                ax.set_xticklabels(media_engagement.index, rotation=45, ha='right')
                ax.set_ylabel('Average Engagement', fontsize=10)
                ax.set_title('Average Engagement by Media Type', fontsize=11, fontweight='bold')
                ax.grid(axis='y', alpha=0.3)
                
                # Add value labels
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, height, f'{height:.4f}', 
                           ha='center', va='bottom', fontsize=9)
                
                st.pyplot(fig)
        
        st.divider()
        
        # ===== SECTION 5: DETAILED DATA TABLE =====
        st.subheader("📋 Detailed Instagram Data")
        
        # Pagination
        rows_per_page = st.select_slider("Rows per page", options=[10, 25, 50, 100], value=50, key="ig_rows")
        total_pages = (len(instagram_df) + rows_per_page - 1) // rows_per_page
        current_page = st.slider("Page", 1, total_pages, 1, key="ig_page")
        
        start_idx = (current_page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        
        display_cols = ['post_id', 'account_type', 'media_type', 'likes', 'comments', 'impressions', 'predicted_engagement']
        display_cols = [col for col in display_cols if col in instagram_df.columns]
        
        st.dataframe(
            instagram_df[display_cols].iloc[start_idx:end_idx].reset_index(drop=True),
            use_container_width=True,
            height=400
        )
        
        st.caption(f"Showing rows {start_idx + 1}-{min(end_idx, len(instagram_df))} of {len(instagram_df)}")

# ===== TAB 4: MODEL PERFORMANCE =====
with tab4:
    st.header("🎯 Model Performance Analytics")
    
    if model is None:
        st.warning("⚠️ Model file not found. Run the pipeline to train the model.")
    else:
        st.markdown("""
        **Model Details:**
        - Algorithm: Random Forest Regressor
        - Estimators: 100 trees
        - Objective: Predict engagement score from content features
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Model Features")
            features = ["like_ratio", "comment_ratio", "publish_hour", "title_length"]
            st.write("This model uses the following features to predict engagement:")
            for i, feat in enumerate(features, 1):
                st.write(f"{i}. **{feat}** - Extracted from content metadata")
        
        with col2:
            st.subheader("🔍 Feature Importance")
            if hasattr(model, 'feature_importances_'):
                feature_importance = pd.DataFrame({
                    'Feature': features,
                    'Importance': model.feature_importances_
                }).sort_values('Importance', ascending=False)
                
                fig, ax = plt.subplots(figsize=(8, 5))
                bars = ax.barh(feature_importance['Feature'], feature_importance['Importance'], color='#1f77b4')
                ax.set_xlabel('Importance Score', fontsize=11)
                ax.set_title('Feature Importance in Engagement Prediction', fontsize=12, fontweight='bold')
                
                # Add value labels
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax.text(width, bar.get_y() + bar.get_height()/2, f'{width:.4f}', 
                           ha='left', va='center', fontsize=10)
                
                st.pyplot(fig)
        
        st.divider()
        
        st.subheader("📈 Model Training Information")
        st.info("""
        **Training Process:**
        1. Feature engineering from raw content data (views, likes, comments, publish time, title length)
        2. Data normalization and preprocessing
        3. Train/Test split: 80/20
        4. Random Forest model training with 100 estimators
        5. Model evaluation on test set
        
        **Features:**
        - **like_ratio**: Calculated as likes / views
        - **comment_ratio**: Calculated as comments / views  
        - **publish_hour**: Hour of publication (0-23)
        - **title_length**: Number of characters in content title
        """)

# ===== TAB 5: CROSS-PLATFORM COMPARISON =====
with tab5:
    st.header("🔄 Cross-Platform Comparison")
    
    if youtube_df is None or instagram_df is None:
        st.error("⚠️ Need both YouTube and Instagram data for comparison.")
    else:
        st.subheader("📊 Platform Comparison Metrics")
        
        # Comparison table
        comparison_data = {
            'Metric': [
                'Total Items',
                'Avg Engagement Score',
                'Max Engagement Score',
                'Min Engagement Score',
                'Std Dev',
                'Median Engagement'
            ],
            'YouTube': [
                len(youtube_df),
                f"{youtube_df['predicted_engagement'].mean():.4f}",
                f"{youtube_df['predicted_engagement'].max():.4f}",
                f"{youtube_df['predicted_engagement'].min():.4f}",
                f"{youtube_df['predicted_engagement'].std():.4f}",
                f"{youtube_df['predicted_engagement'].median():.4f}"
            ],
            'Instagram': [
                len(instagram_df),
                f"{instagram_df['predicted_engagement'].mean():.4f}",
                f"{instagram_df['predicted_engagement'].max():.4f}",
                f"{instagram_df['predicted_engagement'].min():.4f}",
                f"{instagram_df['predicted_engagement'].std():.4f}",
                f"{instagram_df['predicted_engagement'].median():.4f}"
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        st.divider()
        
        # Visual comparison
        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Box plot comparison
            data_to_plot = [youtube_df['predicted_engagement'], instagram_df['predicted_engagement']]
            bp = ax.boxplot(data_to_plot, labels=['YouTube', 'Instagram'], patch_artist=True)
            
            colors = ['#FF0000', '#E1306C']
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            ax.set_ylabel('Predicted Engagement Score', fontsize=11)
            ax.set_title('Engagement Distribution Comparison', fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)
        
        with col_comp2:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Distribution overlay
            ax.hist(youtube_df['predicted_engagement'], bins=30, alpha=0.6, label='YouTube', color='#FF0000', edgecolor='black')
            ax.hist(instagram_df['predicted_engagement'], bins=30, alpha=0.6, label='Instagram', color='#E1306C', edgecolor='black')
            ax.set_xlabel('Predicted Engagement Score', fontsize=11)
            ax.set_ylabel('Frequency', fontsize=11)
            ax.set_title('Engagement Distribution Overlay', fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)
        
        st.divider()
        
        # Insights
        st.subheader("💡 Comparison Insights")
        
        yt_avg = youtube_df['predicted_engagement'].mean()
        ig_avg = instagram_df['predicted_engagement'].mean()
        
        insights_comp = []
        
        if yt_avg > ig_avg:
            pct_diff = ((yt_avg - ig_avg) / ig_avg * 100)
            insights_comp.append(f"📹 YouTube has **{pct_diff:.1f}% higher** average engagement than Instagram")
        else:
            pct_diff = ((ig_avg - yt_avg) / yt_avg * 100)
            insights_comp.append(f"📸 Instagram has **{pct_diff:.1f}% higher** average engagement than YouTube")
        
        yt_std = youtube_df['predicted_engagement'].std()
        ig_std = instagram_df['predicted_engagement'].std()
        
        if yt_std > ig_std:
            insights_comp.append(f"📊 YouTube engagement is **more variable** (Std: {yt_std:.4f} vs {ig_std:.4f})")
        else:
            insights_comp.append(f"📊 Instagram engagement is **more variable** (Std: {ig_std:.4f} vs {yt_std:.4f})")
        
        insights_comp.append(f"📌 YouTube dataset size: {len(youtube_df)} videos")
        insights_comp.append(f"📌 Instagram dataset size: {len(instagram_df)} posts")
        
        for idx, insight in enumerate(insights_comp, 1):
            st.markdown(f"<div class='insight-box'>{idx}. {insight}</div>", unsafe_allow_html=True)

# ===== FOOTER =====
st.divider()
st.markdown("""
---
**📊 Content Engagement Prediction Dashboard**  
*Báo cáo: Dự báo mức độ tương tác nội dung số từ bộ dữ liệu instagram/youtube engagement*

**Report Generated:** {}  
**Data Sources:** YouTube API + Kaggle Instagram Analytics + Kaggle YouTube Dataset  
**Technology Stack:** Python, Streamlit, Pandas, Scikit-learn
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
